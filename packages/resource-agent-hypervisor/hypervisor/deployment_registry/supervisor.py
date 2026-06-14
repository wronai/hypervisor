from __future__ import annotations

import time
from pathlib import Path
from typing import Any
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

import httpx

from hypervisor.deployment_registry.lifecycle import (
    agent_logs_uri,
    command_port_from_runtime,
    resolve_effective_health_uri,
    restart_agent,
    run_agent,
)
from hypervisor.deployment_registry.run_plans import build_run_plan
from hypervisor.deployment_registry.runtime_state import (
    is_process_alive,
    load_runtime_state,
    runtime_status,
)


def _state_pid(state: dict[str, Any]) -> int | None:
    process = state.get("process") or {}
    if isinstance(process, dict) and process.get("pid") is not None:
        return process.get("pid")
    return state.get("pid")


def _state_command(state: dict[str, Any]) -> str:
    process = state.get("process") or {}
    if isinstance(process, dict) and process.get("command"):
        return str(process["command"])
    return str(state.get("command") or "")


def _state_health_uri(state: dict[str, Any]) -> str:
    network = state.get("network") or {}
    if isinstance(network, dict) and network.get("effective_health_uri"):
        return str(network["effective_health_uri"])
    return str(state.get("health_uri") or "")


def _runtime_command_port(state: dict[str, Any], plan: dict[str, Any]) -> int | None:
    runtime_command = _state_command(state)
    if runtime_command:
        return command_port_from_runtime({"command": runtime_command}, plan)
    return None
from hypervisor.deployment_registry.selector import resolve_deployment
from hypervisor.paths import find_repo_root


def _lifecycle_payload(payload: dict[str, Any]) -> dict[str, Any]:
    from uri3.results.envelope import enrich_lifecycle_dict

    return enrich_lifecycle_dict(payload)


def _repo_root(root: str | Path) -> Path:
    return Path(root) if str(root) != "." else find_repo_root()


def _port_from_http_uri(uri: str | None) -> int | None:
    if not uri:
        return None
    parsed = urlsplit(uri)
    if parsed.port is not None:
        return parsed.port
    if parsed.scheme == "http":
        return 80
    if parsed.scheme == "https":
        return 443
    return None


def _probe_http(uri: str | None, *, timeout: float) -> dict[str, Any]:
    if not uri or not uri.startswith(("http://", "https://")):
        return {"uri": uri, "ok": False, "skipped": True, "reason": "missing http uri"}
    try:
        response = httpx.get(uri, timeout=timeout)
        content_type = response.headers.get("content-type", "")
        payload = response.json() if "json" in content_type else None
        json_ok = payload.get("ok") if isinstance(payload, dict) else None
        agent_name = payload.get("agent") if isinstance(payload, dict) else None
        ok = response.is_success and (json_ok is not False)
        return {
            "uri": uri,
            "ok": ok,
            "status_code": response.status_code,
            "json_ok": json_ok,
            "agent": agent_name,
            "payload": payload if isinstance(payload, dict) else None,
        }
    except Exception as exc:
        return {"uri": uri, "ok": False, "error": str(exc)}


def _log_uri_with_filters(log_uri: str, *, limit: int, level: str = "ERROR") -> str:
    parsed = urlsplit(log_uri)
    query = dict(parse_qsl(parsed.query, keep_blank_values=True))
    query.setdefault("level", level)
    query["limit"] = str(limit)
    return urlunsplit(
        (parsed.scheme, parsed.netloc, parsed.path, urlencode(query), parsed.fragment)
    )


def _read_error_logs(log_uri: str, *, root: Path, limit: int) -> dict[str, Any]:
    filtered = _log_uri_with_filters(log_uri, limit=limit)
    try:
        from uri3.logs.reader import read_logs_result, summarize_logs

        summary = summarize_logs(filtered, root=root)
        entries = read_logs_result(filtered, root=root)
        if isinstance(entries, dict):
            log_entries = entries.get("entries") or []
            hint = entries.get("hint")
        else:
            log_entries = entries
            hint = ""
        return {
            "uri": filtered,
            "summary": summary,
            "entries": log_entries[-limit:],
            "hint": hint,
            "error_count": len(log_entries),
        }
    except Exception as exc:
        return {"uri": filtered, "summary": {}, "entries": [], "error": str(exc), "error_count": 0}


def _readiness_summary(
    *,
    process_alive: bool,
    health: dict[str, Any],
    card: dict[str, Any],
    logs: dict[str, Any],
    effective_health_uri: str,
    declared_health_uri: str | None,
) -> dict[str, Any]:
    effective_port = _port_from_http_uri(effective_health_uri)
    return {
        "process": "running" if process_alive else "stopped",
        "health": "ok" if health.get("ok") else "failed",
        "card": "ok" if card.get("ok") else ("skipped" if not card.get("uri") else "failed"),
        "log_errors": logs.get("error_count", 0),
        "effective_port": effective_port,
        "declared_health_uri": declared_health_uri,
        "effective_health_uri": effective_health_uri,
    }


def inspect_agent(
    selector: str,
    *,
    root: str | Path = ".",
    timeout: float = 2.0,
    log_limit: int = 20,
) -> dict[str, Any]:
    """Inspect process, health, card and recent error logs for one deployment."""
    repo = _repo_root(root)
    deployment = resolve_deployment(selector, root=repo)
    state = load_runtime_state(deployment.id, repo) or {}
    run_plan: dict[str, Any] | None = None
    try:
        run_plan = build_run_plan(deployment, root=repo)
    except (FileNotFoundError, ValueError):
        run_plan = None

    pid = _state_pid(state)
    process_alive = is_process_alive(pid if isinstance(pid, int) else None)
    runtime = runtime_status(deployment.id, repo)
    plan_dict = run_plan or {}
    stored_health_uri = str(
        _state_health_uri(state) or plan_dict.get("health_uri") or deployment.health_uri or ""
    )
    effective_health_uri = resolve_effective_health_uri(state, plan_dict)
    effective_port = _port_from_http_uri(effective_health_uri)
    effective_card_uri = state.get("card_uri") or plan_dict.get("card_uri") or deployment.card_uri
    if effective_port:
        effective_card_uri = f"http://localhost:{effective_port}/.well-known/agent-card.json"
    log_uri = str(state.get("log_uri") or agent_logs_uri(deployment.id, root=repo))
    health = _probe_http(effective_health_uri or None, timeout=timeout)
    card = _probe_http(str(effective_card_uri) if effective_card_uri else None, timeout=timeout)
    logs = _read_error_logs(log_uri, root=repo, limit=log_limit)
    incidents = _classify_incidents(
        runtime=runtime,
        process_alive=process_alive,
        deployment_health_uri=deployment.health_uri,
        stored_health_uri=stored_health_uri,
        effective_health_uri=effective_health_uri,
        state=state,
        plan=plan_dict,
        health=health,
        card=card,
        logs=logs,
    )
    readiness = _readiness_summary(
        process_alive=process_alive,
        health=health,
        card=card,
        logs=logs,
        effective_health_uri=effective_health_uri,
        declared_health_uri=deployment.health_uri,
    )
    blocking = _blocking_incidents(incidents)
    service_status = (
        "healthy" if health.get("ok") and process_alive and not blocking else "degraded"
    )
    if runtime in {"stopped", "stale"} and not process_alive:
        service_status = "stopped"
    elif not health.get("ok") and process_alive:
        service_status = "unhealthy"

    payload = {
        "ok": service_status == "healthy",
        "id": deployment.id,
        "agent_ref": deployment.agent_ref,
        "target_uri": deployment.target_uri,
        "service_status": service_status,
        "runtime_status": runtime,
        "process": {
            "pid": pid,
            "running": process_alive,
        },
        "readiness": readiness,
        "health": health,
        "card": card,
        "log_uri": log_uri,
        "log_errors": logs,
        "declared_health_uri": deployment.health_uri,
        "stored_health_uri": stored_health_uri or None,
        "effective_health_uri": effective_health_uri,
        "incidents": blocking,
        "warnings": [
            item for item in incidents if item.get("code") not in _BLOCKING_INCIDENT_CODES
        ],
        "runtime_state": state or None,
    }
    if run_plan is not None:
        payload["run_plan"] = {
            "port": run_plan.get("port"),
            "health_uri": run_plan.get("health_uri"),
            "card_uri": run_plan.get("card_uri"),
            "command": run_plan.get("command_string"),
        }
    return _lifecycle_payload(payload)


def _classify_incidents(
    *,
    runtime: str,
    process_alive: bool,
    deployment_health_uri: str | None,
    stored_health_uri: str,
    effective_health_uri: str,
    state: dict[str, Any],
    plan: dict[str, Any],
    health: dict[str, Any],
    card: dict[str, Any],
    logs: dict[str, Any],
) -> list[dict[str, Any]]:
    incidents: list[dict[str, Any]] = []
    command_port = _runtime_command_port(state, plan)
    stored_port = _port_from_http_uri(stored_health_uri)
    effective_port = _port_from_http_uri(effective_health_uri)
    if runtime == "stale":
        incidents.append(
            {"code": "RUNTIME_STATE_STALE", "detail": "runtime state points to a dead process"}
        )
    if runtime == "running" and not process_alive:
        incidents.append(
            {
                "code": "PROCESS_NOT_ALIVE",
                "detail": "runtime status is running but pid is not alive",
            }
        )
    if command_port is not None and stored_port is not None and command_port != stored_port:
        incidents.append(
            {
                "code": "COMMAND_HEALTH_MISMATCH",
                "detail": "uvicorn command port differs from stored health_uri",
                "command_port": command_port,
                "stored_health_uri": stored_health_uri,
                "severity": "error",
            }
        )
    if (
        deployment_health_uri
        and effective_health_uri
        and deployment_health_uri != effective_health_uri
    ):
        incidents.append(
            {
                "code": "HEALTH_URI_DRIFT",
                "detail": "effective health URI differs from deployment registry health URI",
                "declared": deployment_health_uri,
                "effective": effective_health_uri,
                "severity": "warning",
            }
        )
    if process_alive and not health.get("ok"):
        incidents.append(
            {
                "code": "PROCESS_RUNNING_BUT_UNHEALTHY",
                "detail": "process is alive but HTTP health probe failed",
                "uri": health.get("uri"),
                "effective_port": effective_port,
            }
        )
    elif not health.get("ok"):
        incidents.append(
            {
                "code": "HEALTH_FAILED",
                "detail": health.get("error") or f"health returned {health.get('status_code')}",
                "uri": health.get("uri"),
            }
        )
    if card.get("uri") and not card.get("ok"):
        incidents.append(
            {
                "code": "CARD_FAILED",
                "detail": card.get("error") or f"card returned {card.get('status_code')}",
                "uri": card.get("uri"),
            }
        )
    if logs.get("error_count", 0) > 0:
        incidents.append(
            {
                "code": "RECENT_LOG_ERRORS",
                "detail": f"{logs['error_count']} recent error log entries matched",
                "uri": logs.get("uri"),
            }
        )
    return incidents


_BLOCKING_INCIDENT_CODES = frozenset(
    {
        "HEALTH_FAILED",
        "PROCESS_RUNNING_BUT_UNHEALTHY",
        "RUNTIME_STATE_STALE",
        "PROCESS_NOT_ALIVE",
        "COMMAND_HEALTH_MISMATCH",
        "CARD_FAILED",
    }
)


def _blocking_incidents(incidents: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [item for item in incidents if item.get("code") in _BLOCKING_INCIDENT_CODES]


def _auto_repair_plan(inspection: dict[str, Any]) -> tuple[str, dict[str, Any]]:
    codes = {item["code"] for item in inspection.get("incidents") or []}
    warning_codes = {item["code"] for item in inspection.get("warnings") or []}
    all_codes = codes | warning_codes
    state = inspection.get("runtime_state") or {}
    plan = inspection.get("run_plan") or {}
    port = _runtime_command_port(state, plan) or command_port_from_runtime(state, plan) or plan.get("port")

    if all_codes & {"RUNTIME_STATE_STALE", "PROCESS_NOT_ALIVE"}:
        return "restart", {"port": port} if port else {}
    if "COMMAND_HEALTH_MISMATCH" in all_codes:
        return "sync_health", {}
    if "PROCESS_RUNNING_BUT_UNHEALTHY" in all_codes and port:
        return "restart", {"port": port}
    if "HEALTH_FAILED" in all_codes:
        return "restart", {"port": port} if port else {}
    if "HEALTH_URI_DRIFT" in all_codes:
        return "sync_health", {}
    return "restart", {"port": port} if port else {}


def _apply_repair(
    selector: str,
    *,
    root: Path,
    strategy: str,
    params: dict[str, Any],
    detach: bool = True,
) -> dict[str, Any]:
    port = params.get("port")
    if strategy == "sync_health":
        return run_agent(selector, root=root, detach=detach, if_running="reuse", port=port)
    if strategy == "reuse":
        return run_agent(selector, root=root, detach=detach, if_running="reuse", port=port)
    if strategy == "restart":
        return restart_agent(selector, root=root, detach=detach, port=port)
    raise ValueError(f"unsupported repair strategy: {strategy}")


def ensure_agent_healthy(
    selector: str,
    *,
    root: str | Path = ".",
    port: int | None = None,
    repair: str = "auto",
    timeout: float = 2.0,
    log_limit: int = 20,
    max_attempts: int = 3,
    settle_seconds: float = 0.5,
) -> dict[str, Any]:
    """Run bounded inspect → repair → re-probe loop until healthy or attempts exhausted."""
    repo = _repo_root(root)
    before = inspect_agent(selector, root=repo, timeout=timeout, log_limit=log_limit)
    if before.get("ok"):
        return _lifecycle_payload(
            {
                "ok": True,
                "id": before["id"],
                "status": "healthy",
                "repair": repair,
                "attempts": 0,
                "actions": [],
                "before": before,
                "after": before,
            }
        )

    actions: list[dict[str, Any]] = []
    current = before
    attempts = 0
    while attempts < max_attempts and not current.get("ok"):
        if repair == "auto":
            strategy, params = _auto_repair_plan(current)
        elif repair in {"restart", "reuse", "sync_health"}:
            strategy, params = repair, {"port": port} if port is not None else {}
        else:
            raise ValueError("repair must be one of: auto, restart, reuse, sync_health")

        if port is not None:
            params = {**params, "port": port}
        action = _apply_repair(selector, root=repo, strategy=strategy, params=params)
        actions.append({"strategy": strategy, "params": params, "result": action})
        time.sleep(settle_seconds)
        current = inspect_agent(selector, root=repo, timeout=timeout, log_limit=log_limit)
        attempts += 1

    return _lifecycle_payload(
        {
            "ok": bool(current.get("ok")),
            "id": current["id"],
            "status": "healthy" if current.get("ok") else "degraded",
            "repair": repair,
            "attempts": attempts,
            "actions": actions,
            "before": before,
            "after": current,
        }
    )


def supervise_agent(
    selector: str,
    *,
    root: str | Path = ".",
    repair: str = "none",
    timeout: float = 2.0,
    log_limit: int = 20,
    settle_seconds: float = 0.5,
    max_attempts: int = 3,
) -> dict[str, Any]:
    """Inspect an agent and optionally run a bounded repair loop."""
    if repair not in {"none", "restart", "reuse", "sync_health", "auto"}:
        raise ValueError("repair must be one of: none, restart, reuse, sync_health, auto")

    if repair == "none":
        before = inspect_agent(selector, root=root, timeout=timeout, log_limit=log_limit)
        if before.get("ok"):
            return _lifecycle_payload(
                {
                    "ok": True,
                    "id": before["id"],
                    "status": "healthy",
                    "actions": [],
                    "before": before,
                    "after": before,
                }
            )
        return _lifecycle_payload(
            {
                "ok": False,
                "id": before["id"],
                "status": "blocked",
                "reason": ("service is not healthy; run with --repair auto or --repair restart"),
                "actions": [],
                "before": before,
                "after": before,
            }
        )

    return ensure_agent_healthy(
        selector,
        root=root,
        repair=repair,
        timeout=timeout,
        log_limit=log_limit,
        max_attempts=max_attempts,
        settle_seconds=settle_seconds,
    )

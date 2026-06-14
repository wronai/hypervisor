from __future__ import annotations

from pathlib import Path
from typing import Any

from hypervisor.deployment_registry.env import default_log_uri, resolve_deployment_env
from hypervisor.deployment_registry.health_uri import port_from_command, port_from_http_uri
from hypervisor.deployment_registry.process import start_process
from hypervisor.deployment_registry.process_discovery import (
    command_matches_plan,
    pids_listening_on_port,
    terminate_pid,
)
from hypervisor.deployment_registry.run_executor import (
    attach_started_process,
    build_agent_run_plan,
    load_or_clear_runtime_state,
    prepare_runtime_env,
    process_start_failure_payload,
    rebind_plan_port_if_busy,
    resolve_running_mode,
    reuse_existing_process_plan,
    sync_runtime_health_uri,
    verify_process_alive,
    write_runtime_state_after_start,
)
from hypervisor.deployment_registry.run_plans import build_run_plan
from hypervisor.deployment_registry.runtime_state import (
    clear_runtime_state,
    is_process_alive,
    load_runtime_state,
    now_iso,
    runtime_status,
    save_runtime_state,
)
from hypervisor.deployment_registry.selector import resolve_deployment
from hypervisor.deployment_registry.status import resolve_status
from hypervisor.paths import find_repo_root


def _lifecycle_payload(payload: dict[str, Any]) -> dict[str, Any]:
    from uri3.results.envelope import enrich_lifecycle_dict

    return enrich_lifecycle_dict(payload)


def _repo_root(root: str | Path) -> Path:
    return Path(root) if str(root) != "." else find_repo_root()


def _safe_stop_plan(deployment, *, repo: Path) -> dict[str, Any]:
    try:
        return build_agent_run_plan(deployment, repo=repo, port=None, host="0.0.0.0", reload=False)
    except (FileNotFoundError, ValueError):
        return {}


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


def _candidate_stop_ports(state: dict[str, Any], plan: dict[str, Any]) -> set[int]:
    ports: set[int] = set()
    command_port = port_from_command(_state_command(state))
    if command_port is not None:
        ports.add(command_port)
    health_port = port_from_http_uri(_state_health_uri(state))
    if health_port is not None:
        ports.add(health_port)
    plan_port = plan.get("port")
    if isinstance(plan_port, int):
        ports.add(plan_port)
    return ports


def _terminate_matching_agent_processes(
    state: dict[str, Any],
    plan: dict[str, Any],
    *,
    timeout: float,
) -> dict[str, Any]:
    pids: set[int] = set()
    skipped: list[dict[str, Any]] = []
    state_pid = _state_pid(state)
    if isinstance(state_pid, int) and is_process_alive(state_pid):
        if not plan or command_matches_plan(state_pid, plan):
            pids.add(state_pid)
        else:
            skipped.append({"pid": state_pid, "reason": "runtime_pid_command_mismatch"})

    for port in _candidate_stop_ports(state, plan):
        for pid in pids_listening_on_port(port):
            if not plan or command_matches_plan(pid, plan):
                pids.add(pid)
            else:
                skipped.append({"pid": pid, "port": port, "reason": "listener_command_mismatch"})

    terminated: list[int] = []
    failed: list[int] = []
    for pid in sorted(pids):
        if terminate_pid(pid, timeout=timeout):
            terminated.append(pid)
        else:
            failed.append(pid)
    return {"terminated_pids": terminated, "failed_pids": failed, "skipped": skipped}


def run_agent(
    selector: str,
    *,
    root: str | Path = ".",
    port: int | None = None,
    host: str = "0.0.0.0",
    reload: bool = False,
    dry_run: bool = False,
    detach: bool = False,
    if_running: str | None = None,
    wait_healthy: bool = False,
    supervise_repair: str = "auto",
) -> dict[str, Any]:
    if if_running not in {None, "reuse", "restart", "fail"}:
        raise ValueError("--if-running must be one of: reuse, restart, fail")
    if wait_healthy and supervise_repair not in {"auto", "restart", "reuse", "sync_health"}:
        raise ValueError("--supervise-repair must be one of: auto, restart, reuse, sync_health")
    repo = _repo_root(root)
    deployment = resolve_deployment(selector, root=repo)

    def _finalize(plan_dict: dict[str, Any]) -> dict[str, Any]:
        payload = _lifecycle_payload(plan_dict)
        if wait_healthy and detach and not dry_run:
            from hypervisor.deployment_registry.supervisor import ensure_agent_healthy

            supervision = ensure_agent_healthy(
                selector,
                root=repo,
                port=port,
                repair=supervise_repair,
            )
            payload["supervision"] = supervision
            payload["service_healthy"] = supervision.get("ok")
            if not supervision.get("ok"):
                payload["ok"] = False
                payload["service_result_status"] = "failed"
        return payload

    existing = load_or_clear_runtime_state(deployment.id, repo)
    if existing and not is_process_alive(existing.get("pid")):
        stop_agent(selector, root=repo)
        clear_runtime_state(deployment.id, repo)
        existing = None
    plan = build_agent_run_plan(deployment, repo=repo, port=port, host=host, reload=reload)
    if existing and is_process_alive(existing.get("pid")):
        running_mode = resolve_running_mode(
            if_running=if_running,
            detach=detach,
            port=port,
            existing=existing,
            plan=plan,
            deployment_id=deployment.id,
        )
        if running_mode == "restart":
            stop_agent(selector, root=repo)
            clear_runtime_state(deployment.id, repo)
            existing = None
        elif running_mode == "reuse":
            plan = reuse_existing_process_plan(existing, plan, port=port)
            if plan["health_uri"] != existing.get("health_uri"):
                save_runtime_state(
                    deployment.id,
                    sync_runtime_health_uri(existing, plan["health_uri"]),
                    repo,
                )
            return _finalize(plan)
        elif running_mode == "fail":
            raise RuntimeError(
                f"Agent {deployment.id} already running with pid {existing['pid']}. "
                "Use hypervisor stop-agent first or --if-running reuse|restart."
            )
        else:
            raise ValueError("--if-running must be one of: reuse, restart, fail")
    plan = rebind_plan_port_if_busy(deployment, plan, repo=repo, host=host, reload=reload)
    if dry_run:
        return _lifecycle_payload(plan)
    if deployment.target_uri.startswith("ssh://"):
        raise ValueError(
            "SSH targets support dry-run plans only. "
            "Use hypervisor deploy-agent and verify-agent, then start the agent on the remote host."
        )
    if deployment.target_uri.startswith("docker://"):
        from hypervisor.deployment_registry.docker_runner import apply_docker_deploy

        return apply_docker_deploy(deployment, root=repo)
    runtime_env = prepare_runtime_env(deployment, repo=repo)
    process = start_process(plan, root=repo, detach=detach, runtime_env=runtime_env)
    if detach and process is not None:
        if not verify_process_alive(process.pid):
            return _lifecycle_payload(
                process_start_failure_payload(deployment.id, process_pid=process.pid, plan=plan)
            )
        write_runtime_state_after_start(
            deployment,
            plan,
            process_pid=process.pid,
            runtime_env=runtime_env,
            host=host,
            requested_port=port,
            repo=repo,
        )
        plan = attach_started_process(plan, process.pid)
    return _finalize(plan)


def stop_agent(
    selector: str,
    *,
    root: str | Path = ".",
    timeout: float = 5.0,
) -> dict[str, Any]:
    repo = _repo_root(root)
    deployment = resolve_deployment(selector, root=repo)
    if deployment.target_uri.startswith("docker://"):
        from hypervisor.deployment_registry.docker_runner import stop_docker_deployment

        return stop_docker_deployment(deployment, root=repo)
    plan = _safe_stop_plan(deployment, repo=repo)
    state = load_runtime_state(deployment.id, repo)
    if not state:
        stopped_without_state = _terminate_matching_agent_processes({}, plan, timeout=timeout)
        if stopped_without_state["terminated_pids"]:
            return _lifecycle_payload(
                {
                    "id": deployment.id,
                    "status": "stopped",
                    "message": "Matching agent process discovered without runtime state; stopped",
                    **stopped_without_state,
                }
            )
        return _lifecycle_payload(
            {"id": deployment.id, "status": "stopped", "message": "No runtime state found"}
        )
    pid = _state_pid(state)
    stop_result = _terminate_matching_agent_processes(state, plan, timeout=timeout)
    if stop_result["failed_pids"]:
        return _lifecycle_payload(
            {
                "ok": False,
                "id": deployment.id,
                "status": "failed",
                "message": "Failed to stop one or more matching agent processes",
                **stop_result,
            }
        )
    if stop_result["terminated_pids"]:
        reported_pid = pid
        if reported_pid not in stop_result["terminated_pids"]:
            reported_pid = stop_result["terminated_pids"][0]
        stopped = {
            "id": deployment.id,
            "pid": reported_pid,
            "status": "stopped",
            "stopped_at": now_iso(),
            **stop_result,
        }
        save_runtime_state(deployment.id, stopped, repo)
        return _lifecycle_payload(stopped)
    if not is_process_alive(pid):
        clear_runtime_state(deployment.id, repo)
        return _lifecycle_payload(
            {
                "id": deployment.id,
                "status": "stopped",
                "message": "Process not alive; state cleared",
                **stop_result,
            }
        )
    return _lifecycle_payload(
        {
            "ok": False,
            "id": deployment.id,
            "status": "failed",
            "message": (
                "Runtime PID is alive but does not match the deployment command; not stopped"
            ),
            **stop_result,
        }
    )


def restart_agent(
    selector: str,
    *,
    root: str | Path = ".",
    port: int | None = None,
    host: str = "0.0.0.0",
    reload: bool = False,
    detach: bool = True,
) -> dict[str, Any]:
    repo = _repo_root(root)
    deployment = resolve_deployment(selector, root=repo)
    stop_agent(selector, root=repo)
    clear_runtime_state(deployment.id, repo)
    return run_agent(
        selector,
        root=repo,
        port=port,
        host=host,
        reload=reload,
        detach=detach,
        if_running="fail",
    )


def agent_status(
    selector: str,
    *,
    root: str | Path = ".",
    check_health: bool = True,
) -> dict[str, Any]:
    repo = _repo_root(root)
    deployment = resolve_deployment(selector, root=repo)
    status = resolve_status(deployment, check_health=check_health)
    runtime = runtime_status(deployment.id, repo)
    payload = {
        "id": deployment.id,
        "agent_ref": deployment.agent_ref,
        "target_uri": deployment.target_uri,
        "status": status,
        "runtime_status": runtime,
        "health_uri": deployment.health_uri,
        "card_uri": deployment.card_uri,
        "env": resolve_deployment_env(
            deployment.id, deployment.agent_ref, deployment.env, root=repo, resolve_secrets=False
        ),
    }
    state = load_runtime_state(deployment.id, repo)
    if state:
        payload["runtime_state"] = state
    if deployment.target_uri.startswith("local://") or deployment.target_uri.startswith("ssh://"):
        try:
            payload["run_plan"] = build_run_plan(deployment, root=repo)
        except (ValueError, FileNotFoundError):
            payload["run_plan"] = None
    return _lifecycle_payload(payload)


def agent_logs_uri(selector: str, *, root: str | Path = ".") -> str:
    repo = _repo_root(root)
    deployment = resolve_deployment(selector, root=root)
    state = load_runtime_state(deployment.id, repo)
    if state and state.get("log_uri"):
        return str(state["log_uri"])
    return default_log_uri(deployment.id, deployment.agent_ref, root=repo)

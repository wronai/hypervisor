from __future__ import annotations

import os
import re
import signal
import time
from pathlib import Path
from typing import Any

from hypervisor.deployment_registry.env import default_log_uri, resolve_deployment_env
from hypervisor.deployment_registry.process import start_process
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


def _port_from_http_uri(uri: str | None) -> int | None:
    if not uri:
        return None
    from urllib.parse import urlparse

    parsed = urlparse(uri)
    if parsed.port is not None:
        return parsed.port
    if parsed.scheme == "http":
        return 80
    if parsed.scheme == "https":
        return 443
    return None


def _port_from_command(command: str | None) -> int | None:
    if not command:
        return None
    match = re.search(r"--port(?:=|\s+)(\d+)", command)
    return int(match.group(1)) if match else None


def _health_uri_for_port(port: int) -> str:
    return f"http://localhost:{port}/health"


def _resolve_health_uri(state: dict[str, Any], plan: dict[str, Any]) -> str:
    command = str(state.get("command") or plan.get("command_string") or "")
    command_port = _port_from_command(command)
    if command_port is not None:
        return _health_uri_for_port(command_port)
    return str(state.get("health_uri") or plan.get("health_uri") or "")


def resolve_effective_health_uri(state: dict[str, Any], plan: dict[str, Any]) -> str:
    return _resolve_health_uri(state, plan)


def command_port_from_runtime(state: dict[str, Any], plan: dict[str, Any]) -> int | None:
    command = str(state.get("command") or plan.get("command_string") or "")
    return _port_from_command(command)


def _lifecycle_payload(payload: dict[str, Any]) -> dict[str, Any]:
    from uri3.results.envelope import enrich_lifecycle_dict

    return enrich_lifecycle_dict(payload)


def _repo_root(root: str | Path) -> Path:
    return Path(root) if str(root) != "." else find_repo_root()


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

    existing = load_runtime_state(deployment.id, repo)
    if existing and not is_process_alive(existing.get("pid")):
        clear_runtime_state(deployment.id, repo)
        existing = None
    plan = build_run_plan(deployment, root=repo, port=port, host=host, reload=reload)
    if existing and is_process_alive(existing.get("pid")):
        running_mode = if_running or ("reuse" if detach else "fail")
        existing_port = _port_from_http_uri(str(existing.get("health_uri") or ""))
        requested_port = plan.get("port")
        if (
            port is not None
            and existing_port is not None
            and requested_port is not None
            and existing_port != requested_port
        ):
            if running_mode == "reuse":
                running_mode = "restart"
            elif running_mode == "fail":
                raise RuntimeError(
                    f"Agent {deployment.id} already running on port {existing_port}, "
                    f"requested port {requested_port}. Use --if-running restart."
                )
        if running_mode == "restart":
            stop_agent(selector, root=repo)
        elif running_mode == "reuse":
            plan["pid"] = existing.get("pid")
            plan["health_uri"] = (
                plan.get("health_uri")
                if port is not None
                else resolve_effective_health_uri(existing, plan)
            )
            if plan["health_uri"] != existing.get("health_uri"):
                save_runtime_state(
                    deployment.id,
                    {**existing, "health_uri": plan["health_uri"]},
                    repo,
                )
            plan["runtime_status"] = "running"
            plan["already_running"] = True
            return _finalize(plan)
        elif running_mode == "fail":
            raise RuntimeError(
                f"Agent {deployment.id} already running with pid {existing['pid']}. "
                "Use hypervisor stop-agent first or --if-running reuse|restart."
            )
        else:
            raise ValueError("--if-running must be one of: reuse, restart, fail")
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
    runtime_env = resolve_deployment_env(
        deployment.id, deployment.agent_ref, deployment.env, root=repo, resolve_secrets=True
    )
    process = start_process(plan, root=repo, detach=detach, runtime_env=runtime_env)
    if detach and process is not None:
        effective_port = plan.get("port")
        declared_health = deployment.health_uri or plan.get("health_uri")
        state = {
            "id": deployment.id,
            "agent_ref": deployment.agent_ref,
            "pid": process.pid,
            "status": "running",
            "health_status": "unknown",
            "lifecycle_status": "running",
            "started_at": now_iso(),
            "command": plan["command_string"],
            "health_uri": plan["health_uri"],
            "log_uri": plan["log_uri"],
            "env": runtime_env,
            "requested_port": port,
            "declared_health_uri": declared_health,
            "network": {
                "host": host,
                "requested_port": port,
                "effective_port": effective_port,
                "effective_health_uri": plan["health_uri"],
                "declared_health_uri": declared_health,
            },
        }
        save_runtime_state(deployment.id, state, repo)
        plan["pid"] = process.pid
        plan["runtime_status"] = "running"
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
    state = load_runtime_state(deployment.id, repo)
    if not state:
        return _lifecycle_payload(
            {"id": deployment.id, "status": "stopped", "message": "No runtime state found"}
        )
    pid = state.get("pid")
    if not is_process_alive(pid):
        clear_runtime_state(deployment.id, repo)
        return _lifecycle_payload(
            {
                "id": deployment.id,
                "status": "stopped",
                "message": "Process not alive; state cleared",
            }
        )
    os.kill(pid, signal.SIGTERM)
    deadline = time.time() + timeout
    while time.time() < deadline and is_process_alive(pid):
        time.sleep(0.1)
    if is_process_alive(pid):
        os.kill(pid, signal.SIGKILL)
    stopped = {
        "id": deployment.id,
        "pid": pid,
        "status": "stopped",
        "stopped_at": now_iso(),
    }
    save_runtime_state(deployment.id, stopped, repo)
    return _lifecycle_payload(stopped)


def restart_agent(
    selector: str,
    *,
    root: str | Path = ".",
    port: int | None = None,
    host: str = "0.0.0.0",
    reload: bool = False,
    detach: bool = True,
) -> dict[str, Any]:
    stop_agent(selector, root=root)
    return run_agent(selector, root=root, port=port, host=host, reload=reload, detach=detach)


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

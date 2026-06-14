from __future__ import annotations

import os
import signal
import subprocess
import sys
import time
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from hypervisor.deployment_registry.env import default_log_uri, resolve_deployment_env
from hypervisor.deployment_registry.loader import load_deployment_registry
from hypervisor.deployment_registry.models import AgentDeployment
from hypervisor.deployment_registry.runtime_state import (
    clear_runtime_state,
    is_process_alive,
    load_runtime_state,
    now_iso,
    runtime_status,
    save_runtime_state,
)
from hypervisor.deployment_registry.status import infer_port, resolve_status
from hypervisor.deployment_registry.remote_runner import build_ssh_run_plan
from hypervisor.paths import find_repo_root


def local_target_to_relative_path(target_uri: str) -> Path:
    parsed = urlparse(target_uri)
    if parsed.scheme != "local":
        raise ValueError(f"Only local:// targets can be started directly: {target_uri}")
    if parsed.netloc:
        return Path(f"{parsed.netloc}/{parsed.path.lstrip('/')}")
    return Path(parsed.path.lstrip("/"))


def local_target_to_module(target_uri: str) -> str:
    relative = local_target_to_relative_path(target_uri)
    parts = relative.parts
    if len(parts) >= 3 and parts[0] == "agents" and parts[1] == "generated":
        package = parts[2]
        return f"agents.generated.{package}.main:app"
    raise ValueError(f"Unsupported local agent path: {target_uri}")


def resolve_deployment(
    selector: str,
    *,
    root: str | Path = ".",
) -> AgentDeployment:
    registry = load_deployment_registry(root)
    deployment = registry.by_id(selector)
    if deployment is None:
        matches = registry.by_agent_ref(selector if selector.startswith("agent://") else f"agent://{selector}")
        if len(matches) == 1:
            deployment = matches[0]
        elif len(matches) > 1:
            ids = ", ".join(item.id for item in matches)
            raise ValueError(f"Ambiguous agent selector {selector!r}; choose deployment id: {ids}")
    if deployment is None:
        raise ValueError(f"Deployment not found: {selector}")
    return deployment


def build_run_plan(
    deployment: AgentDeployment,
    *,
    root: str | Path | None = None,
    port: int | None = None,
    host: str = "0.0.0.0",
    reload: bool = False,
) -> dict[str, Any]:
    repo = Path(root) if root is not None else find_repo_root()
    parsed = urlparse(deployment.target_uri)
    chosen_port = port or infer_port(deployment)

    if parsed.scheme == "local":
        module = local_target_to_module(deployment.target_uri)
        agent_path = repo / local_target_to_relative_path(deployment.target_uri)
        if not agent_path.exists():
            raise FileNotFoundError(f"Generated agent path not found: {agent_path}")
        command = [
            sys.executable,
            "-m",
            "uvicorn",
            module,
            "--host",
            host,
            "--port",
            str(chosen_port),
        ]
        if reload:
            command.append("--reload")
        health_uri = deployment.health_uri or f"http://localhost:{chosen_port}/health"
        display_env = resolve_deployment_env(
            deployment.id, deployment.agent_ref, deployment.env, root=repo, resolve_secrets=False
        )
        return {
            "deployment_id": deployment.id,
            "agent_ref": deployment.agent_ref,
            "target_uri": deployment.target_uri,
            "module": module,
            "path": str(agent_path),
            "host": host,
            "port": chosen_port,
            "health_uri": health_uri,
            "card_uri": deployment.card_uri or f"http://localhost:{chosen_port}/.well-known/agent-card.json",
            "command": command,
            "command_string": " ".join(command),
            "env": display_env,
            "log_uri": default_log_uri(deployment.id, deployment.agent_ref, root=repo),
            "runtime_state_path": str((repo / "output" / "runtime" / "agents" / deployment.id / "state.json")),
        }

    if parsed.scheme == "ssh":
        return build_ssh_run_plan(deployment, root=repo, port=chosen_port, host=host)

    if parsed.scheme == "docker":
        from hypervisor.deployment_registry.docker_runner import build_docker_control_plan

        return build_docker_control_plan(deployment, "up", root=repo)

    raise ValueError(f"Unsupported deployment target scheme: {parsed.scheme}")


def _start_process(
    plan: dict[str, Any],
    *,
    root: Path,
    detach: bool,
    runtime_env: dict[str, str] | None = None,
) -> subprocess.Popen[Any] | None:
    env = os.environ.copy()
    env.update(runtime_env or plan.get("env") or {})
    cwd = str(root)
    command = plan["command"]
    if detach:
        return subprocess.Popen(
            command,
            cwd=cwd,
            env=env,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
        )
    subprocess.run(command, check=True, cwd=cwd, env=env)
    return None


def run_agent(
    selector: str,
    *,
    root: str | Path = ".",
    port: int | None = None,
    host: str = "0.0.0.0",
    reload: bool = False,
    dry_run: bool = False,
    detach: bool = False,
) -> dict[str, Any]:
    repo = Path(root) if str(root) != "." else find_repo_root()
    deployment = resolve_deployment(selector, root=repo)
    existing = load_runtime_state(deployment.id, repo)
    if existing and is_process_alive(existing.get("pid")):
        raise RuntimeError(
            f"Agent {deployment.id} already running with pid {existing['pid']}. "
            "Use hypervisor stop-agent first."
        )
    plan = build_run_plan(deployment, root=repo, port=port, host=host, reload=reload)
    if dry_run:
        return plan
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
    process = _start_process(plan, root=repo, detach=detach, runtime_env=runtime_env)
    if detach and process is not None:
        state = {
            "id": deployment.id,
            "agent_ref": deployment.agent_ref,
            "pid": process.pid,
            "status": "running",
            "started_at": now_iso(),
            "command": plan["command_string"],
            "health_uri": plan["health_uri"],
            "log_uri": plan["log_uri"],
            "env": runtime_env,
        }
        save_runtime_state(deployment.id, state, repo)
        plan["pid"] = process.pid
        plan["runtime_status"] = "running"
    return plan


def stop_agent(
    selector: str,
    *,
    root: str | Path = ".",
    timeout: float = 5.0,
) -> dict[str, Any]:
    repo = Path(root) if str(root) != "." else find_repo_root()
    deployment = resolve_deployment(selector, root=repo)
    if deployment.target_uri.startswith("docker://"):
        from hypervisor.deployment_registry.docker_runner import stop_docker_deployment

        return stop_docker_deployment(deployment, root=repo)
    state = load_runtime_state(deployment.id, repo)
    if not state:
        return {"id": deployment.id, "status": "stopped", "message": "No runtime state found"}
    pid = state.get("pid")
    if not is_process_alive(pid):
        clear_runtime_state(deployment.id, repo)
        return {"id": deployment.id, "status": "stopped", "message": "Process not alive; state cleared"}
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
    return stopped


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
    repo = Path(root) if str(root) != "." else find_repo_root()
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
        "env": resolve_deployment_env(deployment.id, deployment.agent_ref, deployment.env, root=repo, resolve_secrets=False),
    }
    state = load_runtime_state(deployment.id, repo)
    if state:
        payload["runtime_state"] = state
    if deployment.target_uri.startswith("local://") or deployment.target_uri.startswith("ssh://"):
        try:
            payload["run_plan"] = build_run_plan(deployment, root=repo)
        except (ValueError, FileNotFoundError):
            payload["run_plan"] = None
    return payload


def agent_logs_uri(selector: str, *, root: str | Path = ".") -> str:
    deployment = resolve_deployment(selector, root=root)
    state = load_runtime_state(deployment.id, root if str(root) != "." else find_repo_root())
    if state and state.get("log_uri"):
        return str(state["log_uri"])
    return default_log_uri(deployment.id, deployment.agent_ref, root=root if str(root) != "." else find_repo_root())

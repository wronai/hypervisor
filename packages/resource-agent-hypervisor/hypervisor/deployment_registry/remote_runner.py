from __future__ import annotations

import shlex
import sys
from pathlib import Path
from typing import Any

from hypervisor.deployment_registry.env import resolve_deployment_env
from hypervisor.deployment_registry.models import AgentDeployment
from hypervisor.deployment_registry.status import infer_port
from hypervisor.paths import find_repo_root
from uri3.resolvers.ssh_resolver import parse_ssh_uri, ssh_transport_option
from uri3.scanner.http_scanner import health_scan_ok, scan_http
from uri3.scanner.ssh_scanner import scan_ssh


def generated_agent_dir(agent_ref: str, root: Path) -> Path:
    package = agent_ref.removeprefix("agent://").replace("-", "_")
    return root / "agents" / "generated" / package


def remote_module_for(deployment: AgentDeployment) -> str:
    return str(deployment.metadata.get("remote_module") or "main:app")


def build_ssh_deploy_plan(
    deployment: AgentDeployment,
    *,
    root: Path | None = None,
) -> dict[str, Any]:
    repo = root or find_repo_root()
    ssh_ref = parse_ssh_uri(deployment.target_uri)
    source = generated_agent_dir(deployment.agent_ref, repo)
    if not source.exists():
        raise FileNotFoundError(f"Generated agent source not found: {source}")
    remote_path = ssh_ref["path"]
    transport = ssh_transport_option(ssh_ref)
    rsync_cmd = [
        "rsync",
        "-avz",
        "--delete",
        "-e",
        transport,
        f"{source}/",
        f"{ssh_ref['target']}:{remote_path}/",
    ]
    post_deploy_checks = [
        f"test -d {shlex.quote(remote_path)}",
        f"test -f {shlex.quote(remote_path)}/main.py",
    ]
    return {
        "deployment_id": deployment.id,
        "agent_ref": deployment.agent_ref,
        "target_uri": deployment.target_uri,
        "ssh": ssh_ref,
        "local_source": str(source),
        "remote_path": remote_path,
        "steps": [
            {
                "action": "rsync",
                "description": "Sync generated agent package to remote host",
                "command": rsync_cmd,
                "command_string": " ".join(rsync_cmd),
            },
            {
                "action": "verify_remote_path",
                "description": "Verify remote agent directory exists",
                "remote_commands": post_deploy_checks,
            },
        ],
        "hint": "Use hypervisor deploy-agent --apply to run rsync (requires SSH auth).",
    }


def build_ssh_run_plan(
    deployment: AgentDeployment,
    *,
    root: Path | None = None,
    port: int | None = None,
    host: str = "0.0.0.0",
) -> dict[str, Any]:
    repo = root or find_repo_root()
    ssh_ref = parse_ssh_uri(deployment.target_uri)
    chosen_port = port or infer_port(deployment)
    remote_path = ssh_ref["path"]
    module = remote_module_for(deployment)
    display_env = resolve_deployment_env(
        deployment.id, deployment.agent_ref, deployment.env, root=repo, resolve_secrets=False
    )
    env_prefix = " ".join(f"{key}={shlex.quote(value)}" for key, value in display_env.items())
    remote_command = (
        f"cd {shlex.quote(remote_path)} && "
        f"{env_prefix + ' ' if env_prefix else ''}"
        f"{shlex.quote(sys.executable)} -m uvicorn {module} "
        f"--host {shlex.quote(host)} --port {chosen_port}"
    )
    from uri3.resolvers.ssh_resolver import build_ssh_command

    command = build_ssh_command(ssh_ref, remote_command)
    health_uri = deployment.health_uri or f"http://{ssh_ref['host']}:{chosen_port}/health"
    return {
        "deployment_id": deployment.id,
        "agent_ref": deployment.agent_ref,
        "target_uri": deployment.target_uri,
        "transport": "ssh",
        "ssh": ssh_ref,
        "remote_path": remote_path,
        "module": module,
        "host": host,
        "port": chosen_port,
        "health_uri": health_uri,
        "card_uri": deployment.card_uri or f"http://{ssh_ref['host']}:{chosen_port}/.well-known/agent-card.json",
        "remote_command": remote_command,
        "command": command,
        "command_string": " ".join(command),
        "env": display_env,
        "hint": "Remote start is dry-run only in v0.6; deploy first, then run manually or via future remote detach.",
    }


def verify_remote_deployment(
    deployment: AgentDeployment,
    *,
    root: Path | None = None,
    check_health: bool = True,
) -> dict[str, Any]:
    ssh_ref = parse_ssh_uri(deployment.target_uri)
    ssh_items = scan_ssh(deployment.target_uri)
    payload: dict[str, Any] = {
        "id": deployment.id,
        "agent_ref": deployment.agent_ref,
        "target_uri": deployment.target_uri,
        "ssh_scan": [item.__dict__ for item in ssh_items],
        "ssh_ok": any(item.kind == "ssh_connectivity" and item.status == "reachable" for item in ssh_items),
        "remote_path_ok": any(item.kind == "remote_path" and item.status == "present" for item in ssh_items),
    }
    if check_health and deployment.health_uri:
        http_items = scan_http(deployment.health_uri)
        payload["health_scan"] = [item.__dict__ for item in http_items]
        payload["health_ok"] = health_scan_ok(http_items)
    else:
        payload["health_scan"] = []
        payload["health_ok"] = None
    payload["verified"] = payload["ssh_ok"] and payload["remote_path_ok"] and (
        payload["health_ok"] is None or payload["health_ok"]
    )
    payload["ssh_host"] = ssh_ref["host"]
    return payload


def apply_ssh_deploy_plan(plan: dict[str, Any]) -> dict[str, Any]:
    import subprocess

    from uri3.resolvers.ssh_resolver import build_ssh_command, parse_ssh_uri

    results: list[dict[str, Any]] = []
    ssh_ref = plan["ssh"]
    for step in plan["steps"]:
        if step["action"] == "rsync":
            completed = subprocess.run(step["command"], capture_output=True, text=True, check=False)
            results.append(
                {
                    "action": "rsync",
                    "returncode": completed.returncode,
                    "stdout": completed.stdout,
                    "stderr": completed.stderr,
                }
            )
            if completed.returncode != 0:
                return {"ok": False, "steps": results}
        elif step["action"] == "verify_remote_path":
            ref = parse_ssh_uri(plan["target_uri"])
            for remote_cmd in step["remote_commands"]:
                completed = subprocess.run(build_ssh_command(ref, remote_cmd), capture_output=True, text=True)
                results.append(
                    {
                        "action": "verify_remote_path",
                        "command": remote_cmd,
                        "returncode": completed.returncode,
                        "stdout": completed.stdout,
                        "stderr": completed.stderr,
                    }
                )
                if completed.returncode != 0:
                    return {"ok": False, "steps": results}
    return {"ok": True, "steps": results}

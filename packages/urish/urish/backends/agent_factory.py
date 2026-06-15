from __future__ import annotations

import re
import socket
import sys
from contextlib import suppress
from pathlib import Path
from typing import Any

import yaml
from uri3.paths import find_repo_root

_AGENT_NAME_RE = re.compile(
    r"\b(?:agent|agenta)\s+([a-zA-Z][\w.-]*-agent|[a-zA-Z][\w.-]*)\b",
    re.I,
)
_DEVICE_URI_RE = re.compile(r"\bdevice://[^\s,;`\"']+", re.I)
_ROBOT_URI_RE = re.compile(r"\brobot://[^\s,;`\"']+", re.I)
_SSH_URI_RE = re.compile(r"ssh://[^\s,;`\"']+", re.I)


def _slug(value: str, *, fallback: str = "generated-agent") -> str:
    text = re.sub(r"[^a-zA-Z0-9.-]+", "-", value.strip().lower()).strip(".-")
    text = re.sub(r"-+", "-", text)
    return text or fallback


def infer_agent_name(prompt: str, explicit: str | None = None) -> str:
    raw = explicit or ""
    if not raw:
        match = _AGENT_NAME_RE.search(prompt)
        raw = match.group(1) if match else "generated-agent"
    name = _slug(raw.removesuffix(".local"))
    return name if name.endswith("-agent") else f"{name}-agent"


def _python_package(agent_name: str) -> str:
    return agent_name.replace("-", "_").replace(".", "_")


def _first_uri(pattern: re.Pattern[str], prompt: str, fallback: str | None = None) -> str | None:
    match = pattern.search(prompt)
    return match.group(0).rstrip(".") if match else fallback


def _capabilities(prompt: str, *, readme_uri: str) -> list[dict[str, Any]]:
    lower = prompt.lower()
    capabilities: list[dict[str, Any]] = []
    if "file://" in lower or "readme" in lower or "markpact" in lower:
        capabilities.append(
            {
                "name": "read_markpact_source",
                "type": "resource_read",
                "uri": readme_uri,
                "output_schema": "app.codex.v1.MarkpactSourceView",
                "renderer": "text",
                "description": "Read generated agent README/provenance through file://.",
            }
        )
    device_uri = _first_uri(
        _DEVICE_URI_RE,
        prompt,
        "device://device/sensor-1/status" if "device" in lower or "urząd" in lower else None,
    )
    if device_uri:
        capabilities.append(
            {
                "name": "read_device_status",
                "type": "resource_read",
                "uri": device_uri,
                "output_schema": "operator.device.v1.DeviceStatus",
                "renderer": "detail",
                "description": "Read device status through uri2ops.",
            }
        )
    robot_uri = _first_uri(_ROBOT_URI_RE, prompt)
    if robot_uri:
        capabilities.append(
            {
                "name": "read_robot_state",
                "type": "resource_read",
                "uri": robot_uri,
                "output_schema": "operator.robot.v1.RobotState",
                "renderer": "detail",
                "description": "Read robot state through uri2ops.",
            }
        )
    if "cron" in lower or "harmonogram" in lower or "schedule" in lower:
        capabilities.append(
            {
                "name": "run_cron_monitor",
                "type": "command",
                "uri": "cron://www/monitor/landing",
                "command": "RunCronMonitor",
                "input_schema": "app.codex.v1.RunCronMonitorCommand",
                "emits": ["CronMonitorRequested"],
                "description": "Dispatch a scheduled monitor through cron:// URI.",
            }
        )
    if not capabilities:
        capabilities.append(
            {
                "name": "read_markpact_source",
                "type": "resource_read",
                "uri": readme_uri,
                "output_schema": "app.codex.v1.MarkpactSourceView",
                "renderer": "text",
                "description": "Default generated agent provenance capability.",
            }
        )
    return capabilities


def _port_free(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as handle:
        handle.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            handle.bind(("127.0.0.1", port))
        except OSError:
            return False
    return True


def _next_agent_port(root: Path, preferred: int | None = None) -> int:
    from hypervisor.deployment_registry.loader import load_deployment_registry

    used: set[int] = set()
    for deployment in load_deployment_registry(root).deployments:
        declared = deployment.declared
        if declared and declared.preferred_port:
            used.add(int(declared.preferred_port))
    start = preferred or 8130
    for port in range(start, start + 200):
        if port not in used and _port_free(port):
            return port
    raise RuntimeError(f"no free agent port found from {start}")


def build_agent_contract(
    prompt: str,
    *,
    name: str | None = None,
    root: str | Path = ".",
) -> dict[str, Any]:
    repo = Path(root)
    agent_name = infer_agent_name(prompt, name)
    package = _python_package(agent_name)
    readme_path = repo / "agents" / "generated" / package / "README.md"
    readme_uri = f"file://{readme_path.resolve().as_posix()}"
    return {
        "agent": {
            "name": agent_name,
            "python_package": package,
            "version": "0.1.0",
            "description": f"Generated from NL prompt: {prompt}",
            "runtime_url_env": "RESOURCE_RUNTIME_URL",
            "runtime_url_default": "http://localhost:8000",
        },
        "capabilities": _capabilities(prompt, readme_uri=readme_uri),
    }


def _write_yaml(path: Path, payload: dict[str, Any]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(payload, sort_keys=False, allow_unicode=True), encoding="utf-8")
    return path


def _generate_agent_package(contract_path: Path, root: Path) -> Path:
    factory_root = root / "packages" / "resource-agent-factory"
    sys.path.insert(0, str(factory_root))
    try:
        from generator.agent_generator import generate_agent

        return generate_agent(contract_path, output_root=root / "agents" / "generated")
    finally:
        with suppress(ValueError):
            sys.path.remove(str(factory_root))


def _ssh_target_from_prompt(prompt: str, *, agent_name: str) -> str | None:
    match = _SSH_URI_RE.search(prompt)
    if match:
        return match.group(0).rstrip(".")
    lower = prompt.lower()
    if not re.search(r"\b(ssh|zdaln|remote host|remote deploy|wdro[zż]|wdroż)\b", lower):
        return None
    return f"ssh://deploy@localhost:2222/opt/agents/{agent_name}"


def _remote_deploy_next_steps(agent_name: str) -> list[str]:
    ssh_id = f"{agent_name}.ssh-dev"
    return [
        f"hypervisor deploy-agent {ssh_id} --apply",
        f"hypervisor verify-agent {ssh_id}",
        f"hypervisor run-agent {ssh_id} --detach --wait-healthy",
        (
            "curl -X POST http://localhost:8135/skills/deploy_verify_start "
            f"-H 'Content-Type: application/json' "
            f"-d '{{\"deployment_id\":\"{ssh_id}\",\"wait_healthy\":true}}'"
        ),
    ]


def _upsert_deployment(
    *,
    root: Path,
    agent_name: str,
    package: str,
    port: int,
    contract_path: Path,
) -> Path:
    from hypervisor.deployment_registry.loader import load_deployment_registry
    from hypervisor.deployment_registry.models import AgentDeployment, DeploymentDeclared
    from hypervisor.deployment_registry.writer import save_deployment_registry, upsert_deployment

    deployment_id = f"{agent_name}.local"
    target_uri = f"local://agents/generated/{package}"
    health_uri = f"http://localhost:{port}/health"
    card_uri = f"http://localhost:{port}/.well-known/agent-card.json"
    deployment = AgentDeployment(
        id=deployment_id,
        agent_ref=f"agent://{agent_name}",
        target_uri=target_uri,
        status="generated",
        declared=DeploymentDeclared(
            target_uri=target_uri,
            preferred_port=port,
            health_uri=health_uri,
            card_uri=card_uri,
        ),
        health_uri=health_uri,
        card_uri=card_uri,
        metadata={
            "source": "nl_agent_factory",
            "contract": str(contract_path.relative_to(root)),
        },
    )
    registry = load_deployment_registry(root)
    upsert_deployment(registry, deployment)
    return save_deployment_registry(registry)


def _upsert_ssh_deployment(
    *,
    root: Path,
    agent_name: str,
    ssh_target_uri: str,
    port: int,
    contract_path: Path,
) -> Path:
    from hypervisor.deployment_registry.loader import load_deployment_registry
    from hypervisor.deployment_registry.models import AgentDeployment, DeploymentDeclared
    from hypervisor.deployment_registry.writer import save_deployment_registry, upsert_deployment

    deployment_id = f"{agent_name}.ssh-dev"
    health_uri = f"http://localhost:{port}/health"
    deployment = AgentDeployment(
        id=deployment_id,
        agent_ref=f"agent://{agent_name}",
        target_uri=ssh_target_uri,
        status="planned",
        declared=DeploymentDeclared(
            target_uri=ssh_target_uri,
            preferred_port=port,
            health_uri=health_uri,
        ),
        health_uri=health_uri,
        metadata={
            "source": "nl_agent_factory",
            "contract": str(contract_path.relative_to(root)),
            "remote_module": "main:app",
        },
    )
    registry = load_deployment_registry(root)
    upsert_deployment(registry, deployment)
    return save_deployment_registry(registry)


def _upsert_deployments(
    *,
    root: Path,
    agent_name: str,
    package: str,
    port: int,
    contract_path: Path,
    prompt: str,
) -> tuple[Path, str | None]:
    registry_path = _upsert_deployment(
        root=root,
        agent_name=agent_name,
        package=package,
        port=port,
        contract_path=contract_path,
    )
    ssh_target = _ssh_target_from_prompt(prompt, agent_name=agent_name)
    if ssh_target:
        registry_path = _upsert_ssh_deployment(
            root=root,
            agent_name=agent_name,
            ssh_target_uri=ssh_target,
            port=port,
            contract_path=contract_path,
        )
    return registry_path, ssh_target


def _planned_payload(
    *,
    repo: Path,
    contract: dict[str, Any],
    agent_name: str,
    package: str,
    chosen_port: int,
    contract_path: Path,
    prompt: str,
) -> dict[str, Any]:
    deployment_id = f"{agent_name}.local"
    ssh_target = _ssh_target_from_prompt(prompt, agent_name=agent_name)
    planned: dict[str, Any] = {
        "contract_path": str(contract_path),
        "package_path": str(repo / "agents" / "generated" / package),
        "deployment_id": deployment_id,
        "agent_ref": f"agent://{agent_name}",
        "target_uri": f"local://agents/generated/{package}",
        "health_uri": f"http://localhost:{chosen_port}/health",
        "card_uri": f"http://localhost:{chosen_port}/.well-known/agent-card.json",
        "capabilities": contract["capabilities"],
    }
    if ssh_target:
        planned["ssh_deployment_id"] = f"{agent_name}.ssh-dev"
        planned["ssh_target_uri"] = ssh_target
    return planned


def _generation_next_steps(
    *,
    prompt: str,
    agent_name: str,
    deployment_id: str,
    chosen_port: int,
    approve: bool,
) -> list[str]:
    if approve:
        steps = [
            f"uri agent run {deployment_id} --wait-healthy --approve",
            f"uri call health://agent/{deployment_id}",
            f"uri call view://process/agent/{deployment_id}/latest",
        ]
    else:
        steps = [
            f"uri agent generate {prompt!r} --name {agent_name} --port {chosen_port} --approve",
            f"uri agent run {deployment_id} --wait-healthy --approve",
            f"uri call health://agent/{deployment_id}",
            f"uri call view://process/agent/{deployment_id}/latest",
        ]
    if _ssh_target_from_prompt(prompt, agent_name=agent_name):
        steps.extend(_remote_deploy_next_steps(agent_name))
    return steps


def generate_agent_from_prompt(
    prompt: str,
    *,
    name: str | None = None,
    port: int | None = None,
    dry_run: bool = True,
    approve: bool = False,
    overwrite: bool = False,
    root: str | Path | None = None,
) -> dict[str, Any]:
    repo = Path(root) if root is not None else find_repo_root(strict=False)
    contract = build_agent_contract(prompt, name=name, root=repo)
    agent_name = str(contract["agent"]["name"])
    package = str(contract["agent"]["python_package"])
    contract_path = repo / "contracts" / "agents" / f"{package}.yaml"
    chosen_port = _next_agent_port(repo, port)
    deployment_id = f"{agent_name}.local"
    planned = _planned_payload(
        repo=repo,
        contract=contract,
        agent_name=agent_name,
        package=package,
        chosen_port=chosen_port,
        contract_path=contract_path,
        prompt=prompt,
    )
    next_steps = _generation_next_steps(
        prompt=prompt,
        agent_name=agent_name,
        deployment_id=deployment_id,
        chosen_port=chosen_port,
        approve=False,
    )
    if dry_run or not approve:
        return {
            "ok": True,
            "result_type": "agent_generation_plan",
            "workflow_status": "completed",
            "execution_status": "completed",
            "service_result_status": "succeeded",
            "dry_run": True,
            "requires_approval": True,
            "contract": contract,
            "planned": planned,
            "next_steps": next_steps,
        }
    if contract_path.exists() and not overwrite:
        return {
            "ok": False,
            "result_type": "agent_generation",
            "workflow_status": "completed_with_service_error",
            "execution_status": "completed",
            "service_result_status": "failed",
            "error": f"contract already exists: {contract_path}",
            "planned": planned,
        }
    _write_yaml(contract_path, contract)
    package_path = _generate_agent_package(contract_path, repo)
    registry_path, _ssh_target = _upsert_deployments(
        root=repo,
        agent_name=agent_name,
        package=package,
        port=chosen_port,
        contract_path=contract_path,
        prompt=prompt,
    )
    return {
        "ok": True,
        "result_type": "agent_generation",
        "workflow_status": "completed",
        "execution_status": "completed",
        "service_result_status": "succeeded",
        "contract_path": str(contract_path),
        "package_path": str(package_path),
        "deployment_registry": str(registry_path),
        "deployment_id": deployment_id,
        "agent_ref": f"agent://{agent_name}",
        "health_uri": planned["health_uri"],
        "card_uri": planned["card_uri"],
        "capabilities": contract["capabilities"],
        "planned": planned,
        "next_steps": _generation_next_steps(
            prompt=prompt,
            agent_name=agent_name,
            deployment_id=deployment_id,
            chosen_port=chosen_port,
            approve=True,
        ),
    }

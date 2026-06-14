from __future__ import annotations

from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import httpx

from hypervisor.deployment_registry.loader import default_registry_path, load_deployment_registry
from hypervisor.deployment_registry.models import AgentDeployment, DeploymentRegistry
from hypervisor.deployment_registry.writer import save_deployment_registry, upsert_deployment

DEFAULT_AGENT_PORTS = {
    "weather-map-agent": 8101,
    "user-agent": 8102,
}


def deployment_id_for_agent(agent_id: str, *, suffix: str = "local") -> str:
    return f"{agent_id}.{suffix}"


def infer_health_uri(target_uri: str, agent_id: str) -> str | None:
    parsed = urlparse(target_uri)
    if parsed.scheme in {"http", "https"}:
        base = target_uri.rstrip("/")
        return f"{base}/health"
    if parsed.scheme == "local":
        port = DEFAULT_AGENT_PORTS.get(agent_id)
        if port:
            return f"http://localhost:{port}/health"
    return None


def infer_card_uri(agent: dict[str, Any], agent_id: str) -> str | None:
    card_uri = agent.get("card_uri")
    if isinstance(card_uri, str) and card_uri.startswith("http"):
        return card_uri
    port = DEFAULT_AGENT_PORTS.get(agent_id)
    if port:
        return f"http://localhost:{port}/.well-known/agent-card.json"
    return card_uri if isinstance(card_uri, str) else None


def deployment_from_uri_tree(tree: dict[str, Any]) -> AgentDeployment | None:
    deployment_block = tree.get("deployment") or {}
    default = deployment_block.get("default") if isinstance(deployment_block, dict) else None
    if not isinstance(default, dict) or not default.get("uri"):
        return None

    agent = tree.get("agent") or {}
    agent_id = str(agent.get("id") or "unknown-agent")
    agent_ref = str(agent.get("uri") or f"agent://{agent_id}")
    target_uri = str(default["uri"])

    return AgentDeployment(
        id=deployment_id_for_agent(agent_id),
        agent_ref=agent_ref,
        target_uri=target_uri,
        card_uri=infer_card_uri(agent, agent_id),
        health_uri=infer_health_uri(target_uri, agent_id),
        status="generated",
        metadata={"source": "uri_tree", "domain_id": tree.get("domain", {}).get("id")},
    )


def sync_from_uri_tree(
    tree: dict[str, Any],
    *,
    root: str | Path = ".",
    path: str | Path | None = None,
) -> AgentDeployment | None:
    deployment = deployment_from_uri_tree(tree)
    if deployment is None:
        return None
    registry = load_deployment_registry(root, path=path)
    upsert_deployment(registry, deployment)
    save_deployment_registry(registry)
    return deployment


def resolve_status(
    deployment: AgentDeployment,
    *,
    check_health: bool = False,
    timeout: float = 2.0,
) -> str:
    if not check_health:
        return deployment.status

    health_uri = deployment.health_uri
    if not health_uri or not health_uri.startswith("http"):
        return deployment.status if deployment.status in {"running", "stopped", "failed"} else "generated"

    try:
        response = httpx.get(health_uri, timeout=timeout)
        response.raise_for_status()
        payload = response.json() if "json" in response.headers.get("content-type", "") else {}
        if isinstance(payload, dict) and payload.get("ok") is True:
            return "running"
        return "deployed"
    except Exception:
        if deployment.status == "running":
            return "failed"
        return deployment.status if deployment.status != "running" else "stopped"


def list_deployments(registry: DeploymentRegistry | None = None, *, root: str | Path = ".") -> list[AgentDeployment]:
    registry = registry or load_deployment_registry(root)
    return list(registry.deployments)


def get_deployment_for_agent(
    agent_ref: str,
    *,
    registry: DeploymentRegistry | None = None,
    root: str | Path = ".",
) -> AgentDeployment | None:
    registry = registry or load_deployment_registry(root)
    matches = registry.by_agent_ref(agent_ref)
    return matches[0] if matches else None


def registry_summary(registry: DeploymentRegistry | None = None, *, root: str | Path = ".") -> list[dict[str, Any]]:
    registry = registry or load_deployment_registry(root)
    return [
        {
            "id": item.id,
            "agent_ref": item.agent_ref,
            "target_uri": item.target_uri,
            "status": item.status,
            "card_uri": item.card_uri,
            "health_uri": item.health_uri,
        }
        for item in registry.deployments
    ]

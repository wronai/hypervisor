from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from hypervisor.deployment_registry.models import AgentDeployment, DeploymentRegistry


def default_registry_path(root: str | Path = ".") -> Path:
    return Path(root) / "deployments" / "agent_deployments.yaml"


def _read_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"deployments": []}
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    return value if isinstance(value, dict) else {"deployments": []}


def _parse_deployment(item: dict[str, Any]) -> AgentDeployment:
    return AgentDeployment(
        id=str(item["id"]),
        agent_ref=str(item["agent_ref"]),
        target_uri=str(item["target_uri"]),
        card_uri=item.get("card_uri"),
        health_uri=item.get("health_uri"),
        status=str(item.get("status", "generated")),
        metadata=dict(item.get("metadata") or {}),
    )


def load_deployment_registry(
    root: str | Path = ".",
    *,
    path: str | Path | None = None,
) -> DeploymentRegistry:
    root = Path(root)
    registry_path = Path(path) if path else default_registry_path(root)
    raw = _read_yaml(registry_path)
    deployments = [_parse_deployment(item) for item in raw.get("deployments") or [] if isinstance(item, dict)]
    return DeploymentRegistry(root=root, path=registry_path, deployments=deployments, raw=raw)

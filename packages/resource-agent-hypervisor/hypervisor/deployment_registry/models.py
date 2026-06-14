from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

DEPLOYMENT_STATUSES = frozenset({"generated", "deployed", "running", "stopped", "failed", "unknown"})


@dataclass(frozen=True)
class AgentDeployment:
    id: str
    agent_ref: str
    target_uri: str
    card_uri: str | None = None
    health_uri: str | None = None
    status: str = "generated"
    env: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "id": self.id,
            "agent_ref": self.agent_ref,
            "target_uri": self.target_uri,
            "status": self.status,
        }
        if self.card_uri:
            payload["card_uri"] = self.card_uri
        if self.health_uri:
            payload["health_uri"] = self.health_uri
        if self.env:
            payload["env"] = self.env
        if self.metadata:
            payload["metadata"] = self.metadata
        return payload


@dataclass
class DeploymentRegistry:
    root: Path
    path: Path
    deployments: list[AgentDeployment]
    raw: dict[str, Any]

    def by_id(self, deployment_id: str) -> AgentDeployment | None:
        return next((item for item in self.deployments if item.id == deployment_id), None)

    def by_agent_ref(self, agent_ref: str) -> list[AgentDeployment]:
        return [item for item in self.deployments if item.agent_ref == agent_ref]

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

from uri3.routing import UriRoute


@dataclass(frozen=True)
class RoutePolicyDecision:
    allowed: bool
    requires_approval: bool = False
    reasons: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return {
            "allowed": self.allowed,
            "requires_approval": self.requires_approval,
            "reasons": list(self.reasons),
        }


@dataclass(frozen=True)
class HypervisorRouteResolution:
    route: UriRoute
    agent_uri: str | None = None
    deployment_id: str | None = None
    environment_uri: str | None = None
    contract_uri: str | None = None
    policy_uri: str | None = None
    side_effects: bool = False
    requires_approval: bool = False
    runtime: dict[str, Any] = field(default_factory=dict)
    context: dict[str, Any] = field(default_factory=dict)
    policy: RoutePolicyDecision = field(
        default_factory=lambda: RoutePolicyDecision(allowed=True)
    )

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["route"] = self.route.to_dict()
        payload["policy"] = self.policy.to_dict()
        return payload

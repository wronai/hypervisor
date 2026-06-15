from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class UriAction:
    label: str
    uri: str
    requires_approval: bool
    kind: str = "read"

    def to_dict(self) -> dict[str, Any]:
        return {
            "label": self.label,
            "uri": self.uri,
            "requires_approval": self.requires_approval,
            "kind": self.kind,
        }


@dataclass
class ProcessViewModel:
    agent_id: str
    agent_ref: str
    title: str
    service_status: str
    deployment_status: str
    process_status: str
    health_status: str
    recommended_action: str
    effective_health_uri: str | None
    effective_port: int | None
    incidents: list[dict[str, Any]] = field(default_factory=list)
    warnings: list[dict[str, Any]] = field(default_factory=list)
    readiness: dict[str, Any] = field(default_factory=dict)
    related_uris: dict[str, str] = field(default_factory=dict)
    actions: list[UriAction] = field(default_factory=list)
    inspection: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "agent_id": self.agent_id,
            "agent_ref": self.agent_ref,
            "title": self.title,
            "status": self.service_status,
            "service_status": self.service_status,
            "deployment_status": self.deployment_status,
            "process_status": self.process_status,
            "health_status": self.health_status,
            "recommended_action": self.recommended_action,
            "effective_health_uri": self.effective_health_uri,
            "effective_port": self.effective_port,
            "incidents": self.incidents,
            "warnings": self.warnings,
            "readiness": self.readiness,
            "related_uris": self.related_uris,
            "actions": [item.to_dict() for item in self.actions],
            "inspection": self.inspection,
        }


@dataclass
class ViewEnvelope:
    view_uri: str
    content_type: str
    title: str
    data: dict[str, Any]
    html: str | None = None

    def to_dict(self) -> dict[str, Any]:
        payload = {
            "result_type": "view",
            "view_uri": self.view_uri,
            "content_type": self.content_type,
            "title": self.title,
            "data": self.data,
        }
        if self.html is not None:
            payload["html"] = self.html
        return payload

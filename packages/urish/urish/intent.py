from __future__ import annotations

import re
from typing import Any

from urigen.models import wants_dashboard


DASHBOARD_PLANNED_URIS = [
    "agent://hypervisor-dashboard",
    "deployment://hypervisor-dashboard.local",
    "view://process/agent/{agent_id}/latest",
    "view://workflow/{workflow_id}/timeline",
    "view://incident/{incident_id}/explain",
    "repair://agent/{agent_id}/diagnose",
    "repair://agent/{agent_id}/apply",
    "ticket://bug/from-incident/{incident_id}",
]


def detect_intent(prompt: str) -> dict[str, Any]:
    text = prompt.strip()
    kind = _detect_kind(text)
    if kind == "ecosystem" and wants_dashboard(text, "minimal"):
        return {
            "kind": "ecosystem",
            "subtype": "dashboard-agent",
            "profile": "dashboard-agent",
            "ecosystem_id": "hypervisor-dashboard",
            "agent_id": "hypervisor-dashboard",
            "deployment_id": "hypervisor-dashboard.local",
            "dashboard_port": 8788,
        }
    if kind == "ecosystem":
        from urigen.models import slugify

        if "pogod" in text.lower() or "weather" in text.lower():
            eco_id = "weather-demo"
        else:
            eco_id = slugify(text[:64], fallback="generated-ecosystem")
        return {
            "kind": "ecosystem",
            "subtype": "generic-ecosystem",
            "profile": "minimal",
            "ecosystem_id": eco_id,
            "agent_id": None,
            "deployment_id": None,
            "dashboard_port": None,
        }
    if kind == "workflow":
        return {"kind": "workflow", "subtype": None, "profile": None}
    return {"kind": "domain", "subtype": None, "profile": None}


def _detect_kind(prompt: str) -> str:
    if re.search(r"\b(ecosystem|ekosystem)\b", prompt, re.I):
        return "ecosystem"
    if re.search(r"\b(stw[oó]rz|zbuduj|generuj)\b.*\b(agent|agenta)\b", prompt, re.I):
        return "ecosystem"
    if re.search(r"\b(agent|agenta)\b", prompt, re.I) and re.search(
        r"\b(stw[oó]rz|zbuduj|generuj|healthcheck|health)\b", prompt, re.I
    ):
        return "ecosystem"
    if re.search(r"\b(flow|workflow|graf|health|chrome|localhost|napraw|repair)\b", prompt, re.I):
        return "workflow"
    return "domain"

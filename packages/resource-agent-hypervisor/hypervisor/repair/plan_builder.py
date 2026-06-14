from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from hypervisor.repair.models import API_VERSION, REPAIR_PLAN_SCHEMA
from hypervisor.repair.policy import playbook_requires_approval, policy_level_for_playbook


def _plan_id(agent_id: str) -> str:
    stamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
    safe_id = agent_id.replace(".", "_")
    return f"rp_{safe_id}_{stamp}"


def build_repair_plan_from_diagnosis(
    diagnosis: dict[str, Any],
    *,
    incident_uri: str | None = None,
) -> dict[str, Any]:
    """Map diagnosis envelope to a RepairPlan artifact (planner only — no mutation)."""
    inspection = diagnosis.get("inspection") or {}
    classification = diagnosis.get("classification") or {}
    agent_id = str(inspection.get("id") or diagnosis.get("id") or "unknown")
    readiness = inspection.get("agent_readiness") or {}

    playbooks = list(classification.get("safe_repairs") or [])
    known_case = diagnosis.get("known_case") or {}
    if known_case.get("repair_sequence"):
        playbooks = list(known_case["repair_sequence"]) + playbooks

    if not playbooks:
        action = readiness.get("recommended_action")
        action_to_playbook = {
            "rebind_port": "rebind_port",
            "restart": "restart_agent",
            "repair": "restart_agent",
            "observe": "sync_health_uri",
        }
        playbooks = [action_to_playbook.get(action, "restart_agent")]

    playbook = playbooks[0]
    plan_id = _plan_id(agent_id)
    return {
        "$schema": REPAIR_PLAN_SCHEMA,
        "apiVersion": API_VERSION,
        "kind": "RepairPlan",
        "metadata": {
            "id": plan_id,
            "source_incident": incident_uri or f"incident://agent/{agent_id}/pending",
        },
        "uri": {"self": f"repair://agent/{agent_id}/plan/{plan_id}"},
        "spec": {
            "playbook": playbook,
            "policy_level": policy_level_for_playbook(playbook),
            "steps": playbooks[:4],
            "requires_approval": playbook_requires_approval(playbook),
        },
    }


def build_repair_plan_from_inspection(
    inspection: dict[str, Any],
    *,
    classification: dict[str, Any] | None = None,
    known_case: dict[str, Any] | None = None,
    incident_uri: str | None = None,
) -> dict[str, Any]:
    return build_repair_plan_from_diagnosis(
        {
            "id": inspection.get("id"),
            "inspection": inspection,
            "classification": classification or {},
            "known_case": known_case,
        },
        incident_uri=incident_uri,
    )

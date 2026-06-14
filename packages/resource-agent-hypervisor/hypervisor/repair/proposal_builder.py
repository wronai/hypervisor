from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from hypervisor.paths import find_repo_root


def build_repair_proposal(
    incident: dict[str, Any],
    *,
    repo_root: Path | None = None,
) -> dict[str, Any]:
    repo = repo_root or find_repo_root()
    metadata = incident.get("metadata") or {}
    incident_id = str(metadata.get("id") or "inc_unknown")
    classification = incident.get("classification") or {}
    families = classification.get("family") or ["HEALTH_TIMEOUT"]
    proposal_id = f"proposal_from_{incident_id}"
    proposals_dir = repo / "evolution" / "proposals"
    proposals_dir.mkdir(parents=True, exist_ok=True)
    proposal_path = proposals_dir / f"{proposal_id}.yaml"
    payload = {
        "$schema": "schemas/evolution_proposal.schema.json",
        "apiVersion": "uri3.io/v1",
        "kind": "EvolutionProposal",
        "proposal_id": proposal_id,
        "type": "add_repair_capability",
        "reason": (
            f"Unresolved incident {incident.get('uri', {}).get('self')} "
            f"requires new repair capability for {', '.join(families)}."
        ),
        "source_incident": incident.get("uri", {}).get("self"),
        "adds": {
            "repair_agent": {
                "name": f"repair_{'_'.join(f.lower() for f in families[:2])}_agent",
                "handles": families,
                "capabilities": [
                    {
                        "uri": "repair://agent/{agent_id}/diagnose-health",
                        "operation": "diagnose",
                    },
                    {
                        "uri": "repair://agent/{agent_id}/rebind-health-uri",
                        "operation": "patch",
                    },
                    {
                        "uri": "repair://agent/{agent_id}/restart-and-verify",
                        "operation": "repair",
                    },
                ],
            }
        },
        "checks": [
            f"uri2verify://replay/{incident_id}",
            "uri2verify://capability-plan/repair-health-agent",
        ],
        "approval": {
            "required_for": ["register_repair_capability", "modify_contracts"],
            "auto_allowed": ["read_logs", "check_process", "curl_health", "suggest_patch"],
        },
        "evolution_uri": f"evolution://proposal/from-incident/{incident_id}",
    }
    proposal_path.write_text(
        yaml.safe_dump(payload, sort_keys=False, allow_unicode=True),
        encoding="utf-8",
    )
    return {
        "ok": True,
        "proposal_id": proposal_id,
        "proposal_path": str(proposal_path),
        "proposal_uri": payload["evolution_uri"],
        "payload": payload,
    }


def link_proposal_to_incident(incident_path: Path, proposal: dict[str, Any]) -> None:
    payload = yaml.safe_load(incident_path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{incident_path} must contain YAML mapping")
    payload["evolution"] = {
        "proposal_uri": proposal.get("proposal_uri"),
        "proposal_path": proposal.get("proposal_path"),
        "allowed": False,
        "requires_approval": True,
    }
    incident_path.write_text(
        yaml.safe_dump(payload, sort_keys=False, allow_unicode=True),
        encoding="utf-8",
    )

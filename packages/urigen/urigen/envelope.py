from __future__ import annotations

from typing import Any


def stamp_proposal(payload: dict[str, Any]) -> dict[str, Any]:
    proposal = dict(payload.get("proposal") or {})
    eco_id = str(proposal.get("id") or "generated-ecosystem")
    body = dict(payload)
    body.setdefault("$schema", "packages/urigen/urigen/schemas/ecosystem_proposal.schema.json")
    body.setdefault("apiVersion", "uri3.io/v1")
    body.setdefault("kind", "EcosystemProposal")
    body.setdefault(
        "uri",
        {
            "self": f"proposal://ecosystem/{eco_id}",
            "target": f"ecosystem://{eco_id}",
        },
    )
    body.setdefault(
        "metadata",
        {
            "id": eco_id,
            "created_by": "urigen://planner",
            "source_prompt": proposal.get("source_prompt", ""),
        },
    )
    body.setdefault(
        "spec",
        {
            "profile": proposal.get("profile", "minimal"),
            "intent": body.get("intent") or {},
            "artifacts_to_generate": body.get("artifacts_to_generate") or [],
        },
    )
    return body


def stamp_ecosystem(payload: dict[str, Any], *, lifecycle: dict[str, Any] | None = None) -> dict[str, Any]:
    eco = dict(payload.get("ecosystem") or {})
    eco_id = str(eco.get("id") or "generated-ecosystem")
    body = dict(payload)
    body.setdefault("$schema", "packages/urigen/urigen/schemas/ecosystem.schema.json")
    body.setdefault("apiVersion", "uri3.io/v1")
    body.setdefault("kind", "Ecosystem")
    body.setdefault(
        "uri",
        {
            "self": f"ecosystem://{eco_id}",
            "proposal": f"proposal://ecosystem/{eco_id}",
        },
    )
    body.setdefault(
        "metadata",
        {
            "id": eco_id,
            "description": eco.get("description", ""),
            "source_prompt": eco.get("source_prompt", ""),
            "profile": eco.get("profile", "minimal"),
        },
    )
    body.setdefault(
        "spec",
        {
            "domains": body.get("domains") or [],
            "agents": body.get("agents") or [],
            "capabilities": body.get("capabilities") or [],
            "flows": body.get("flows") or [],
            "deployments": body.get("deployments") or [],
            "tests": body.get("tests") or [],
        },
    )
    default_lifecycle = {
        "generated": True,
        "verified": False,
        "explained": False,
        "applied": False,
        "active": False,
    }
    body.setdefault("status", {"lifecycle": {**default_lifecycle, **(lifecycle or {})}})
    return body

from __future__ import annotations

from copy import deepcopy
from typing import Any

_ENVELOPE_KEYS = {"$schema", "apiVersion", "kind", "metadata", "uri", "spec"}


def _legacy_fields(payload: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in payload.items() if key not in _ENVELOPE_KEYS}


def stamp_proposal(payload: dict[str, Any]) -> dict[str, Any]:
    proposal = dict(payload.get("proposal") or {})
    eco_id = str(proposal.get("id") or "generated-ecosystem")
    body = dict(payload)
    return {
        "$schema": body.get("$schema")
        or "packages/urigen/urigen/schemas/ecosystem_proposal.schema.json",
        "apiVersion": body.get("apiVersion") or "uri3.io/v1",
        "kind": body.get("kind") or "EcosystemProposal",
        "metadata": deepcopy(
            body.get("metadata")
            or {
                "id": eco_id,
                "created_by": "urigen://planner",
                "source_prompt": proposal.get("source_prompt", ""),
            }
        ),
        "uri": deepcopy(
            body.get("uri")
            or {
                "self": f"proposal://ecosystem/{eco_id}",
                "target": f"ecosystem://{eco_id}",
            }
        ),
        "spec": deepcopy(
            body.get("spec")
            or {
                "profile": proposal.get("profile", "minimal"),
                "intent": body.get("intent") or {},
                "artifacts_to_generate": body.get("artifacts_to_generate") or [],
            }
        ),
        **_legacy_fields(body),
    }


def _default_lifecycle(lifecycle: dict[str, Any] | None) -> dict[str, Any]:
    default = {
        "generated": True,
        "verified": False,
        "explained": False,
        "applied": False,
        "active": False,
    }
    return {**default, **(lifecycle or {})}


def _ecosystem_metadata(body: dict[str, Any], eco: dict[str, Any], eco_id: str) -> dict[str, Any]:
    return deepcopy(
        body.get("metadata")
        or {
            "id": eco_id,
            "description": eco.get("description", ""),
            "source_prompt": eco.get("source_prompt", ""),
            "profile": eco.get("profile", "minimal"),
        }
    )


def _ecosystem_spec(body: dict[str, Any]) -> dict[str, Any]:
    return deepcopy(
        body.get("spec")
        or {
            "domains": body.get("domains") or [],
            "agents": body.get("agents") or [],
            "capabilities": body.get("capabilities") or [],
            "flows": body.get("flows") or [],
            "deployments": body.get("deployments") or [],
            "tests": body.get("tests") or [],
        }
    )


def stamp_ecosystem(
    payload: dict[str, Any], *, lifecycle: dict[str, Any] | None = None
) -> dict[str, Any]:
    eco = dict(payload.get("ecosystem") or {})
    eco_id = str(eco.get("id") or "generated-ecosystem")
    body = dict(payload)
    return {
        "$schema": body.get("$schema") or "packages/urigen/urigen/schemas/ecosystem.schema.json",
        "apiVersion": body.get("apiVersion") or "uri3.io/v1",
        "kind": body.get("kind") or "Ecosystem",
        "metadata": _ecosystem_metadata(body, eco, eco_id),
        "uri": deepcopy(
            body.get("uri")
            or {
                "self": f"ecosystem://{eco_id}",
                "proposal": f"proposal://ecosystem/{eco_id}",
            }
        ),
        "spec": _ecosystem_spec(body),
        **_legacy_fields(body),
        "status": deepcopy(
            body.get("status") or {"lifecycle": _default_lifecycle(lifecycle)}
        ),
    }

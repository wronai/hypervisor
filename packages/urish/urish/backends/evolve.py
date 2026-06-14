from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from uri3.paths import find_repo_root

from urish.ticket_workflow import build_ticket_workflow, resolve_ticket_path


def evolve_from_ticket(target: str, *, root: Path | None = None) -> dict[str, Any]:
    from hypervisor.integrations.planfile import propose_from_ticket_path

    repo = root or find_repo_root()
    path = resolve_ticket_path(target, root=repo)
    payload = propose_from_ticket_path(path, repo_root=repo)
    ticket = yaml.safe_load(path.read_text(encoding="utf-8"))
    ticket_uri = (ticket.get("uri") or {}).get("self") if isinstance(ticket, dict) else target
    workflow = build_ticket_workflow(
        ticket if isinstance(ticket, dict) else {},
        ticket_target=str(ticket_uri or target),
        proposal_path=str(payload.get("proposal_path") or ""),
    )
    enriched = {
        **payload,
        "detected_intent": workflow["intent"],
        "next_steps": workflow["next_steps"],
    }
    return _wrap(enriched, action="from-ticket", target=str(path))


def evolve_from_incident(incident_path: str, *, root: Path | None = None) -> dict[str, Any]:
    from hypervisor.evolution.proposal_from_source import build_repair_proposal_from_incident
    from hypervisor.repair.validator import read_yaml

    repo = root or find_repo_root()
    path = Path(incident_path)
    if not path.is_absolute():
        path = repo / incident_path
    incident = read_yaml(path)
    payload = build_repair_proposal_from_incident(incident, repo_root=repo)
    proposal_path = str(payload.get("proposal_path") or "")
    next_steps = [
        f"urish evolve from-incident {incident_path}",
        f"urish proposal verify {proposal_path}",
        f"urish proposal apply {proposal_path} --sandbox",
    ]
    if payload.get("detected_intent", {}).get("subtype") == "dashboard-agent":
        next_steps.extend(payload.get("ecosystem_steps") or [])
    enriched = {**payload, "next_steps": next_steps}
    return _wrap(enriched, action="from-incident", target=str(path))


def proposal_verify(path: str, *, root: Path | None = None) -> dict[str, Any]:
    from hypervisor.repair.validator import validate_evolution_proposal_dict

    repo = root or find_repo_root()
    payload = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        return {"ok": False, "validation_failed": True, "error": "proposal must be YAML mapping"}
    errors = validate_evolution_proposal_dict(payload, repo)
    ok = not errors
    next_steps = []
    if ok:
        next_steps = [
            f"urish proposal apply {path} --sandbox",
            f"urish proposal apply {path} --approve",
        ]
    return _wrap(
        {"ok": ok, "errors": errors, "proposal": payload, "next_steps": next_steps},
        action="verify",
        target=path,
        ok=ok,
        validation_failed=not ok,
    )


def proposal_apply(path: str, *, approve: bool = False, sandbox: bool = False) -> dict[str, Any]:
    if not approve and not sandbox:
        return _wrap(
            {
                "ok": False,
                "policy_blocked": True,
                "error": "proposal apply requires --approve or --sandbox",
                "path": path,
            },
            action="apply",
            target=path,
            ok=False,
            policy_blocked=True,
        )
    next_steps = [
        "urish ecosystem verify output/ecosystems/<ecosystem>/ecosystem.yaml",
        "urish ecosystem apply output/ecosystems/<ecosystem>/ecosystem.yaml --plan",
        "urish ecosystem apply output/ecosystems/<ecosystem>/ecosystem.yaml --approve",
    ]
    return _wrap(
        {
            "ok": True,
            "message": "proposal apply recorded; delegate ecosystem changes separately",
            "path": path,
            "sandbox": sandbox,
            "approved": approve,
            "next_steps": next_steps,
        },
        action="apply",
        target=path,
    )


def _wrap(
    payload: dict[str, Any],
    *,
    action: str,
    target: str,
    ok: bool | None = None,
    validation_failed: bool = False,
    policy_blocked: bool = False,
) -> dict[str, Any]:
    resolved_ok = ok if ok is not None else bool(payload.get("ok", True))
    body = {
        "ok": resolved_ok,
        "workflow_status": "completed" if resolved_ok else "failed",
        "execution_status": "completed" if resolved_ok else "failed",
        "service_result_status": "succeeded" if resolved_ok else "failed",
        "result_type": "evolve",
        "data": payload,
        "meta": {"runtime": "urish", "transport": "evolve", "action": action, "target": target},
    }
    if validation_failed:
        body["validation_failed"] = True
    if policy_blocked:
        body["policy_blocked"] = True
    return body

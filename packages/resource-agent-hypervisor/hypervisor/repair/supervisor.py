from __future__ import annotations

import time
from pathlib import Path
from typing import Any

from hypervisor.deployment_registry.supervisor import ensure_agent_healthy, inspect_agent
from hypervisor.paths import find_repo_root
from hypervisor.repair.classifier import classify_inspection
from hypervisor.repair.incident import build_incident_from_inspection, load_incident, write_incident
from hypervisor.repair.plan_builder import build_repair_plan_from_diagnosis
from hypervisor.repair.playbooks import apply_playbook
from hypervisor.repair.policy import is_playbook_allowed, playbook_requires_approval
from hypervisor.repair.proposal_builder import build_repair_proposal, link_proposal_to_incident
from hypervisor.repair.registry import find_matching_case
from hypervisor.repair.sandbox import test_repair_plan_in_sandbox


def _envelope(payload: dict[str, Any]) -> dict[str, Any]:
    from uri3.results.envelope import enrich_lifecycle_dict

    body = dict(payload)
    body.setdefault("result_type", "repair")
    return enrich_lifecycle_dict(body)


def _repo_root(root: str | Path | None) -> Path:
    return Path(root) if root is not None else find_repo_root()


def diagnose_agent(
    selector: str,
    *,
    root: str | Path | None = None,
    timeout: float = 2.0,
    log_limit: int = 20,
) -> dict[str, Any]:
    repo = _repo_root(root)
    inspection = inspect_agent(selector, root=repo, timeout=timeout, log_limit=log_limit)
    classification = classify_inspection(inspection, log_payload=inspection.get("log_errors"))
    known_case = find_matching_case(classification, inspection, repo_root=repo)
    diagnosis_body = {
        "ok": bool(inspection.get("ok")),
        "id": inspection.get("id"),
        "result_type": "diagnosis",
        "inspection": inspection,
        "classification": classification,
        "known_case": known_case,
        "readiness": inspection.get("readiness"),
        "agent_readiness": inspection.get("agent_readiness"),
    }
    diagnosis_body["repair_plan"] = build_repair_plan_from_diagnosis(diagnosis_body)
    return _envelope(diagnosis_body)


def repair_apply(
    selector: str,
    *,
    root: str | Path | None = None,
    safe: bool = True,
    approved: bool = False,
    playbook: str | None = None,
    timeout: float = 2.0,
) -> dict[str, Any]:
    repo = _repo_root(root)
    diagnosis = diagnose_agent(selector, root=repo, timeout=timeout)
    inspection = diagnosis["inspection"]
    if inspection.get("ok"):
        return _envelope(
            {
                "ok": True,
                "status": "healthy",
                "id": selector,
                "actions": [],
                "diagnosis": diagnosis,
            }
        )

    classification = diagnosis["classification"]
    known_case = diagnosis.get("known_case")
    if playbook:
        candidates = [playbook]
    elif known_case:
        candidates = list(known_case.get("repair_sequence") or [])[:4]
    else:
        candidates = list(classification.get("safe_repairs") or [])[:3]

    actions: list[dict[str, Any]] = []
    for name in candidates:
        if safe and not is_playbook_allowed(name, max_level="level_1_safe_fix"):
            actions.append({"playbook": name, "status": "blocked", "reason": "requires approval"})
            continue
        if playbook_requires_approval(name) and not approved:
            actions.append({"playbook": name, "status": "blocked", "reason": "requires approval"})
            continue
        actions.append(apply_playbook(name, selector=selector, root=repo, approved=approved))

    time.sleep(0.5)
    after = inspect_agent(selector, root=repo, timeout=timeout)
    return _envelope(
        {
            "ok": bool(after.get("ok")),
            "status": "repaired" if after.get("ok") else "degraded",
            "id": selector,
            "actions": actions,
            "diagnosis": diagnosis,
            "after": after,
        }
    )


def supervise_with_repair(
    selector: str,
    *,
    root: str | Path | None = None,
    repair: str = "auto",
    learn: bool = True,
    timeout: float = 2.0,
    log_limit: int = 20,
    max_attempts: int = 3,
) -> dict[str, Any]:
    """Observe → diagnose → playbook → verify → incident → proposal (bounded)."""
    repo = _repo_root(root)

    healed = ensure_agent_healthy(
        selector,
        root=repo,
        repair=repair if repair != "learn" else "auto",
        timeout=timeout,
        log_limit=log_limit,
        max_attempts=max_attempts,
    )
    if healed.get("ok"):
        return _envelope(
            {
                **healed,
                "result_type": "repair",
                "phase": "healthy",
            }
        )

    after = healed.get("after") or inspect_agent(
        selector, root=repo, timeout=timeout, log_limit=log_limit
    )
    classification = classify_inspection(after, log_payload=after.get("log_errors"))
    incident = build_incident_from_inspection(
        after,
        classification=classification,
        source=f"hypervisor://agent/{selector}/supervise-with-repair",
    )
    incident.repair = {
        "attempted": healed.get("actions") or [],
        "next": {
            "operation": "repair.propose",
            "uri": f"repair://agent/{selector}/propose",
            "requires_approval": True,
        },
    }
    incident_path = write_incident(incident, repo_root=repo)

    proposal: dict[str, Any] | None = None
    escalation: dict[str, Any] | None = None
    if learn:
        proposal = build_repair_proposal(incident.to_dict(repo_root=repo), repo_root=repo)
        link_proposal_to_incident(incident_path, proposal)
        sandbox = test_repair_plan_in_sandbox(
            {
                "spec": {
                    "playbook": (classification.get("safe_repairs") or ["restart_agent"])[0],
                    "steps": classification.get("safe_repairs") or ["restart_agent"],
                }
            },
            selector=selector,
            root=repo,
        )
        if not sandbox.get("ok"):
            escalation = {
                "status": "human_review",
                "reason": "sandbox verification failed",
                "sandbox": sandbox,
            }

    return _envelope(
        {
            "ok": False,
            "status": "incident_created",
            "id": selector,
            "phase": "learn",
            "incident_uri": incident.self_uri,
            "incident_path": str(incident_path),
            "classification": classification,
            "heal_attempt": healed,
            "proposal": proposal,
            "escalation": escalation,
        }
    )


def learn_from_incident(
    incident_path: str | Path,
    *,
    root: str | Path | None = None,
    run_sandbox: bool = True,
) -> dict[str, Any]:
    repo = _repo_root(root)
    incident = load_incident(incident_path, repo_root=repo)
    metadata = incident.get("metadata") or {}
    agent_id = str(metadata.get("agent_id") or "")
    classification = incident.get("classification") or classify_inspection(
        {"incidents": incident.get("symptoms") or []}
    )
    proposal = build_repair_proposal(incident, repo_root=repo)
    link_proposal_to_incident(Path(incident_path), proposal)

    sandbox_result = None
    if run_sandbox and agent_id:
        sandbox_result = test_repair_plan_in_sandbox(
            {
                "spec": {
                    "playbook": (classification.get("safe_repairs") or ["restart_agent"])[0],
                    "steps": classification.get("safe_repairs") or ["restart_agent"],
                }
            },
            selector=agent_id,
            root=repo,
        )

    return _envelope(
        {
            "ok": bool(sandbox_result.get("ok")) if sandbox_result else True,
            "status": "proposal_created",
            "incident_path": str(incident_path),
            "proposal": proposal,
            "sandbox": sandbox_result,
        }
    )

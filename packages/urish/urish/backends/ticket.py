from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from uri3.paths import find_repo_root

from urish.ticket_workflow import build_ticket_workflow, resolve_ticket_path


def tickets_dir(*, root: Path | None = None) -> Path:
    repo = root or find_repo_root()
    return repo / "output" / "tickets"


def list_tickets(*, root: Path | None = None) -> dict[str, Any]:
    directory = tickets_dir(root)
    items: list[dict[str, Any]] = []
    if directory.exists():
        for path in sorted(directory.glob("*.yaml")):
            payload = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
            items.append(
                {
                    "id": (payload.get("metadata") or {}).get("id") or path.stem,
                    "uri": (payload.get("uri") or {}).get("self") or f"ticket://feature/{path.stem}",
                    "path": str(path),
                    "title": (payload.get("spec") or {}).get("title") or path.stem,
                }
            )
    return {
        "ok": True,
        "workflow_status": "completed",
        "execution_status": "completed",
        "service_result_status": "succeeded",
        "result_type": "tickets",
        "data": {"tickets": items, "count": len(items)},
        "meta": {"runtime": "urish", "transport": "ticket"},
    }


def show_ticket(target: str, *, root: Path | None = None) -> dict[str, Any]:
    path = resolve_ticket_path(target, root=root)
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        return {"ok": False, "not_found": True, "error": f"invalid ticket file: {path}"}
    ticket_uri = (payload.get("uri") or {}).get("self") or target
    workflow = build_ticket_workflow(payload, ticket_target=ticket_uri)
    return {
        "ok": True,
        "workflow_status": "completed",
        "execution_status": "completed",
        "service_result_status": "succeeded",
        "result_type": "ticket",
        "data": {
            **payload,
            "detected_intent": workflow["intent"],
            "next_steps": workflow["next_steps"],
        },
        "meta": {"runtime": "urish", "transport": "ticket", "target": str(path)},
    }


def import_tickets(strategy: str, *, sprint: str = "", root: Path | None = None) -> dict[str, Any]:
    from hypervisor.integrations.planfile import import_tickets_from_planfile

    repo = root or find_repo_root()
    strategy_path = Path(strategy)
    if not strategy_path.is_absolute():
        strategy_path = repo / strategy
    payload = import_tickets_from_planfile(strategy_path, repo_root=repo, sprint_id=sprint or None)
    return {
        "ok": bool(payload.get("ok", True)),
        "workflow_status": "completed",
        "execution_status": "completed",
        "service_result_status": "succeeded" if payload.get("ok", True) else "failed",
        "result_type": "ticket_import",
        "data": payload,
        "meta": {"runtime": "urish", "transport": "ticket", "target": str(strategy_path)},
    }


def plan_ticket(target: str, *, root: Path | None = None) -> dict[str, Any]:
    from hypervisor.integrations.planfile import propose_from_ticket_path

    repo = root or find_repo_root()
    path = resolve_ticket_path(target, root=root)
    payload = propose_from_ticket_path(path, repo_root=repo)
    ticket = yaml.safe_load(path.read_text(encoding="utf-8"))
    ticket_uri = (ticket.get("uri") or {}).get("self") if isinstance(ticket, dict) else target
    workflow = build_ticket_workflow(
        ticket if isinstance(ticket, dict) else {},
        ticket_target=str(ticket_uri or target),
        proposal_path=str(payload.get("proposal_path") or ""),
    )
    return {
        "ok": True,
        "workflow_status": "completed",
        "execution_status": "completed",
        "service_result_status": "succeeded",
        "result_type": "ticket_plan",
        "data": {
            **payload,
            "detected_intent": workflow["intent"],
            "next_steps": workflow["next_steps"],
        },
        "meta": {"runtime": "urish", "transport": "ticket", "target": str(path)},
    }

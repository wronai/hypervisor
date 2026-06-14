from __future__ import annotations

from pathlib import Path
from typing import Any

from uri3.paths import find_repo_root

from urish.ecosystem_workflow import SHELL_CMD, build_ecosystem_next_steps
from urish.intent import detect_intent


def resolve_ticket_path(target: str, *, root: Path | None = None) -> Path:
    repo = root or find_repo_root()
    tickets_dir = repo / "output" / "tickets"
    if target.startswith("ticket://"):
        parts = target.replace("ticket://", "", 1).split("/", 1)
        ticket_id = parts[1] if len(parts) > 1 else parts[0]
        path = tickets_dir / f"{ticket_id}.yaml"
        if path.exists():
            return path
    path = Path(target)
    if path.is_absolute() and path.exists():
        return path
    if path.exists():
        return path
    fallback = tickets_dir / f"{target}.yaml"
    if fallback.exists():
        return fallback
    repo_relative = repo / target
    if repo_relative.exists():
        return repo_relative
    raise FileNotFoundError(f"ticket not found: {target}")


def detect_intent_from_ticket(ticket: dict[str, Any]) -> dict[str, Any]:
    from urigen.models import wants_dashboard

    spec = ticket.get("spec") or {}
    text = " ".join(
        str(spec.get(key) or "")
        for key in ("title", "description", "type")
    ).strip()
    scope = ticket.get("scope") or {}
    affected = scope.get("affected_uris") or []
    if affected:
        text = f"{text} {' '.join(str(item) for item in affected)}"
    if wants_dashboard(text, "minimal"):
        return {
            "kind": "ecosystem",
            "subtype": "dashboard-agent",
            "profile": "dashboard-agent",
            "ecosystem_id": "hypervisor-dashboard",
            "agent_id": "hypervisor-dashboard",
            "deployment_id": "hypervisor-dashboard.local",
            "dashboard_port": 8788,
        }
    intent = detect_intent(text or str((ticket.get("metadata") or {}).get("id") or ""))
    if intent.get("kind") == "ecosystem":
        return intent
    metadata = ticket.get("metadata") or {}
    ticket_id = str(metadata.get("id") or "ticket")
    return {
        "kind": "evolution",
        "subtype": "ticket-driven",
        "ticket_id": ticket_id,
        "profile": None,
        "ecosystem_id": None,
        "agent_id": None,
    }


def build_evolution_next_steps(*, ticket_target: str, proposal_path: str) -> list[str]:
    return [
        f"{SHELL_CMD} evolve from-ticket {ticket_target}",
        f"{SHELL_CMD} proposal verify {proposal_path}",
        f"{SHELL_CMD} proposal apply {proposal_path} --sandbox",
    ]


def build_ticket_workflow(
    ticket: dict[str, Any],
    *,
    ticket_target: str,
    proposal_path: str | None = None,
) -> dict[str, Any]:
    intent = detect_intent_from_ticket(ticket)
    spec = ticket.get("spec") or {}
    prompt = str(spec.get("description") or spec.get("title") or "").strip()
    steps: list[str] = [f"{SHELL_CMD} ticket show {ticket_target}"]
    if proposal_path:
        steps.extend(build_evolution_next_steps(ticket_target=ticket_target, proposal_path=proposal_path))
    else:
        steps.append(f"{SHELL_CMD} evolve from-ticket {ticket_target}")

    ecosystem_steps: list[str] = []
    if intent.get("subtype") == "dashboard-agent":
        eco_id = str(intent.get("ecosystem_id") or "hypervisor-dashboard")
        ecosystem_steps = build_ecosystem_next_steps(
            prompt=prompt or "stwórz web UI agenta hypervisor-dashboard",
            intent={**intent, "ecosystem_id": eco_id},
        )
        steps.extend(ecosystem_steps)

    return {
        "intent": intent,
        "next_steps": steps,
        "ecosystem_steps": ecosystem_steps,
    }

"""Tests for urish doctor --strict and ticket evolution workflow."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import yaml

from urish.backends.doctor import doctor_all
from urish.backends.evolve import evolve_from_ticket
from urish.backends.ticket import show_ticket
from urish.cli import main
from urish.ticket_workflow import build_ticket_workflow, detect_intent_from_ticket


def _write_ticket(tmp_path: Path, *, ticket_id: str = "PL-10", description: str = "Add ticket URI") -> Path:
    ticket = {
        "$schema": "schemas/ticket.schema.json",
        "apiVersion": "uri3.io/v1",
        "kind": "Ticket",
        "metadata": {"id": ticket_id, "created_at": "2026-06-14T00:00:00Z", "created_by": "test"},
        "uri": {
            "self": f"ticket://feature/{ticket_id}",
            "proposal": f"evolution://proposal/from-ticket/{ticket_id}",
        },
        "spec": {
            "type": "feature",
            "title": "Ticket URI scheme",
            "description": description,
        },
    }
    tickets_dir = tmp_path / "output" / "tickets"
    tickets_dir.mkdir(parents=True)
    path = tickets_dir / f"{ticket_id}.yaml"
    path.write_text(yaml.safe_dump(ticket, sort_keys=False), encoding="utf-8")
    return path


def test_detect_dashboard_intent_from_ticket():
    ticket = {
        "metadata": {"id": "PL-10"},
        "spec": {
            "title": "Hypervisor dashboard",
            "description": "stwórz web UI do pokazywania procesów hypervisora",
        },
    }
    intent = detect_intent_from_ticket(ticket)
    assert intent["subtype"] == "dashboard-agent"
    assert intent["ecosystem_id"] == "hypervisor-dashboard"


def test_ticket_workflow_includes_ecosystem_steps():
    ticket = {
        "metadata": {"id": "PL-10"},
        "uri": {"self": "ticket://feature/PL-10"},
        "spec": {
            "title": "Dashboard",
            "description": "stwórz web UI agenta hypervisor-dashboard do pokazywania procesów",
        },
    }
    workflow = build_ticket_workflow(
        ticket,
        ticket_target="ticket://feature/PL-10",
        proposal_path="evolution/proposals/proposal_from_ticket_PL-10.yaml",
    )
    joined = "\n".join(workflow["next_steps"])
    assert "urish proposal verify" in joined
    assert "urish ecosystem generate" in joined
    assert "hypervisor-dashboard" in joined


def test_show_ticket_returns_next_steps(tmp_path):
    _write_ticket(tmp_path, description="Regular feature")
    with patch("urish.ticket_workflow.find_repo_root", return_value=tmp_path):
        result = show_ticket("ticket://feature/PL-10")
    assert result["ok"] is True
    assert result["data"]["next_steps"]
    assert result["data"]["detected_intent"]["kind"] == "evolution"


def test_evolve_from_ticket_generates_proposal_and_steps(tmp_path):
    _write_ticket(
        tmp_path,
        description="stwórz web UI agenta do pokazywania procesów hypervisora",
    )
    schemas = Path(__file__).resolve().parents[2] / "schemas"
    for schema in schemas.rglob("*.schema.json"):
        rel = schema.relative_to(Path(__file__).resolve().parents[2])
        target = tmp_path / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(schema.read_text(encoding="utf-8"), encoding="utf-8")

    with patch("urish.backends.evolve.find_repo_root", return_value=tmp_path):
        result = evolve_from_ticket("ticket://feature/PL-10")
    assert result["ok"] is True
    assert result["data"]["proposal_path"]
    assert any("urish ecosystem generate" in step for step in result["data"]["next_steps"])
    assert result["data"]["detected_intent"]["subtype"] == "dashboard-agent"


def test_doctor_strict_adds_artifact_checks():
    with patch("uri3.paths.find_repo_root") as root_mock, patch(
        "uri2run.doctor.doctor_transport_dependencies",
        return_value={"ok": True},
    ), patch("uri3.doctor.runner.run_doctor", return_value={"ok": True}), patch(
        "hypervisor.artifacts.gate.check_schemas",
        return_value={"ok": True, "checked": 1, "failed": 0, "results": []},
    ), patch(
        "hypervisor.artifacts.gate.check_artifacts",
        return_value={"ok": True, "checked": 0, "failed": 0, "results": []},
    ), patch(
        "hypervisor.artifacts.gate.check_lifecycle_coverage",
        return_value={"ok": True, "strict": True, "checked": 0},
    ):
        root_mock.return_value = Path("/tmp/repo")
        result = doctor_all(strict=True)
    assert result["strict"] is True
    check_ids = {item["id"] for item in result["checks"]}
    assert "artifacts.schemas" in check_ids
    assert "artifacts.incidents_tickets" in check_ids
    assert "artifacts.lifecycle" in check_ids


def test_cli_doctor_strict_flag():
    with patch("urish.backends.doctor.doctor_all") as mocked:
        mocked.return_value = {"ok": True, "checks": [], "failed": 0}
        code = main(["doctor", "--strict", "--json"])
        assert code == 0
        mocked.assert_called_once_with(strict=True)

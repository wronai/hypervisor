"""Tests for artifact standardization layer."""

from __future__ import annotations

from pathlib import Path

import yaml
from hypervisor.artifacts.gate import check_lifecycle_coverage
from hypervisor.deployment_registry.loader import load_deployment_registry
from hypervisor.deployment_registry.runtime_state import (
    load_runtime_state,
    save_runtime_state,
)
from hypervisor.evolution.proposal_from_source import build_evolution_proposal_from_ticket
from hypervisor.integrations.planfile import import_tickets_from_planfile
from hypervisor.repair.validator import (
    validate_evolution_proposal_dict,
    validate_runtime_state_dict,
)
from uri3.artifacts.evolution_source import normalize_evolution_source
from uri3.logs.writer import append_log


def test_runtime_state_schema_on_save(tmp_path):
    save_runtime_state(
        "demo.local",
        {
            "agent_ref": "agent://demo",
            "pid": 12345,
            "status": "running",
            "command": "uvicorn main:app --port 8101",
            "health_uri": "http://localhost:8101/health",
        },
        tmp_path,
    )
    loaded = load_runtime_state("demo.local", tmp_path)
    assert loaded is not None
    assert loaded["kind"] == "RuntimeState"
    assert loaded["pid"] == 12345
    assert loaded["process_status"] == "running"
    assert loaded["uri"]["self"] == "runtime://agent/demo.local/state"
    errors = validate_runtime_state_dict(
        yaml.safe_load((tmp_path / "output/runtime/agents/demo.local/state.json").read_text()),
        tmp_path,
    )
    assert errors == []


def test_legacy_runtime_state_upgrades_on_load(tmp_path):
    state_path = tmp_path / "output/runtime/agents/demo.local/state.json"
    state_path.parent.mkdir(parents=True)
    state_path.write_text(
        '{"id": "demo.local", "pid": 999999, "status": "running", "health_uri": "http://localhost:8101/health"}',
        encoding="utf-8",
    )
    loaded = load_runtime_state("demo.local", tmp_path)
    assert loaded["process_status"] == "running"
    assert loaded["health_uri"] == "http://localhost:8101/health"


def test_log_event_envelope(tmp_path):
    append_log(
        "hypervisor",
        "health check failed",
        level="ERROR",
        root=tmp_path,
        subject_uri="agent://demo",
    )
    line = (tmp_path / "output/logs/hypervisor.log").read_text().strip()
    import json

    payload = json.loads(line)
    assert payload["kind"] == "LogEvent"
    assert payload["event"]["code"] == "LOG_ERROR"
    assert payload["uri"]["subject"] == "agent://demo"


def test_deployment_registry_declared_runtime_views():
    registry = load_deployment_registry(Path(__file__).resolve().parents[2])
    deployment = registry.by_id("weather-map-agent.local")
    assert deployment is not None
    assert deployment.declared is not None
    assert deployment.declared.health_uri == "http://localhost:8101/health"


def test_planfile_ticket_import_and_proposal(tmp_path):
    strategy = tmp_path / "planfile.yaml"
    strategy.write_text(
        """
name: hypervisor-evolution
sprints:
  - id: 1
    tasks:
      - id: PL-1
        type: feature
        title: Add ticket URI scheme
        description: Introduce ticket:// artifacts
        priority: critical
""",
        encoding="utf-8",
    )
    imported = import_tickets_from_planfile(strategy, repo_root=tmp_path, sprint_id="1")
    assert imported["count"] == 1
    ticket_path = Path(imported["imported"][0]["path"])
    ticket = yaml.safe_load(ticket_path.read_text(encoding="utf-8"))
    assert ticket["uri"]["self"] == "ticket://feature/PL-1"
    proposal = build_evolution_proposal_from_ticket(ticket, repo_root=tmp_path)
    assert proposal["proposal_uri"].startswith("evolution://proposal/from-ticket/PL-1")
    errors = validate_evolution_proposal_dict(proposal["payload"], tmp_path)
    assert errors == []


def test_evolution_source_normalization():
    source = normalize_evolution_source(uri="incident://agent/demo/inc_001")
    assert source.kind == "Incident"
    assert source.schema == "schemas/incident.schema.json"


def test_artifact_lifecycle_coverage_reports_loose_files(tmp_path):
    canonical = tmp_path / "output/runtime/agents/demo.local/state.json"
    canonical.parent.mkdir(parents=True)
    canonical.write_text(
        """
{
  "$schema": "schemas/runtime_state.schema.json",
  "apiVersion": "uri3.io/v1",
  "kind": "RuntimeState",
  "uri": {"self": "runtime://agent/demo.local/state"},
  "id": "demo.local",
  "status": {"process_status": "running"}
}
""",
        encoding="utf-8",
    )
    loose = tmp_path / "output/artifacts/operator/open_health.json"
    loose.parent.mkdir(parents=True)
    loose.write_text('{"url": "http://localhost:8101/health"}', encoding="utf-8")

    report = check_lifecycle_coverage(tmp_path, strict=False)
    assert report["ok"] is True
    assert report["canonical"] == 1
    assert report["loose"] == 1

    strict = check_lifecycle_coverage(tmp_path, strict=True)
    assert strict["ok"] is False
    assert strict["samples"][0]["path"] == "output/artifacts/operator/open_health.json"

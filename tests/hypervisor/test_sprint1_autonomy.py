"""Tests for Sprint 1 autonomy: readiness report, inspection pipeline, repair plan."""

from __future__ import annotations

import pytest

from hypervisor.deployment_registry.inspection.readiness import build_agent_readiness_report
from hypervisor.repair.plan_builder import build_repair_plan_from_diagnosis
from hypervisor.repair.supervisor import diagnose_agent


def test_build_agent_readiness_report_separates_process_from_health():
    report = build_agent_readiness_report(
        deployment_id="weather-map-agent.local",
        service_status="unhealthy",
        runtime="running",
        process_alive=True,
        health={"ok": False, "uri": "http://localhost:8101/health"},
        card={"ok": True, "uri": "http://localhost:8101/.well-known/agent-card.json"},
        logs={"error_count": 0},
        incidents=[{"code": "PROCESS_RUNNING_BUT_UNHEALTHY", "detail": "probe failed"}],
        effective_health_uri="http://localhost:8101/health",
        declared_health_uri="http://localhost:8101/health",
    )
    assert report["kind"] == "AgentReadinessReport"
    assert report["process_status"] == "running"
    assert report["health_status"] == "failed"
    assert report["recommended_action"] == "repair"
    assert report["deployment_status"] == "unhealthy"
    assert "PROCESS_RUNNING_BUT_UNHEALTHY" in report["incident_codes"]


def test_build_agent_readiness_report_rebind_on_port_conflict():
    report = build_agent_readiness_report(
        deployment_id="agent.local",
        service_status="degraded",
        runtime="running",
        process_alive=True,
        health={"ok": False, "foreign_service": "identification-backend"},
        card={"ok": False},
        logs={"error_count": 0},
        incidents=[
            {"code": "PORT_OCCUPIED", "detail": "port 8101 in use"},
            {"code": "FOREIGN_SERVICE_ON_PORT", "detail": "foreign service"},
        ],
        effective_health_uri="http://localhost:8101/health",
        declared_health_uri="http://localhost:8101/health",
    )
    assert report["recommended_action"] == "rebind_port"


def test_build_repair_plan_from_diagnosis():
    diagnosis = {
        "id": "weather-map-agent.local",
        "inspection": {
            "id": "weather-map-agent.local",
            "agent_readiness": {"recommended_action": "restart"},
        },
        "classification": {
            "family": ["HEALTH_TIMEOUT"],
            "safe_repairs": ["read_logs", "restart_agent"],
        },
    }
    plan = build_repair_plan_from_diagnosis(diagnosis)
    assert plan["kind"] == "RepairPlan"
    assert plan["spec"]["playbook"] == "read_logs"
    assert plan["spec"]["policy_level"] == "level_0_observe"
    assert plan["metadata"]["source_incident"].startswith("incident://")


def test_diagnose_includes_repair_plan(monkeypatch: pytest.MonkeyPatch):
    fake_inspection = {
        "ok": False,
        "id": "weather-map-agent.local",
        "incidents": [{"code": "HEALTH_FAILED", "detail": "connection refused"}],
        "warnings": [],
        "health": {"ok": False, "error": "connection refused"},
        "log_errors": {"error_count": 0, "entries": []},
        "readiness": {"process": "stopped", "health": "failed"},
        "agent_readiness": {
            "recommended_action": "restart",
            "health_status": "failed",
            "process_status": "stopped",
        },
    }

    monkeypatch.setattr(
        "hypervisor.repair.supervisor.inspect_agent",
        lambda *_args, **_kwargs: fake_inspection,
    )
    monkeypatch.setattr(
        "hypervisor.repair.supervisor.find_matching_case",
        lambda *_args, **_kwargs: None,
    )

    payload = diagnose_agent("weather-map-agent.local")
    assert payload["result_type"] == "diagnosis"
    assert "repair_plan" in payload
    assert payload["repair_plan"]["kind"] == "RepairPlan"
    assert payload["repair_plan"]["spec"]["playbook"] in {
        "restart_agent",
        "read_logs",
        "check_process",
        "sync_health_uri",
    }

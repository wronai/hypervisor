"""Agent registry detection, URI tasks, and hypervisor repair lifecycle."""

from __future__ import annotations

from typing import Any

import pytest
from fastapi.testclient import TestClient

from hypervisor.deployment_registry.runner import build_run_plan, resolve_deployment
from hypervisor_dashboard_agent.main import app
from hypervisor_dashboard_agent.uri_client import call_system_uri, list_agent_deployments


NEW_AGENT_IDS = ("user-agent.local", "invoices-agent.local")


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


def test_registry_lists_new_agents():
    agents = list_agent_deployments()
    ids = {item["id"] for item in agents}
    for agent_id in NEW_AGENT_IDS:
        assert agent_id in ids, f"missing deployment {agent_id}"


def test_api_agents_includes_new_deployments(client: TestClient):
    response = client.get("/api/agents")
    assert response.status_code == 200
    ids = {item["id"] for item in response.json()["agents"]}
    for agent_id in NEW_AGENT_IDS:
        assert agent_id in ids


@pytest.mark.parametrize("agent_id,port,module", [
    ("user-agent.local", 8102, "agents.generated.user_agent.main:app"),
    ("invoices-agent.local", 8103, "agents.generated.invoices_agent.main:app"),
])
def test_build_run_plan_for_new_agents(agent_id: str, port: int, module: str):
    deployment = resolve_deployment(agent_id)
    plan = build_run_plan(deployment)
    assert plan["module"] == module
    assert plan["port"] == port
    assert plan["health_uri"] == f"http://localhost:{port}/health"


def test_uri_health_dry_run_for_new_agent():
    result = call_system_uri("health://agent/user-agent.local", dry_run=True)
    assert result["result_type"] == "health"
    assert result["agent_id"] == "user-agent.local"


def test_uri_repair_diagnose_for_new_agent():
    result = call_system_uri("repair://agent/invoices-agent.local/diagnose")
    assert result["result_type"] == "diagnosis"
    assert result["id"] == "invoices-agent.local"
    assert "repair_plan" in result


def test_uri_repair_apply_dry_run(client: TestClient):
    response = client.post(
        "/api/uri/call",
        json={
            "uri": "repair://agent/user-agent.local/apply",
            "dry_run": True,
            "policy": "dev",
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload.get("dry_run") is True or payload.get("result_type") == "repair"


def test_uri_repair_apply_requires_approval(client: TestClient):
    response = client.post(
        "/api/uri/call",
        json={"uri": "repair://agent/invoices-agent.local/apply", "policy": "dev"},
    )
    assert response.status_code == 403
    assert response.json()["detail"]["requires_approval"] is True


def test_hypervisor_repair_supervisor_auto(monkeypatch: pytest.MonkeyPatch):
    from hypervisor.repair.supervisor import repair_apply

    fake_diagnosis: dict[str, Any] = {
        "ok": False,
        "id": "user-agent.local",
        "inspection": {"ok": False, "service_status": "stopped"},
        "classification": {"primary": "agent_stopped", "safe_repairs": ["restart_agent"]},
        "repair_plan": {"playbooks": ["restart_agent"]},
    }

    monkeypatch.setattr(
        "hypervisor.repair.supervisor.diagnose_agent",
        lambda *args, **kwargs: fake_diagnosis,
    )
    monkeypatch.setattr(
        "hypervisor.repair.supervisor.apply_playbook",
        lambda playbook, **kwargs: {"ok": True, "playbook": playbook, "status": "applied"},
    )
    monkeypatch.setattr(
        "hypervisor.repair.supervisor.inspect_agent",
        lambda *args, **kwargs: {"ok": True, "service_status": "healthy"},
    )
    monkeypatch.setattr("hypervisor.repair.supervisor.time.sleep", lambda *_args: None)

    result = repair_apply("user-agent.local", approved=True, safe=True)
    assert result["ok"] is True
    assert any(item.get("playbook") == "restart_agent" for item in result.get("actions", []))

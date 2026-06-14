"""Tests for hypervisor-dashboard-agent system agent."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from hypervisor_dashboard_agent.main import app
from hypervisor_dashboard_agent.policy import decision_for_uri, preview_action
from hypervisor_dashboard_agent.uri_client import resolve_view_uri


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


def test_health_and_agent_card(client: TestClient):
    health = client.get("/health")
    assert health.status_code == 200
    assert health.json()["agent"] == "hypervisor-dashboard"

    card = client.get("/.well-known/agent-card.json")
    assert card.status_code == 200
    payload = card.json()
    assert payload["id"] == "hypervisor-dashboard"
    assert any(cap["id"] == "process.view" for cap in payload["capabilities"])


def test_ui_agents_lists_deployments(client: TestClient, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(
        "hypervisor_dashboard_agent.routes.list_agent_deployments",
        lambda **kwargs: [
            {
                "id": "weather-map-agent.local",
                "agent_ref": "agent://weather-map-agent",
                "status": "generated",
                "view_uri": "view://process/agent/weather-map-agent.local/latest",
            }
        ],
    )
    response = client.get("/ui/agents")
    assert response.status_code == 200
    assert "weather-map-agent.local" in response.text


def test_api_process_view(client: TestClient, monkeypatch: pytest.MonkeyPatch):
    fake_view = {
        "result_type": "view",
        "view_uri": "view://process/agent/weather-map-agent.local/latest",
        "content_type": "text/html",
        "title": "Weather Map Agent",
        "data": {"service_status": "healthy"},
        "html": "<html>ok</html>",
    }

    class _Envelope:
        def to_dict(self):
            return fake_view

    monkeypatch.setattr(
        "hypervisor_dashboard_agent.routes.resolve_view_uri",
        lambda uri, **kwargs: _Envelope(),
    )
    response = client.get("/api/view/process/agent/weather-map-agent.local")
    assert response.status_code == 200
    assert response.json()["result_type"] == "view"


def test_uri_call_read_allowed(client: TestClient, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(
        "hypervisor_dashboard_agent.routes.call_system_uri",
        lambda uri, **kwargs: {"result_type": "health", "ok": True},
    )
    response = client.post(
        "/api/uri/call",
        json={"uri": "health://agent/weather-map-agent.local", "policy": "dev"},
    )
    assert response.status_code == 200
    assert response.json()["ok"] is True


def test_uri_call_repair_apply_requires_approval(client: TestClient):
    response = client.post(
        "/api/uri/call",
        json={"uri": "repair://agent/weather-map-agent.local/apply", "policy": "dev"},
    )
    assert response.status_code == 403
    detail = response.json()["detail"]
    assert detail["requires_approval"] is True


def test_uri_call_repair_apply_with_approval(client: TestClient, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(
        "hypervisor_dashboard_agent.routes.call_system_uri",
        lambda uri, **kwargs: {"result_type": "repair", "ok": True},
    )
    response = client.post(
        "/api/uri/call",
        json={
            "uri": "repair://agent/weather-map-agent.local/apply",
            "approved": True,
            "policy": "dev",
        },
    )
    assert response.status_code == 200


def test_policy_preview_repair():
    preview = preview_action("repair://agent/x/apply", policy="dev")
    assert preview["requires_approval"] is True
    assert preview["execute_allowed_with_approval"] is True


def test_local_target_supports_packages_path():
    from hypervisor.deployment_registry.local_targets import local_target_to_module

    assert (
        local_target_to_module("local://packages/hypervisor-dashboard-agent")
        == "hypervisor_dashboard_agent.main:app"
    )


def test_resolve_view_uri_process(monkeypatch: pytest.MonkeyPatch):
    from hypervisor_dashboard_agent.models import ProcessViewModel, ViewEnvelope

    model = ProcessViewModel(
        agent_id="weather-map-agent.local",
        agent_ref="agent://weather-map-agent",
        title="Weather Map Agent",
        service_status="healthy",
        deployment_status="healthy",
        process_status="running",
        health_status="ok",
        recommended_action="none",
        effective_health_uri="http://localhost:8101/health",
        effective_port=8101,
    )
    monkeypatch.setattr(
        "hypervisor_dashboard_agent.uri_client.build_process_view",
        lambda agent_id, **kwargs: model,
    )
    monkeypatch.setattr(
        "hypervisor_dashboard_agent.uri_client.render_process_html",
        lambda m: "<html>process</html>",
    )
    envelope = resolve_view_uri("view://process/agent/weather-map-agent.local/latest")
    assert envelope.content_type == "text/html"
    assert envelope.data["agent_id"] == "weather-map-agent.local"

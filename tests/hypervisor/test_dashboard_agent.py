"""Tests for hypervisor-dashboard-agent system agent."""

from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from hypervisor_dashboard_agent.main import app
from hypervisor_dashboard_agent.policy import preview_action
from hypervisor_dashboard_agent.uri_client import call_system_uri, resolve_view_uri


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


def test_uri_call_execution_error_returns_failed_envelope(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
):
    def fail_call(*args, **kwargs):
        raise OSError("read-only registry")

    monkeypatch.setattr("hypervisor_dashboard_agent.routes.call_system_uri", fail_call)
    response = client.post(
        "/api/uri/call",
        json={"uri": "repair://agent/weather-map-agent.local/diagnose", "policy": "dev"},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["ok"] is False
    assert payload["service_result_status"] == "failed"
    assert payload["error_type"] == "OSError"
    assert "read-only registry" in payload["message_markdown"]


def test_policy_preview_repair():
    preview = preview_action("repair://agent/x/apply", policy="dev")
    assert preview["requires_approval"] is True
    assert preview["execute_allowed_with_approval"] is True


def test_monitor_webhook_surfaces_in_events(client: TestClient, tmp_path, monkeypatch):
    monkeypatch.setattr("hypervisor_dashboard_agent.routes.find_repo_root", lambda: tmp_path)
    monkeypatch.setattr(
        "hypervisor_dashboard_agent.events_service.list_agent_deployments",
        lambda **kwargs: [],
    )

    response = client.post(
        "/api/monitors/webhook",
        json={
            "source": "uptime",
            "event": "PAGE_DOWN",
            "summary": "landing page down",
            "url": "http://localhost:8788/www/",
            "ok": False,
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["result_type"] == "monitor_webhook"
    assert payload["event"] == "PAGE_DOWN"

    events = client.get("/api/events?limit=10").json()["events"]
    event_types = {event["type"] for event in events}
    assert "monitor.snapshot" in event_types
    assert "log.event" in event_types
    assert any("landing page down" in event["summary"] for event in events)


def test_local_target_supports_packages_path():
    from hypervisor.deployment_registry.local_targets import local_target_to_module

    assert (
        local_target_to_module("local://packages/hypervisor-dashboard-agent")
        == "hypervisor_dashboard_agent.main:app"
    )


def test_resolve_view_uri_process(monkeypatch: pytest.MonkeyPatch):
    from hypervisor_dashboard_agent.models import ProcessViewModel

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


def test_call_system_uri_marks_view_and_logs_as_success(monkeypatch: pytest.MonkeyPatch):
    fake_view = {
        "result_type": "view",
        "view_uri": "view://process/agent/demo.local/latest",
        "content_type": "text/html",
        "title": "Demo",
        "data": {},
        "html": "<html>ok</html>",
    }

    class _Envelope:
        def to_dict(self):
            return fake_view

    monkeypatch.setattr(
        "hypervisor_dashboard_agent.uri_client.resolve_view_uri",
        lambda *_a, **_k: _Envelope(),
    )
    monkeypatch.setattr("uri3.logs.reader.read_logs_result", lambda *_a, **_k: [])

    view = call_system_uri("view://process/agent/demo.local/latest")
    logs = call_system_uri("log://file/output/logs/agents/demo.log?tail=5")

    assert view["ok"] is True
    assert view["service_result_status"] == "succeeded"
    assert logs["ok"] is True
    assert logs["service_result_status"] == "succeeded"


def test_uri_implies_dry_run_suffix():
    from hypervisor_dashboard_agent.uri_client import uri_implies_dry_run

    assert uri_implies_dry_run("workflow://portal/zus-form/dry-run") is True
    assert uri_implies_dry_run("workflow://portal/zus-form") is False


def test_call_system_uri_workflow_portal_zus_dry_run():
    result = call_system_uri("workflow://portal/zus-form/dry-run", dry_run=False)
    assert result.get("ok") is True
    assert result.get("result_type") in {"plan", "workflow", "query"}


def test_api_uri_call_workflow_without_dry_run_checkbox(client: TestClient):
    """URIs ending in /dry-run must execute even when dry_run=false in the body."""
    response = client.post(
        "/api/uri/call",
        json={
            "uri": "workflow://portal/zus-form/dry-run",
            "dry_run": False,
            "approved": False,
            "policy": "dev",
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload.get("ok") is True
    assert payload.get("result_type") in {"plan", "workflow", "query"}
    assert "unsupported or unimplemented URI" not in payload.get("message_markdown", "")


def test_call_system_uri_http_health(monkeypatch: pytest.MonkeyPatch):
    class _Response:
        is_success = True
        status_code = 200
        text = '{"ok":true}'

        @staticmethod
        def json():
            return {"ok": True}

    monkeypatch.setattr(
        "httpx.get",
        lambda *args, **kwargs: _Response(),
    )
    result = call_system_uri("http://localhost:8118/health")
    assert result.get("ok") is True
    assert result.get("result_type") == "http"


def test_call_system_uri_browser_open_mock():
    result = call_system_uri(
        "browser://chrome/page/open",
        approved=True,
        dry_run=False,
        payload={"url": "https://example.com/reports"},
    )
    assert result.get("ok") is True
    assert result.get("result_type") in {"operator", "query", "command", "lifecycle", "data"}


def test_call_system_uri_browser_open_dry_run_plan():
    result = call_system_uri("browser://chrome/page/open", dry_run=True)
    assert result.get("ok") is True
    assert result.get("result_type") == "plan"
    assert result.get("explain", {}).get("matched_registry") == "uri2ops"


def test_call_system_uri_office_supplier_report_dry_run():
    result = call_system_uri("workflow://office/supplier-report/monthly", dry_run=True)
    assert result.get("ok") is True
    assert result.get("result_type") in {"plan", "workflow", "query"}


def test_call_system_uri_office_supplier_report_execute(tmp_path: Path):
    result = call_system_uri(
        "workflow://office/supplier-report/monthly",
        approved=True,
        dry_run=False,
        artifact_root=tmp_path,
    )
    assert result.get("ok") is True
    assert result.get("result_type") == "workflow"


def test_api_uri_call_office_supplier_report(client: TestClient):
    response = client.post(
        "/api/uri/call",
        json={
            "uri": "workflow://office/supplier-report/monthly",
            "dry_run": True,
            "approved": False,
            "policy": "dev",
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload.get("ok") is True
    assert "No capability matches URI" not in payload.get("message_markdown", "")


def test_api_uri_call_browser_open(client: TestClient):
    response = client.post(
        "/api/uri/call",
        json={
            "uri": "browser://chrome/page/open",
            "dry_run": False,
            "approved": True,
            "policy": "dev",
            "payload": {"url": "https://example.com/reports"},
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload.get("ok") is True
    assert "unsupported or unimplemented URI" not in payload.get("message_markdown", "")


def test_api_uri_call_browser_open_requires_approval(client: TestClient):
    response = client.post(
        "/api/uri/call",
        json={
            "uri": "browser://chrome/page/open",
            "dry_run": False,
            "approved": False,
            "policy": "dev",
            "payload": {"url": "https://example.com/reports"},
        },
    )
    assert response.status_code == 403
    detail = response.json()["detail"]
    assert detail["requires_approval"] is True
    assert "dry-run" in detail["error"]


def test_api_uri_call_desktop_operator_health(client: TestClient):
    response = client.post(
        "/api/uri/call",
        json={
            "uri": "health://agent/desktop-operator.local",
            "dry_run": False,
            "approved": False,
            "policy": "dev",
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload.get("result_type") == "health"
    assert "Deployment not found" not in payload.get("message_markdown", "")

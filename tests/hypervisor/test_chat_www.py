"""Tests for www chat markdown formatting and /api/ask."""

from __future__ import annotations

from typing import Any

import pytest
from fastapi.testclient import TestClient
from hypervisor_dashboard_agent.chat_format import format_ask_markdown, format_uri_result_markdown
from hypervisor_dashboard_agent.main import app


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


def test_format_ask_markdown_dashboard():
    md = format_ask_markdown(
        {
            "detected_kind": "ecosystem",
            "detected_subtype": "dashboard-agent",
            "profile": "dashboard-agent",
            "ecosystem_id": "hypervisor-dashboard",
            "agent_id": "hypervisor-dashboard",
            "planned_uris": [
                "proposal://ecosystem/hypervisor-dashboard",
                "agent://hypervisor-dashboard",
            ],
            "next_steps": [
                "urish ecosystem plan --prompt 'dashboard'",
                "urish ecosystem generate hypervisor-dashboard",
            ],
        }
    )
    assert "dashboard-agent" in md
    assert "agent://hypervisor-dashboard" in md
    assert "urish ecosystem plan" in md
    assert "proposal://" not in md


def test_format_uri_result_markdown():
    md = format_uri_result_markdown(
        {
            "ok": True,
            "result_type": "view",
            "service_result_status": "succeeded",
            "workflow_status": "completed",
            "data": {"user_summary": "Agent healthy"},
        }
    )
    assert "succeeded" in md
    assert "Agent healthy" in md


def test_api_ask_returns_markdown(client: TestClient, monkeypatch: pytest.MonkeyPatch):
    fake_envelope: dict[str, Any] = {
        "ok": True,
        "result_type": "ask",
        "data": {
            "detected_kind": "domain",
            "detected_subtype": None,
            "planned_uris": ["domain://demo"],
            "next_steps": ["uri explain domain://demo"],
        },
    }

    def fake_ask(*args: Any, **kwargs: Any) -> dict[str, Any]:
        return fake_envelope

    monkeypatch.setattr("urish.backends.ask.ask_prompt", fake_ask)

    response = client.post("/api/ask", json={"prompt": "demo domain"})
    assert response.status_code == 200
    payload = response.json()
    assert payload["ok"] is True
    assert "domain://demo" in payload["message_markdown"]
    assert payload["data"]["detected_kind"] == "domain"


def test_root_redirects_to_www(client: TestClient):
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 302
    assert response.headers["location"] == "/www/"


def test_www_index_served(client: TestClient):
    response = client.get("/www/")
    assert response.status_code == 200
    assert "Hypervisor Chat" in response.text
    assert "quick-prompts" in response.text
    assert "agent-list" in response.text
    assert "api-detail" in response.text

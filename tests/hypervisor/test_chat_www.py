"""Tests for www chat markdown formatting and /api/ask."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
import yaml
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


def test_format_uri_result_dry_run_preview():
    md = format_uri_result_markdown(
        {
            "result_type": "dry_run",
            "status": "preview",
            "workflow_status": "planned",
            "service_result_status": "preview",
        }
    )
    assert "preview" in md
    assert "failed" not in md.splitlines()[0].lower()


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
    assert "Taskinity" in response.text
    assert "Autonomia w praktyce" in response.text
    assert "tour-slide-host" in response.text
    assert "tour-live-strip" in response.text
    assert "scenario-lab" in response.text
    assert "scenario-terminal" in response.text
    assert "system-map" in response.text
    assert "Deployment registry" in response.text
    assert "landing.css" in response.text


def test_www_chat_served(client: TestClient):
    response = client.get("/www/chat.html")
    assert response.status_code == 200
    assert "Taskinity Chat" in response.text
    assert "quick-prompts" in response.text
    assert "agent-list" in response.text
    assert "copy-chat-btn" in response.text
    assert "Kopiuj chat" in response.text


def test_www_landing_has_tour_copy(client: TestClient):
    response = client.get("/www/")
    assert response.status_code == 200
    assert "tour-copy-chat" in response.text
    assert "Kopiuj chat" in response.text


def test_www_landing_js_explains_repair_loop(repo_root: Path):
    script = (repo_root / "www" / "landing.js").read_text(encoding="utf-8")
    assert "buildSlideRepair" in script
    assert "SCENARIOS" in script
    assert "scenario-replay" in script
    assert "setSystemMapFocus" in script
    assert "failSafeTimer" in script
    assert "RUNTIME_STATE_STALE" in script
    assert "hypervisor supervise user-agent.local --repair auto" in script


def test_www_compose_mounts_system_artifacts(repo_root: Path):
    compose = yaml.safe_load((repo_root / "www" / "docker-compose.yml").read_text())
    volumes = compose["services"]["www-chat"]["volumes"]
    assert "../agents/generated:/app/agents/generated:ro" in volumes
    assert "../deployments:/app/deployments:ro" in volumes
    assert "../knowledge:/app/knowledge:ro" in volumes
    assert "../output:/app/output" in volumes


def test_www_dockerfile_includes_generated_agents_and_repair_cases(repo_root: Path):
    dockerfile = (repo_root / "www" / "Dockerfile").read_text()
    assert "COPY agents ./agents" in dockerfile
    assert "COPY knowledge ./knowledge" in dockerfile
    assert "output/runtime/agents" in dockerfile

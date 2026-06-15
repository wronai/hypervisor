"""Tests for www chat markdown formatting and /api/ask."""

from __future__ import annotations

import asyncio
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest
import yaml
from fastapi.testclient import TestClient
from hypervisor_dashboard_agent.chat_format import (
    format_ask_markdown,
    format_uri_result_markdown,
    format_uri_result_summary,
)
from hypervisor_dashboard_agent.main import app
from hypervisor_dashboard_agent.routes import api_events_stream


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
    assert "URI: failed" not in md


def test_format_uri_result_diagnosis_markdown():
    md = format_uri_result_markdown(
        {
            "ok": False,
            "result_type": "diagnosis",
            "workflow_status": "completed_with_service_error",
            "classification": {
                "family": ["HEALTH_TIMEOUT"],
                "safe_repairs": ["restart_agent", "read_logs"],
            },
            "inspection": {
                "service_status": "stopped",
                "process": {"running": False},
            },
        }
    )
    assert "## URI: diagnosis" in md
    assert "HEALTH_TIMEOUT" in md
    assert "restart_agent" in md


def test_format_uri_result_summary_omits_envelope_json():
    md = format_uri_result_summary(
        {
            "ok": True,
            "result_type": "view",
            "title": "Weather Map Agent",
            "data": {
                "agent_id": "weather-map-agent.local",
                "service_status": "stopped",
                "process_status": "stale",
                "health_status": "ok",
                "incident_codes": ["RUNTIME_STATE_STALE"],
                "recommended_action": "restart",
            },
        }
    )
    assert "Weather Map Agent" in md
    assert "RUNTIME_STATE_STALE" in md
    assert "Restart agent" in md
    assert "Envelope JSON" not in md


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
    assert "Envelope JSON" not in md


def test_format_uri_result_markdown_workflow_plan():
    md = format_uri_result_markdown(
        {
            "ok": True,
            "result_type": "plan",
            "workflow_status": "planned",
            "plan": {
                "graph_id": "website-screenshot-schedule",
                "steps": [
                    {
                        "id": "capture-home",
                        "uri": "browser://chrome/page/capture",
                        "payload": {"url": "https://example.com"},
                    },
                    {
                        "id": "capture-about",
                        "uri": "browser://chrome/page/capture",
                        "payload": {"url": "https://example.com/about"},
                    },
                ],
            },
        }
    )
    assert "### Workflow steps" in md
    assert "capture-home" in md
    assert "browser://chrome/page/capture" in md
    assert "https://example.com" in md
    assert "website-screenshot-schedule" in md
    assert "Envelope JSON" not in md


def test_format_uri_result_markdown_include_envelope_opt_in():
    md = format_uri_result_markdown({"ok": True, "result_type": "view"}, include_envelope=True)
    assert "Envelope JSON" in md


def test_format_uri_result_markdown_includes_runtime_and_logs():
    md = format_uri_result_markdown(
        {
            "ok": True,
            "result_type": "repair",
            "service_result_status": "succeeded",
            "workflow_status": "completed",
            "data": {
                "after": {
                    "service_status": "healthy",
                    "process": {"pid": 1234, "running": True},
                    "readiness": {
                        "process": "running",
                        "health": "ok",
                        "effective_port": 8118,
                    },
                    "effective_health_uri": "http://localhost:8118/health",
                    "log_uri": "log://hypervisor?grep=invoices-agent.local",
                    "process_log_uri": (
                        "log://file/output/logs/agents/invoices-agent.local.process.log"
                    ),
                },
                "actions": [
                    {
                        "playbook": "restart_agent",
                        "result": {"pid": 1234, "service_result_status": "succeeded"},
                    }
                ],
            },
        }
    )
    assert "### Runtime" in md
    assert "**pid:** `1234`" in md
    assert "http://localhost:8118/health" in md
    assert "### Logs" in md
    assert "log://hypervisor?grep=invoices-agent.local" in md
    assert "invoices-agent.local.process.log" in md


def test_format_uri_result_markdown_reads_top_level_runtime():
    md = format_uri_result_markdown(
        {
            "ok": True,
            "result_type": "diagnosis",
            "service_result_status": "succeeded",
            "inspection": {
                "service_status": "healthy",
                "effective_health_uri": "http://localhost:8122/health",
                "process": {"pid": 2814749, "running": True},
                "process_log_uri": (
                    "log://file/output/logs/agents/invoices-agent.local.process.log"
                ),
            },
        }
    )
    assert "### Runtime" in md
    assert "**service:** `healthy`" in md
    assert "**pid:** `2814749`" in md
    assert "http://localhost:8122/health" in md
    assert "### Logs" in md


def test_format_uri_result_markdown_shows_log_entries():
    md = format_uri_result_markdown(
        {
            "ok": True,
            "result_type": "logs",
            "service_result_status": "succeeded",
            "workflow_status": "completed",
            "entries": [
                {"line": 10, "level": "INFO", "message": "server started"},
                {"line": 11, "level": "ERROR", "message": "temporary failure"},
            ],
        }
    )
    assert "### Log entries" in md
    assert "`INFO` line `10`: server started" in md
    assert "`ERROR` line `11`: temporary failure" in md


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


@pytest.mark.parametrize(
    ("prompt", "kind", "subtype", "expected_uri"),
    [
        (
            "pokaż proces agenta weather-map-agent.local",
            "agent",
            "process_view",
            "view://process/agent/weather-map-agent.local/latest",
        ),
        (
            "zdiagnozuj agenta invoices-agent.local",
            "agent",
            "diagnose",
            "repair://agent/invoices-agent.local/diagnose",
        ),
        (
            "zdiagnozuj agenta weather-map-agent.local i pokaż plan naprawy",
            "agent",
            "diagnose",
            "repair://agent/weather-map-agent.local/diagnose",
        ),
    ],
)
def test_api_ask_detects_agent_operational_prompts(
    client: TestClient,
    prompt: str,
    kind: str,
    subtype: str,
    expected_uri: str,
):
    response = client.post("/api/ask", json={"prompt": prompt, "dry_run": True, "llm": False})
    assert response.status_code == 200
    payload = response.json()
    assert payload["ok"] is True
    assert payload["data"]["detected_kind"] == kind
    assert payload["data"]["detected_subtype"] == subtype
    assert expected_uri in payload["data"]["planned_uris"]
    assert expected_uri in payload["message_markdown"]
    assert "domain://" not in payload["message_markdown"]


def test_api_ask_detects_screenshot_schedule_as_workflow(client: TestClient):
    prompt = (
        "rob rzuty ekranów stron softreck.com prototypowanie.pl www "
        "co 5 minut do folderu usera ~/images/"
    )
    response = client.post("/api/ask", json={"prompt": prompt, "dry_run": True, "llm": False})
    assert response.status_code == 200
    payload = response.json()
    planned_uris = payload["data"]["planned_uris"]
    assert payload["ok"] is True
    assert payload["data"]["detected_kind"] == "workflow"
    assert planned_uris == ["workflow://graph/website-screenshot-schedule/dry-run"]
    assert "domain://" not in payload["message_markdown"]


def test_api_ask_detects_weather_forecast(client: TestClient):
    response = client.post(
        "/api/ask",
        json={"prompt": "prognoza pogody Gdańsk 7 dni", "dry_run": True, "llm": False},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["ok"] is True
    assert payload["data"]["detected_kind"] == "weather"
    assert payload["data"]["planned_uris"] == ["weather://forecast/Gdansk/7/html"]
    assert "weather://forecast/Gdansk/7/html" in payload["message_markdown"]
    assert "domain://" not in payload["message_markdown"]


def test_api_ask_multiline_batch_plans_each_line(client: TestClient):
    prompt = (
        "pokaż proces agenta weather-map-agent.local\n"
        "zdiagnozuj agenta invoices-agent.local\n"
        "rob rzuty ekranów stron softreck.com prototypowanie.pl www "
        "co 5 minut do folderu usera ~/images/"
    )
    response = client.post("/api/ask", json={"prompt": prompt, "dry_run": True, "llm": False})
    assert response.status_code == 200
    payload = response.json()
    data = payload["data"]
    assert data["batch"] is True
    assert data["detected_kind"] == "batch"
    assert len(data["actions"]) == 3
    assert data["actions"][0]["detected_subtype"] == "process_view"
    assert data["actions"][0]["deployment_id"] == "weather-map-agent.local"
    assert data["actions"][1]["detected_subtype"] == "diagnose"
    assert data["actions"][1]["deployment_id"] == "invoices-agent.local"
    assert data["actions"][2]["detected_kind"] == "workflow"
    assert "view://process/agent/weather-map-agent.local/latest" in payload["message_markdown"]
    assert "repair://agent/invoices-agent.local/diagnose" in payload["message_markdown"]
    assert "Detected 3 commands" in payload["message_markdown"]


def test_api_ask_accepts_chat_uri_field(client: TestClient):
    text = (
        "pokaż proces agenta weather-map-agent.local\n"
        "zdiagnozuj agenta invoices-agent.local"
    )
    from urish.chat_uri import build_chat_prompt_uri

    response = client.post(
        "/api/ask",
        json={"uri": build_chat_prompt_uri("tellmesh", text), "dry_run": True, "llm": False},
    )
    assert response.status_code == 200
    payload = response.json()
    data = payload["data"]
    assert data["batch"] is True
    assert len(data["actions"]) == 2
    assert data["chat"]["app"] == "tellmesh"
    assert data["chat_uri"].startswith("chat://tellmesh/prompt")
    assert "view://process/agent/weather-map-agent.local/latest" in payload["message_markdown"]
    assert "repair://agent/invoices-agent.local/diagnose" in payload["message_markdown"]


def test_api_ask_accepts_chat_uri_as_prompt(client: TestClient):
    from urish.chat_uri import build_chat_prompt_uri

    response = client.post(
        "/api/ask",
        json={"prompt": build_chat_prompt_uri("tellmesh", "pokaż health agenta user-agent.local")},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["data"]["chat"]["app"] == "tellmesh"
    assert "health://agent/user-agent.local" in payload["data"]["planned_uris"]


def test_api_uri_call_chat_prompt(client: TestClient):
    from urish.chat_uri import build_chat_prompt_uri

    text = (
        "pokaż proces agenta weather-map-agent.local\n"
        "zdiagnozuj agenta invoices-agent.local"
    )
    response = client.post(
        "/api/uri/call",
        json={
            "uri": build_chat_prompt_uri("tellmesh", text, mime_type="text/plain"),
            "dry_run": True,
            "approved": False,
            "policy": "dev",
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["result_type"] == "ask"
    assert payload["data"]["batch"] is True
    assert "Detected 2 commands" in payload["message_markdown"]


def test_api_ask_requires_prompt_or_uri(client: TestClient):
    response = client.post("/api/ask", json={"dry_run": True})
    assert response.status_code == 400
    assert "prompt or uri" in response.json()["detail"]


def test_api_ask_accepts_nl_uri(client: TestClient):
    from urish.nl_uri import build_nl_uri

    text = (
        "pokaż proces agenta weather-map-agent.local\n"
        "zdiagnozuj agenta invoices-agent.local"
    )
    response = client.post(
        "/api/ask",
        json={"uri": build_nl_uri(text), "dry_run": True, "llm": False},
    )
    assert response.status_code == 200
    payload = response.json()
    data = payload["data"]
    assert data["batch"] is True
    assert len(data["actions"]) == 2
    assert data["nl"]["target"] == "ask"
    assert data["nl_uri"].startswith("nl://ask?")


def test_api_uri_call_nl_uri_plans(client: TestClient):
    from urish.nl_uri import build_nl_uri

    response = client.post(
        "/api/uri/call",
        json={
            "uri": build_nl_uri("pokaż health agenta user-agent.local"),
            "dry_run": True,
            "approved": False,
            "policy": "dev",
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["result_type"] == "ask"
    assert "health://agent/user-agent.local" in payload["data"]["planned_uris"]
    assert "health://agent/user-agent.local" in payload["message_markdown"]


def test_api_uri_call_dry_run_preview_markdown(client: TestClient):
    response = client.post(
        "/api/uri/call",
        json={"uri": "domain://test", "dry_run": True, "approved": False, "policy": "dev"},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["result_type"] == "dry_run"
    assert "URI: preview" in payload["message_markdown"]
    assert "URI: failed" not in payload["message_markdown"]


def test_api_uri_call_repair_dry_run_is_preview(client: TestClient):
    response = client.post(
        "/api/uri/call",
        json={
            "uri": "repair://agent/weather-map-agent.local/apply",
            "dry_run": True,
            "approved": False,
            "policy": "dev",
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["ok"] is True
    assert payload["result_type"] == "repair"
    assert payload["workflow_status"] == "planned"
    assert payload["service_result_status"] == "preview"
    assert "URI: preview" in payload["message_markdown"]
    assert "URI: failed" not in payload["message_markdown"]


def test_api_uri_call_physical_operator_dry_run_is_preview(client: TestClient):
    response = client.post(
        "/api/uri/call",
        json={
            "uri": "robot://robot/amr-1/mission/patrol/start",
            "dry_run": True,
            "approved": False,
            "policy": "dev",
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["ok"] is True
    assert payload["workflow_status"] == "planned"
    assert payload["service_result_status"] == "preview"
    assert "URI: preview" in payload["message_markdown"]
    assert "URI: failed" not in payload["message_markdown"]


def test_root_redirects_to_www(client: TestClient):
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 302
    assert response.headers["location"] == "/www/"


def test_www_index_served(client: TestClient):
    response = client.get("/www/")
    assert response.status_code == 200
    assert "TellMesh" in response.text
    assert "Text2Ops" in response.text
    assert "scenario-tabs" in response.text
    assert "demo-terminal" in response.text
    assert 'id="deploy-gate"' in response.text
    assert "contract://agent/weather-map-agent" in response.text
    assert 'id="control-plane"' in response.text


def test_www_index_integrations_section(client: TestClient):
    response = client.get("/www/")
    assert response.status_code == 200
    text = response.text
    assert 'id="integracje"' in text
    assert 'data-integration-card="woocommerce-connector"' in text
    assert "Baselinker" in text


def test_www_index_office_examples(client: TestClient):
    response = client.get("/www/")
    assert response.status_code == 200
    text = response.text
    assert 'id="demo"' in text
    assert "Office day" in text
    assert "workflow://office/day-marta/dry-run" in text
    assert "android://" in text
    assert "bank_token.android.yaml" in text
    assert 'href="#demo"' in text


def test_www_examples_gallery(client: TestClient):
    response = client.get("/www/przyklady.html")
    assert response.status_code == 200
    text = response.text
    assert "Tested integrations" in text
    assert "examples-gallery.js" in text
    assert "examples-grid" in text
    assert "test-all-examples.sh" in text
    assert "office-chains" in text


def test_www_examples_docs_page(client: TestClient):
    response = client.get("/www/docs/examples.html")
    assert response.status_code == 200
    text = response.text
    assert "Examples documentation" in text
    assert 'id="overview"' in text
    assert 'id="ex-10_browser_operator"' in text
    assert 'id="ex-23_nl_to_agent_tutorial"' in text
    assert "android://device" in text
    assert "docs-examples.js" in text


def test_build_examples_docs_script(repo_root: Path):
    script = repo_root / "scripts" / "www" / "build_examples_docs.py"
    out = repo_root / "www" / "docs" / "examples.html"
    result = subprocess.run(
        [sys.executable, str(script), "--check"],
        cwd=repo_root,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr or result.stdout
    assert out.is_file()


def test_examples_docs_link_check(repo_root: Path):
    script = repo_root / "scripts" / "www" / "check_examples_links.py"
    result = subprocess.run(
        [sys.executable, str(script)],
        cwd=repo_root,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr or result.stdout


def test_www_index_links_examples_gallery(client: TestClient):
    response = client.get("/www/")
    assert response.status_code == 200
    assert 'href="przyklady.html"' in response.text
    assert 'href="docs/examples.html"' in response.text


def test_api_ask_office_invoice_batch(client: TestClient):
    response = client.post(
        "/api/ask",
        json={"prompt": "wystaw faktury za wczoraj i pokaż podgląd przed wysyłką"},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["ok"] is True
    assert payload["data"]["detected_kind"] == "office"
    assert "workflow://invoices/batch/dry-run" in payload["message_markdown"]


def test_readme_links_docs_todo_changelog(repo_root: Path):
    readme = (repo_root / "README.md").read_text(encoding="utf-8")
    assert "docs/README.md" in readme
    assert "examples/README.md" in readme
    assert "TODO.md" in readme
    assert "CHANGELOG.md" in readme
    assert "www/docs/examples.html" in readme
    assert "www/przyklady.html" in readme


def test_www_chat_served(client: TestClient):
    response = client.get("/www/chat.html")
    assert response.status_code == 200
    assert "TellMesh Chat" in response.text
    assert "quick-prompts" in response.text
    assert "agent-list" in response.text
    assert "copy-chat-btn" in response.text
    assert "Copy chat" in response.text
    assert "clear-chat-btn" in response.text
    assert "Clear" in response.text
    assert 'src="app.js?v=' in response.text
    assert "chat-flow-view.js" in response.text
    assert "flow-chat.css" in response.text
    assert "view-split-btn" in response.text
    assert "flow-panel" in response.text
    assert "mic-btn" in response.text
    assert "voice-engine" in response.text
    assert "speak-summary" in response.text
    assert "flow-chat.html" in response.text


def test_www_flow_chat_served(client: TestClient):
    response = client.get("/www/flow-chat.html")
    assert response.status_code == 200
    assert "TellMesh Flow Chat" in response.text
    assert "chat-flow-view.js" in response.text
    assert "flow-chat.js" in response.text
    assert "compact-yaml" in response.text
    assert "Load demo session" in response.text


def test_www_chat_flow_view_module(repo_root: Path):
    script = (repo_root / "www" / "chat-flow-view.js").read_text(encoding="utf-8")
    assert "data.actions" in script
    assert "plannerTurnFromAsk" in script
    assert "executorTurnFromCall" in script
    assert "manifest.uri_graph" in script


def test_www_chat_js_guards_stale_and_duplicate_actions(repo_root: Path):
    script = (repo_root / "www" / "app.js").read_text(encoding="utf-8")
    assert "const INTRO_MARKDOWN" in script
    assert "pokaż proces agenta weather-map-agent.local" in script
    assert "zdiagnozuj agenta invoices-agent.local" in script
    assert "let isBusy = false" in script
    assert "function resetConversation()" in script
    assert 'document.getElementById("clear-chat-btn")' in script
    assert 'event.key === "Enter" && (event.ctrlKey || event.metaKey)' in script
    assert "Run real" in script
    assert "Run plan (dry-run)" in script
    assert "appendPlanActions" in script
    assert "TaskinityFlowView" in script
    assert "setChatView" in script
    assert "recordFlowPlanner" in script
    assert "startEventStream" in script
    assert "toggleVoiceCapture" in script
    assert "speak-summary" in script
    assert "auto_repair: true" in script
    assert "speak_summary" in script
    assert "maybeSpeakAssistantReply" in script


def test_www_landing_has_tour_copy(client: TestClient):
    response = client.get("/www/")
    assert response.status_code == 200
    assert "Kopiuj URI" in response.text
    assert 'href="chat.html"' in response.text or 'href="/www/chat.html"' in response.text
    assert 'href="flow-chat.html"' in response.text or 'href="/www/flow-chat.html"' in response.text


def test_www_landing_js_explains_repair_loop(repo_root: Path):
    legacy = repo_root / "www" / "index.legacy.html"
    script = (repo_root / "www" / "landing.js").read_text(encoding="utf-8")
    assert legacy.is_file()
    assert "buildSlideRepair" in script
    assert "SCENARIOS" in script
    assert "scenario-replay" in script
    assert "setSystemMapFocus" in script
    assert "failSafeTimer" in script
    assert "RUNTIME_STATE_STALE" in script
    assert "hypervisor supervise user-agent.local --repair auto" in script
    index = (repo_root / "www" / "index.html").read_text(encoding="utf-8")
    assert "repair" in index.lower()
    assert "contract://agent/weather-map-agent" in index


def test_www_compose_mounts_system_artifacts(repo_root: Path):
    compose = yaml.safe_load((repo_root / "www" / "docker-compose.yml").read_text())
    service = compose["services"]["www-chat"]
    volumes = service["volumes"]
    assert service["network_mode"] == "host"
    assert service["pid"] == "host"
    assert "../agents/generated:/app/agents/generated" in volumes
    assert "../contracts:/app/contracts" in volumes
    assert "../deployments:/app/deployments" in volumes
    assert "../knowledge:/app/knowledge:ro" in volumes
    assert "../output:/app/output" in volumes


def test_www_dockerfile_includes_generated_agents_and_repair_cases(repo_root: Path):
    dockerfile = (repo_root / "www" / "Dockerfile").read_text()
    assert "COPY agents ./agents" in dockerfile
    assert "COPY examples ./examples" in dockerfile
    assert "COPY knowledge ./knowledge" in dockerfile
    assert "output/runtime/agents" in dockerfile


def test_api_events_returns_typed_feed(client: TestClient):
    response = client.get("/api/events?limit=5")
    assert response.status_code == 200
    payload = response.json()
    assert payload["source"] == "hypervisor.events"
    assert isinstance(payload["events"], list)


def test_api_events_stream_contract(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(
        "hypervisor_dashboard_agent.routes.collect_system_events",
        lambda **kwargs: [
            {
                "id": "event-1",
                "type": "agent.health",
                "ts": "2026-06-14T12:00:00Z",
                "summary": "healthy",
            }
        ],
    )
    response = asyncio.run(api_events_stream(limit=1, interval_s=2))

    assert response.media_type == "text/event-stream"
    first_chunk = asyncio.run(asyncio.wait_for(response.body_iterator.__anext__(), timeout=1))
    text = first_chunk.decode() if isinstance(first_chunk, bytes) else first_chunk
    assert text.startswith("data: ")
    assert '"source": "hypervisor.events.stream"' in text
    assert '"type": "agent.health"' in text


def test_api_plan_run_dry_run(client: TestClient):
    uri = "health://agent/user-agent.local"
    response = client.post(
        "/api/plan/run",
        json={
            "planned_uris": [uri],
            "dry_run": True,
            "approved": False,
            "policy": "dev",
            "auto_repair": True,
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["result_type"] == "plan_run"
    assert payload["count"] >= 1
    assert payload["results"][0]["uri"] == uri
    assert uri in payload["message_markdown"]
    assert payload["auto_repair"] is True


def test_api_plan_run_speak_summary(client: TestClient):
    response = client.post(
        "/api/plan/run",
        json={
            "planned_uris": ["health://agent/user-agent.local"],
            "dry_run": True,
            "speak_summary": True,
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["speech"]["ok"] is True
    assert "Plan zakończony" in payload["speech"]["text"]


def test_api_voice_speak_mock(client: TestClient):
    response = client.post(
        "/api/voice/speak",
        json={"text": "Plan gotowy", "voice": "mock", "play": True},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["ok"] is True
    assert payload["speech"]


def test_api_voice_transcribe_mock(client: TestClient):
    response = client.post(
        "/api/voice/transcribe",
        json={"engine": "mock", "text": "zdiagnozuj agenta user-agent.local"},
    )
    assert response.status_code == 200
    payload = response.json()
    assert "user-agent" in payload["transcript"]["text"]

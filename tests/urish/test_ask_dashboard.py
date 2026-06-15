"""Tests for urish ask intent and dashboard workflow."""

from __future__ import annotations

from pathlib import Path

from urish.backends.ask import ask_prompt
from urish.intent import detect_intent


def test_detect_dashboard_agent_intent():
    intent = detect_intent(
        "stwórz aplikację web UI jako agenta do pokazywania procesów hypervisora"
    )
    assert intent["kind"] == "ecosystem"
    assert intent["subtype"] == "dashboard-agent"
    assert intent["ecosystem_id"] == "hypervisor-dashboard"
    assert intent["profile"] == "dashboard-agent"


def test_detect_agent_process_view_intent():
    intent = detect_intent("pokaż proces agenta weather-map-agent.local")
    assert intent["kind"] == "agent"
    assert intent["subtype"] == "process_view"
    assert intent["deployment_id"] == "weather-map-agent.local"
    assert intent["uri"] == "view://process/agent/weather-map-agent.local/latest"


def test_detect_agent_diagnose_intent():
    intent = detect_intent("zdiagnozuj agenta invoices-agent.local")
    assert intent["kind"] == "agent"
    assert intent["subtype"] == "diagnose"
    assert intent["deployment_id"] == "invoices-agent.local"
    assert intent["uri"] == "repair://agent/invoices-agent.local/diagnose"


def test_detect_agent_health_intent():
    intent = detect_intent("pokaż health agenta user-agent.local")
    assert intent["kind"] == "agent"
    assert intent["subtype"] == "health"
    assert intent["uri"] == "health://agent/user-agent.local"


def test_ask_agent_process_view_plans_hypervisor_uri():
    result = ask_prompt("pokaż proces agenta weather-map-agent.local")
    data = result["data"]
    assert data["detected_kind"] == "agent"
    assert data["detected_subtype"] == "process_view"
    assert data["planned_uris"] == ["view://process/agent/weather-map-agent.local/latest"]
    assert any("inspect-agent weather-map-agent.local" in step for step in data["next_steps"])


def test_ask_agent_diagnose_plans_repair_uri():
    result = ask_prompt("zdiagnozuj agenta weather-map-agent.local i pokaż plan naprawy")
    data = result["data"]
    assert data["detected_kind"] == "agent"
    assert data["detected_subtype"] == "diagnose"
    assert data["planned_uris"] == ["repair://agent/weather-map-agent.local/diagnose"]


def test_screenshot_prompt_uses_workflow_not_domain():
    intent = detect_intent(
        "rob rzuty ekranów stron softreck.com prototypowanie.pl www "
        "co 5 minut do folderu usera ~/images/"
    )
    assert intent["kind"] == "workflow"


def test_screenshot_prompt_plans_stable_workflow_uri():
    prompt = (
        "rob rzuty ekranów stron softreck.com prototypowanie.pl www "
        "co 5 minut do folderu usera ~/images/"
    )
    result = ask_prompt(prompt)
    data = result["data"]
    assert data["detected_kind"] == "workflow"
    assert data["planned_uris"] == ["workflow://graph/website-screenshot-schedule/dry-run"]
    generated = data["generated"]
    assert generated["flow"]["id"] == "website-screenshot-schedule"
    assert "softreck.com" in generated["flow"]["sites"][0]
    assert generated["flow"]["schedule_minutes"] == 5
    assert generated["flow"]["output_dir"] == "~/images/"


def test_screenshot_polish_inflection_detects_workflow():
    intent = detect_intent("zaplanuj harmonogram screenshotów strony co 5 minut dry-run")
    assert intent["kind"] == "workflow"
    result = ask_prompt("zaplanuj harmonogram screenshotów strony co 5 minut dry-run")
    assert result["data"]["planned_uris"] == ["workflow://graph/website-screenshot-schedule/dry-run"]


def test_weather_forecast_prompt_plans_weather_uri():
    prompt = "prognoza pogody Gdańsk 7 dni"
    intent = detect_intent(prompt)
    assert intent["kind"] == "weather"
    assert intent["uri"] == "weather://forecast/Gdansk/7/html"
    result = ask_prompt(prompt)
    data = result["data"]
    assert data["detected_kind"] == "weather"
    assert data["planned_uris"] == ["weather://forecast/Gdansk/7/html"]
    assert "domain://" not in data["planned_uris"][0]


def test_detect_www_chat_dashboard_intent_without_agent_word():
    intent = detect_intent(
        "stwórz prosty web UI hypervisora jako chat markdown połączony z API systemu"
    )
    assert intent["kind"] == "ecosystem"
    assert intent["subtype"] == "dashboard-agent"
    assert intent["ecosystem_id"] == "hypervisor-dashboard"


def test_ask_dashboard_includes_generate_and_semantic_id():
    result = ask_prompt("stwórz aplikację web UI jako agenta do pokazywania procesów hypervisora")
    data = result["data"]
    assert data["detected_kind"] == "ecosystem"
    assert data["detected_subtype"] == "dashboard-agent"
    assert data["ecosystem_id"] == "hypervisor-dashboard"
    assert data["profile"] == "dashboard-agent"
    assert any("urish ecosystem generate" in step for step in data["next_steps"])
    assert any("hypervisor-dashboard" in step for step in data["next_steps"])
    assert any("agent run hypervisor-dashboard.local" in step for step in data["next_steps"])
    assert any(uri.startswith("view://") for uri in data["planned_uris"])
    assert data["generated"]["proposal"]["id"] == "hypervisor-dashboard"


def test_plan_ecosystem_dashboard_profile():
    from urigen.proposal import plan_ecosystem

    proposal = plan_ecosystem(
        "dashboard hypervisor processes",
        profile="dashboard-agent",
        ecosystem_id="hypervisor-dashboard",
    )
    assert proposal["proposal"]["profile"] == "dashboard-agent"
    assert proposal["intent"]["agents"] == ["hypervisor-dashboard"]
    assert "view.process.agent" in proposal["intent"]["capabilities"]


def test_dashboard_ecosystem_generate_verify(tmp_path: Path):
    from urigen.generator import generate_ecosystem
    from urigen.io import load_yaml, write_yaml
    from urigen.proposal import plan_ecosystem
    from urigen.verify import verify_ecosystem

    proposal = plan_ecosystem(
        "stwórz web UI agenta hypervisor-dashboard do pokazywania procesów",
        profile="dashboard-agent",
        ecosystem_id="hypervisor-dashboard",
    )
    proposal_path = write_yaml(tmp_path / "proposal.yaml", proposal)
    generated = generate_ecosystem(proposal_path, out=tmp_path / "ecosystem")
    assert generated["ok"] is True

    process_manifest = load_yaml(
        tmp_path / "ecosystem" / "capabilities" / "process_view.uri.capability.yaml"
    )
    assert process_manifest["backend"]["type"] == "http"
    assert process_manifest["backend"]["url"].endswith("/api/view/process/agent/{agent_id}")

    ecosystem = load_yaml(tmp_path / "ecosystem" / "ecosystem.yaml")
    assert ecosystem["applications"][0]["source"] == "app"
    assert ecosystem["applications"][0]["entrypoint"] == "hypervisor_dashboard_agent.main:app"
    assert (tmp_path / "ecosystem" / "app" / "pyproject.toml").is_file()
    assert (
        tmp_path / "ecosystem" / "app" / "hypervisor_dashboard_agent" / "main.py"
    ).is_file()
    assert not any("__pycache__" in item for item in generated["files"])
    assert not any(".egg-info" in item for item in generated["files"])

    verification = verify_ecosystem(tmp_path / "ecosystem" / "ecosystem.yaml")
    assert verification["ok"] is True


def test_dashboard_create_plan_only():
    from urish.backends.dashboard import create_dashboard

    result = create_dashboard("hypervisor-dashboard", plan_only=True)
    assert result["ok"] is True
    assert result["status"] == "planned"
    assert result["ecosystem_id"] == "hypervisor-dashboard"
    assert any(s["step"] == "plan" for s in result["steps"])

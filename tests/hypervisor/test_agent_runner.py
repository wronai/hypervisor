"""Tests for deployment registry agent runner."""

from __future__ import annotations

from pathlib import Path

import pytest

from hypervisor.deployment_registry.runner import (
    agent_status,
    build_run_plan,
    local_target_to_module,
    resolve_deployment,
)
from hypervisor.deployment_registry.models import AgentDeployment


def test_local_target_to_module():
    assert local_target_to_module("local://agents/generated/weather_map_agent") == (
        "agents.generated.weather_map_agent.main:app"
    )


def test_build_run_plan_for_local_deployment():
    deployment = resolve_deployment("weather-map-agent.local")
    plan = build_run_plan(deployment)
    assert plan["module"] == "agents.generated.weather_map_agent.main:app"
    assert plan["port"] == 8101
    assert "uvicorn" in plan["command"]
    assert plan["health_uri"] == "http://localhost:8101/health"
    assert plan["env"]["RESOURCE_RUNTIME_URL"] == "http://localhost:8000"


def test_build_run_plan_missing_path(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.chdir(tmp_path)
    deployment = AgentDeployment(
        id="missing.local",
        agent_ref="agent://missing",
        target_uri="local://agents/generated/missing_agent",
        health_uri="http://localhost:8109/health",
    )
    with pytest.raises(FileNotFoundError):
        build_run_plan(deployment, root=tmp_path)


def test_agent_status_without_health():
    payload = agent_status("weather-map-agent.local", check_health=False)
    assert payload["id"] == "weather-map-agent.local"
    assert payload["status"] == "generated"


def test_ssh_run_plan_via_build_run_plan():
    deployment = resolve_deployment("weather-map-agent.ssh-dev")
    plan = build_run_plan(deployment)
    assert plan["transport"] == "ssh"
    assert "remote_command" in plan


def test_ssh_target_cannot_start_without_dry_run():
    with pytest.raises(ValueError, match="SSH targets support dry-run"):
        from hypervisor.deployment_registry.runner import run_agent

        run_agent("weather-map-agent.ssh-dev", dry_run=False)

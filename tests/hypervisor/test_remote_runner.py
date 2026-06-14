"""Tests for SSH remote deployment runner."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from hypervisor.deployment_registry.models import AgentDeployment
from hypervisor.deployment_registry.remote_runner import (
    build_ssh_deploy_plan,
    build_ssh_run_plan,
    verify_remote_deployment,
)
from hypervisor.deployment_registry.runner import build_run_plan, resolve_deployment


def test_build_ssh_deploy_plan():
    deployment = resolve_deployment("weather-map-agent.ssh-dev")
    plan = build_ssh_deploy_plan(deployment)
    assert plan["local_source"].endswith("agents/generated/weather_map_agent")
    assert plan["steps"][0]["action"] == "rsync"
    assert "rsync" in plan["steps"][0]["command_string"]


def test_build_ssh_run_plan_dry_run():
    deployment = resolve_deployment("weather-map-agent.ssh-dev")
    plan = build_ssh_run_plan(deployment)
    assert plan["transport"] == "ssh"
    assert plan["module"] == "main:app"
    assert "uvicorn" in plan["remote_command"]
    assert plan["command"][0] in {"ssh", "sshpass"}


def test_build_run_plan_ssh_delegates():
    deployment = resolve_deployment("weather-map-agent.ssh-dev")
    plan = build_run_plan(deployment)
    assert plan["transport"] == "ssh"


def test_verify_remote_deployment(monkeypatch: pytest.MonkeyPatch):
    deployment = AgentDeployment(
        id="remote.ssh",
        agent_ref="agent://weather-map-agent",
        target_uri="ssh://deploy@localhost:2222/opt/agents/weather-map-agent",
        health_uri="http://localhost:8101/health",
    )

    monkeypatch.setattr(
        "hypervisor.deployment_registry.remote_runner.scan_ssh",
        lambda uri: [
            MagicMock(kind="ssh_connectivity", status="reachable", uri=uri, metadata={}),
            MagicMock(kind="remote_path", status="present", uri=uri, metadata={}),
        ],
    )
    monkeypatch.setattr(
        "hypervisor.deployment_registry.remote_runner.scan_http",
        lambda uri: [MagicMock(kind="health", status="ok", uri=uri, metadata={"status_code": 200})],
    )
    payload = verify_remote_deployment(deployment)
    assert payload["verified"] is True
    assert payload["ssh_ok"] is True
    assert payload["health_ok"] is True

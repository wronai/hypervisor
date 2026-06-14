"""Tests for hypervisor docker deployment runner."""

from __future__ import annotations

from hypervisor.deployment_registry.docker_runner import build_docker_deploy_plan, build_docker_control_plan
from hypervisor.deployment_registry.runner import resolve_deployment


def test_build_docker_deploy_plan():
    deployment = resolve_deployment("weather-map-agent.docker")
    plan = build_docker_deploy_plan(deployment)
    assert plan["deployment_id"] == "weather-map-agent.docker"
    assert len(plan["steps"]) == 2
    assert plan["steps"][0]["action"] == "generate"


def test_build_docker_control_plan_up():
    deployment = resolve_deployment("weather-map-agent.docker")
    plan = build_docker_control_plan(deployment, "up")
    assert plan["action"] == "up"
    assert plan["dry_run"] is True

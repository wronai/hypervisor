from __future__ import annotations

from hypervisor.deployment_registry.local_targets import (
    build_local_run_plan,
    local_target_to_module,
)
from hypervisor.deployment_registry.models import AgentDeployment, DeploymentDeclared


def test_local_run_plan_ignores_a2a_card_uri(repo_root):
    deployment = AgentDeployment(
        id="weather-map-agent.local",
        agent_ref="agent://weather-map-agent",
        target_uri="local://agents/generated/weather_map_agent",
        card_uri="a2a://weather-map-agent/.well-known/agent-card.json",
        status="generated",
    )
    plan = build_local_run_plan(deployment, repo=repo_root, port=8101)
    assert plan["health_uri"] == "http://localhost:8101/health"
    assert plan["card_uri"] == "http://localhost:8101/.well-known/agent-card.json"


def test_local_run_plan_prefers_declared_http_endpoints(repo_root):
    deployment = AgentDeployment(
        id="weather-map-agent.local",
        agent_ref="agent://weather-map-agent",
        target_uri="local://agents/generated/weather_map_agent",
        card_uri="a2a://weather-map-agent/.well-known/agent-card.json",
        declared=DeploymentDeclared(
            target_uri="local://agents/generated/weather_map_agent",
            preferred_port=8101,
            health_uri="http://localhost:8101/health",
            card_uri="http://localhost:8101/.well-known/agent-card.json",
        ),
        status="generated",
    )
    plan = build_local_run_plan(deployment, repo=repo_root)
    assert plan["health_uri"] == "http://localhost:8101/health"
    assert plan["card_uri"] == "http://localhost:8101/.well-known/agent-card.json"


def test_local_target_to_module_custom_agent():
    assert (
        local_target_to_module("local://agents/custom/screenshot_analysis_agent")
        == "agents.custom.screenshot_analysis_agent.main:app"
    )


def test_local_run_plan_custom_agent(repo_root):
    deployment = AgentDeployment(
        id="screenshot-analysis-agent.local",
        agent_ref="agent://screenshot-analysis-agent",
        target_uri="local://agents/custom/screenshot_analysis_agent",
        status="generated",
    )
    plan = build_local_run_plan(deployment, repo=repo_root, port=8134)
    assert plan["module"] == "agents.custom.screenshot_analysis_agent.main:app"
    assert plan["health_uri"] == "http://localhost:8134/health"

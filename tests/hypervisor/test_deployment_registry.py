"""Deployment registry tests."""

from __future__ import annotations

from pathlib import Path

import yaml

from hypervisor.deployment_registry import (
    get_deployment_for_agent,
    load_deployment_registry,
    resolve_status,
    sync_from_uri_tree,
    upsert_deployment,
)
from hypervisor.deployment_registry.loader import default_registry_path
from hypervisor.deployment_registry.models import AgentDeployment
from hypervisor.deployment_registry.status import deployment_from_uri_tree, registry_summary
from hypervisor.deployment_registry.writer import save_deployment_registry
from nl2uri.domain_planner import plan_from_prompt


def test_load_default_deployments():
    registry = load_deployment_registry(".")
    assert len(registry.deployments) >= 2
    weather = get_deployment_for_agent("agent://weather-map-agent", registry=registry)
    assert weather is not None
    local = registry.by_id("weather-map-agent.local")
    assert local is not None
    assert local.target_uri.startswith("local://")
    assert registry.by_id("user-agent.local") is not None
    assert registry.by_id("invoices-agent.local") is not None


def test_deployment_from_weather_uri_tree():
    tree = plan_from_prompt("generuj mape pogody dwa tygodnie do przodu w html", use_llm=False)
    deployment = deployment_from_uri_tree(tree)
    assert deployment is not None
    assert deployment.id == "weather-map-agent.local"
    assert deployment.agent_ref == "agent://weather-map-agent"
    assert deployment.health_uri == "http://localhost:8101/health"


def test_sync_from_uri_tree_writes_registry(tmp_path: Path):
    tree = plan_from_prompt("generuj mape pogody dwa tygodnie do przodu w html", use_llm=False)
    registry_path = tmp_path / "deployments" / "agent_deployments.yaml"
    deployment = sync_from_uri_tree(tree, root=tmp_path, path=registry_path)
    assert deployment is not None
    assert registry_path.exists()
    loaded = load_deployment_registry(tmp_path, path=registry_path)
    assert loaded.by_id("weather-map-agent.local") is not None


def test_sync_from_uri_tree_preserves_existing_http_endpoints(tmp_path: Path):
    registry_path = tmp_path / "deployments" / "agent_deployments.yaml"
    registry_path.parent.mkdir(parents=True, exist_ok=True)
    registry_path.write_text(
        yaml.safe_dump(
            {
                "deployments": [
                    {
                        "id": "weather-map-agent.local",
                        "agent_ref": "agent://weather-map-agent",
                        "target_uri": "local://agents/generated/weather_map_agent",
                        "status": "generated",
                        "health_uri": "http://localhost:8101/health",
                        "card_uri": "http://localhost:8101/.well-known/agent-card.json",
                        "metadata": {
                            "source": "uri_tree",
                            "contract": "contracts/agents/weather_map_agent.yaml",
                        },
                    }
                ]
            },
            sort_keys=False,
        ),
        encoding="utf-8",
    )
    tree = plan_from_prompt("generuj mape pogody dwa tygodnie do przodu w html", use_llm=False)
    deployment = sync_from_uri_tree(tree, root=tmp_path, path=registry_path)
    assert deployment is not None
    assert deployment.health_uri == "http://localhost:8101/health"
    assert deployment.card_uri == "http://localhost:8101/.well-known/agent-card.json"
    assert deployment.metadata.get("contract") == "contracts/agents/weather_map_agent.yaml"


def test_upsert_replaces_existing_deployment(tmp_path: Path):
    registry_path = default_registry_path(tmp_path)
    registry = load_deployment_registry(tmp_path, path=registry_path)
    updated = AgentDeployment(
        id="weather-map-agent.local",
        agent_ref="agent://weather-map-agent",
        target_uri="local://agents/generated/weather_map_agent",
        status="deployed",
    )
    upsert_deployment(registry, updated)
    save_deployment_registry(registry)
    reloaded = load_deployment_registry(tmp_path, path=registry_path)
    assert reloaded.by_id("weather-map-agent.local").status == "deployed"


def test_resolve_status_without_health_check():
    deployment = AgentDeployment(
        id="demo.local",
        agent_ref="agent://demo",
        target_uri="local://agents/generated/demo",
        status="generated",
    )
    assert resolve_status(deployment, check_health=False) == "generated"


def test_registry_summary():
    registry = load_deployment_registry(".")
    summary = registry_summary(registry)
    assert summary
    assert {"id", "agent_ref", "target_uri", "status"}.issubset(summary[0].keys())


def test_ssh_target_uri_supported_in_model(tmp_path: Path):
    registry_path = default_registry_path(tmp_path)
    registry = load_deployment_registry(tmp_path, path=registry_path)
    remote = AgentDeployment(
        id="weather-map-agent.remote",
        agent_ref="agent://weather-map-agent",
        target_uri="ssh://dev.example.com/opt/agents/weather_map_agent",
        status="generated",
    )
    upsert_deployment(registry, remote)
    save_deployment_registry(registry)
    raw = yaml.safe_load(registry_path.read_text(encoding="utf-8"))
    assert any(item["target_uri"].startswith("ssh://") for item in raw["deployments"])

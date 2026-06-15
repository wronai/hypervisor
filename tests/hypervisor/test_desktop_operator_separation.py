from __future__ import annotations

from pathlib import Path

import yaml


def _load_desktop_operator(repo_root: Path) -> dict:
    path = repo_root / "agents/operators/desktop_operator.yaml"
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def test_desktop_operator_contract_is_generic_capability_agent(repo_root: Path):
    spec = _load_desktop_operator(repo_root)

    assert spec["kind"] == "hypervisor.operator_agent"
    assert spec["metadata"]["agent_ref"] == "agent://desktop-operator"
    assert spec["metadata"]["runtime_package"] == "agents/operators/desktop_operator"
    assert spec["domain_boundary"]["owns_domain_logic"] is False
    assert spec["domain_boundary"]["owns_execution"] is True

    schemes = {capability["scheme"] for capability in spec["capabilities"]}
    assert {"screen", "input", "pcwin", "android"} <= schemes
    assert "browser" not in schemes

    runtime = spec["runtime"]
    assert runtime["deployment_id"] == "desktop-operator.local"
    assert runtime["health_uri"].endswith(":8791/health")
    assert runtime["card_uri"].endswith(":8791/.well-known/agent-card.json")
    assert runtime["a2a_tasks_uri"].endswith(":8791/a2a/tasks")
    assert runtime["mcp_tools_uri"].endswith(":8791/mcp/tools")


def test_desktop_operator_does_not_embed_domain_vocabulary(repo_root: Path):
    path = repo_root / "agents/operators/desktop_operator.yaml"
    source = path.read_text(encoding="utf-8").lower()
    forbidden = [
        "office",
        "invoice",
        "invoices",
        "bank",
        "zus",
        "subiekt",
        "woocommerce",
        "baselinker",
        "allegro",
        "supplier",
    ]

    for needle in forbidden:
        assert needle not in source


def test_domain_registry_uses_operator_uris_without_owning_operator_contract(repo_root: Path):
    registry_path = repo_root / "domains/office/scenario_registry.yaml"
    registry = yaml.safe_load(registry_path.read_text(encoding="utf-8"))

    planned = "\n".join(
        uri
        for uris in registry.get("uri_templates", {}).values()
        for uri in uris
    )
    assert "browser://" in planned
    assert "pcwin://" in planned
    assert "android://" in planned

    serialized = yaml.safe_dump(registry, sort_keys=True)
    assert "agents/operators/desktop_operator.yaml" not in serialized
    assert "agent://desktop-operator" not in serialized


def test_desktop_operator_is_registered_as_package_agent(repo_root: Path):
    from hypervisor.deployment_registry.runner import build_run_plan, local_target_to_module, resolve_deployment

    deployment = resolve_deployment("desktop-operator.local", root=repo_root)
    assert deployment.agent_ref == "agent://desktop-operator"
    assert deployment.target_uri == "local://agents/operators/desktop_operator"
    assert deployment.metadata["source"] == "operator_agent"
    assert deployment.metadata["contract"] == "agents/operators/desktop_operator/desktop_operator.yaml"

    assert local_target_to_module(deployment.target_uri) == "agents.operators.desktop_operator.main:app"
    plan = build_run_plan(deployment, root=repo_root)
    assert plan["module"] == "agents.operators.desktop_operator.main:app"
    assert plan["port"] == 8791
    assert plan["health_uri"] == "http://localhost:8791/health"
    assert plan["card_uri"] == "http://localhost:8791/.well-known/agent-card.json"

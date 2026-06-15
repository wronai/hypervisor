from __future__ import annotations

from pathlib import Path

import yaml


def _load_browser_operator(repo_root: Path) -> dict:
    path = repo_root / "agents/operators/browser_operator.yaml"
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def test_browser_operator_contract_is_generic_capability_agent(repo_root: Path):
    spec = _load_browser_operator(repo_root)

    assert spec["kind"] == "hypervisor.operator_agent"
    assert spec["metadata"]["agent_ref"] == "agent://browser-operator"
    assert spec["metadata"]["runtime_package"] == "agents/operators/browser_operator"
    assert spec["metadata"]["capability_domain"] == "domains/browser_ops"
    assert spec["domain_boundary"]["owns_domain_logic"] is False
    assert spec["domain_boundary"]["owns_execution"] is True

    schemes = {capability["scheme"] for capability in spec["capabilities"]}
    assert schemes == {"browser"}

    runtime = spec["runtime"]
    assert runtime["deployment_id"] == "browser-operator.local"
    assert runtime["health_uri"].endswith(":8793/health")
    assert runtime["card_uri"].endswith(":8793/.well-known/agent-card.json")
    assert runtime["mcp_call_uri"].endswith(":8793/mcp/tools/call")


def test_browser_domain_registry_uses_operator_uris(repo_root: Path):
    registry_path = repo_root / "domains/browser_ops/scenario_registry.yaml"
    registry = yaml.safe_load(registry_path.read_text(encoding="utf-8"))

    planned = "\n".join(
        uri
        for uris in registry.get("uri_templates", {}).values()
        for uri in uris
    )
    assert "browser://" in planned
    assert "pcwin://" not in planned
    assert "android://" not in planned

    serialized = yaml.safe_dump(registry.get("scenarios") or [], sort_keys=True)
    assert "agents/operators/browser_operator.yaml" not in serialized
    assert "agent://browser-operator" not in serialized


def test_browser_operator_is_registered_as_package_agent(repo_root: Path):
    from hypervisor.deployment_registry.runner import build_run_plan, local_target_to_module, resolve_deployment

    deployment = resolve_deployment("browser-operator.local", root=repo_root)
    assert deployment.agent_ref == "agent://browser-operator"
    assert deployment.target_uri == "local://agents/operators/browser_operator"
    assert deployment.metadata["source"] == "operator_agent"
    assert deployment.metadata["role"] == "browser_operator"
    assert deployment.metadata["contract"] == "agents/operators/browser_operator/browser_operator.yaml"

    assert local_target_to_module(deployment.target_uri) == "agents.operators.browser_operator.main:app"
    plan = build_run_plan(deployment, root=repo_root)
    assert plan["module"] == "agents.operators.browser_operator.main:app"
    assert plan["port"] == 8793
    assert plan["health_uri"] == "http://localhost:8793/health"

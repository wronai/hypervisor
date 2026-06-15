from __future__ import annotations

from pathlib import Path

import yaml


def _load_operator(repo_root: Path) -> dict:
    path = repo_root / "agents/operators/device_robot_operator.yaml"
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def test_device_robot_operator_contract_is_generic_capability_agent(repo_root: Path):
    spec = _load_operator(repo_root)

    assert spec["kind"] == "hypervisor.operator_agent"
    assert spec["metadata"]["agent_ref"] == "agent://device-robot-operator"
    assert spec["metadata"]["runtime_package"] == "agents/operators/device_robot_operator"
    assert spec["metadata"]["capability_domain"] == "domains/physical_ops"
    assert spec["domain_boundary"]["owns_domain_logic"] is False
    assert spec["domain_boundary"]["owns_execution"] is True

    schemes = {capability["scheme"] for capability in spec["capabilities"]}
    assert {"robot", "device"} <= schemes

    runtime = spec["runtime"]
    assert runtime["deployment_id"] == "device-robot-operator.local"
    assert runtime["health_uri"].endswith(":8792/health")
    assert runtime["card_uri"].endswith(":8792/.well-known/agent-card.json")
    assert runtime["a2a_tasks_uri"].endswith(":8792/a2a/tasks")


def test_physical_domain_registry_uses_operator_uris(repo_root: Path):
    registry_path = repo_root / "domains/physical_ops/scenario_registry.yaml"
    registry = yaml.safe_load(registry_path.read_text(encoding="utf-8"))

    planned = "\n".join(
        uri
        for uris in registry.get("uri_templates", {}).values()
        for uri in uris
    )
    assert "robot://" in planned
    assert "device://" in planned
    assert "human://operator/safety/approve" in planned

    serialized_scenarios = yaml.safe_dump(registry.get("scenarios") or [], sort_keys=True)
    assert "agents/operators/device_robot_operator.yaml" not in serialized_scenarios
    assert "agent://device-robot-operator" not in serialized_scenarios


def test_device_robot_operator_is_registered_as_package_agent(repo_root: Path):
    from hypervisor.deployment_registry.runner import (
        build_run_plan,
        local_target_to_module,
        resolve_deployment,
    )

    deployment = resolve_deployment("device-robot-operator.local", root=repo_root)
    assert deployment.agent_ref == "agent://device-robot-operator"
    assert deployment.target_uri == "local://agents/operators/device_robot_operator"
    assert deployment.metadata["source"] == "operator_agent"
    assert deployment.metadata["contract"] == "agents/operators/device_robot_operator/device_robot_operator.yaml"

    assert local_target_to_module(deployment.target_uri) == "agents.operators.device_robot_operator.main:app"
    plan = build_run_plan(deployment, root=repo_root)
    assert plan["module"] == "agents.operators.device_robot_operator.main:app"
    assert plan["port"] == 8792
    assert plan["health_uri"] == "http://localhost:8792/health"
    assert plan["card_uri"] == "http://localhost:8792/.well-known/agent-card.json"

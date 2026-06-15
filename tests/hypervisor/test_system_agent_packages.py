"""System agent packages — deployment entry under agents/system/."""

from __future__ import annotations

from pathlib import Path

import yaml


def test_hypervisor_dashboard_is_registered_as_system_agent(repo_root: Path):
    from hypervisor.deployment_registry.runner import build_run_plan, local_target_to_module, resolve_deployment

    deployment = resolve_deployment("hypervisor-dashboard.local", root=repo_root)
    assert deployment.agent_ref == "agent://hypervisor-dashboard"
    assert deployment.target_uri == "local://agents/system/hypervisor_dashboard"
    assert deployment.metadata["source"] == "system_agent"
    assert deployment.metadata["contract"] == "agents/system/hypervisor_dashboard/hypervisor_dashboard.yaml"

    assert local_target_to_module(deployment.target_uri) == "agents.system.hypervisor_dashboard.main:app"
    plan = build_run_plan(deployment, root=repo_root)
    assert plan["module"] == "agents.system.hypervisor_dashboard.main:app"
    assert plan["path"].endswith("agents/system/hypervisor_dashboard")


def test_hypervisor_dashboard_contract_symlink(repo_root: Path):
    contract = repo_root / "agents/system/hypervisor_dashboard/hypervisor_dashboard.yaml"
    assert contract.is_symlink()
    assert contract.resolve().samefile(
        repo_root / "contracts/agents/hypervisor_dashboard_agent.yaml"
    )


def test_hypervisor_dashboard_app_loads():
    from agents.system.hypervisor_dashboard.main import app

    assert app.title == "hypervisor-dashboard"


def test_runtime_environments_lists_system_dashboard(repo_root: Path):
    config = yaml.safe_load(
        (repo_root / "config/runtime_environments.yaml").read_text(encoding="utf-8")
    )
    dashboard = config["control_plane"]["hypervisor-dashboard.local"]
    assert dashboard["runtime_package"] == "agents/system/hypervisor_dashboard"
    assert "agents.system.hypervisor_dashboard.main:app" in dashboard["launch"]["direct"]

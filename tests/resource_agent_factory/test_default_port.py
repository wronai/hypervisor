from __future__ import annotations

from generator.agent_generator import _default_port_for_agent
from generator.model import load_agent_spec


def test_default_port_from_deployment_registry(repo_root):
    spec = load_agent_spec(repo_root / "contracts/agents/invoices_agent.yaml")
    assert _default_port_for_agent(spec, repo_root) == 8123


def test_default_port_falls_back_to_8101(repo_root, tmp_path):
    spec = load_agent_spec(repo_root / "contracts/agents/invoices_agent.yaml")
    assert _default_port_for_agent(spec, tmp_path) == 8101

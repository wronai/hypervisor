"""Hypervisor configuration tests."""

from __future__ import annotations

from pathlib import Path

import pytest

from hypervisor.config import (
    HypervisorConfig,
    get_default_config,
    load_config,
    load_hypervisor_config,
    validate_config,
)


def test_default_config_has_structured_sections():
    cfg = get_default_config()
    assert cfg["hypervisor"]["max_agents"] == 8
    assert cfg["llm"]["model_uri"].startswith("llm://")
    assert "env" in cfg["uri3"]["enabled_schemes"]
    assert cfg["registry"]["path"] == "contracts/registry.yaml"
    assert cfg["domain_pack"]["root"] == "domains/"
    assert cfg["agents"]["generated_root"] == "agents/generated/"
    assert cfg["deployment"]["registry"] == "deployments/agent_deployments.yaml"


def test_load_config_merges_user_file(tmp_path: Path):
    user_cfg = tmp_path / "nlp2uri.yaml"
    user_cfg.write_text(
        """
platform: linux
hypervisor:
  max_agents: 4
  default_profile: fast
registry:
  output: output/custom_registry.json
""",
        encoding="utf-8",
    )
    cfg = load_config(user_cfg)
    assert cfg["platform"] == "linux"
    assert cfg["hypervisor"]["max_agents"] == 4
    assert cfg["hypervisor"]["default_profile"] == "fast"
    assert cfg["registry"]["output"] == "output/custom_registry.json"
    assert cfg["llm"]["provider"] == "openrouter"
    assert "_config_path" in cfg


def test_env_overrides(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("HYPERVISOR_MAX_AGENTS", "16")
    monkeypatch.setenv("HYPERVISOR_REGISTRY_OUTPUT", "output/from_env.json")
    monkeypatch.setenv("HYPERVISOR_LLM_MODEL_URI", "llm://openrouter/custom/model")
    cfg = load_config("/nonexistent/path.yaml")
    assert cfg["hypervisor"]["max_agents"] == "16"
    assert cfg["registry"]["output"] == "output/from_env.json"
    assert cfg["llm"]["model_uri"] == "llm://openrouter/custom/model"


def test_validate_config_reports_invalid_profile():
    errors = validate_config({"hypervisor": {"default_profile": "turbo", "max_agents": 0}})
    assert any("default_profile" in error for error in errors)
    assert any("max_agents" in error for error in errors)


def test_load_hypervisor_config_model():
    model = load_hypervisor_config("/nonexistent/path.yaml")
    assert isinstance(model, HypervisorConfig)
    assert model.hypervisor.max_agents == 8
    assert model.registry.output.endswith("contract_registry.resolved.json")
    roundtrip = model.to_dict()
    assert roundtrip["deployment"]["registry"] == "deployments/agent_deployments.yaml"


def test_load_config_merges_llm_uri_yaml():
    cfg = load_config()
    assert str(cfg["llm"].get("uri_config", "")).endswith("config/llm.uri.yaml")
    assert cfg["llm"]["model"].startswith("llm://")
    assert cfg["llm"]["api_key"].startswith("env://")
    assert "domain_planner" in cfg["llm"]["uri_profiles"]

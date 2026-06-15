from __future__ import annotations

from pathlib import Path

import yaml


def _load_yaml(repo_root: Path, relpath: str) -> dict:
    return yaml.safe_load((repo_root / relpath).read_text(encoding="utf-8"))


def test_browser_ops_domain_declares_operator_boundary(repo_root: Path):
    spec = _load_yaml(repo_root, "domains/browser_ops/domain.yaml")

    assert spec["kind"] == "taskinity.domain_pack"
    assert spec["metadata"]["id"] == "browser_ops"
    assert spec["boundary"]["operator_agent"] == "agent://browser-operator"
    assert spec["boundary"]["deployment_id"] == "browser-operator.local"
    assert spec["schemes"] == ["browser"]
    assert "browser.open" in spec["policy"]["enforcement"]["mutation_operations"]


def test_browser_ops_operator_registry_matches_uri2ops_capabilities(repo_root: Path):
    registry = _load_yaml(repo_root, "domains/browser_ops/operator_registry.yaml")

    assert registry["runtime"]["agent_ref"] == "agent://browser-operator"
    assert registry["runtime"]["deployment_id"] == "browser-operator.local"
    cards = {card["id"]: card for card in registry["cards"]}
    assert set(cards) == {"browser"}
    assert cards["browser"]["adapters"] == ["mock", "playwright", "auto"]


def test_browser_ops_scenario_registry_is_loaded_and_routable(repo_root: Path):
    from urish.intent import detect_intent
    from urish.scenario_registry import clear_scenario_registry_cache, load_scenario_registries

    clear_scenario_registry_cache()
    registries = load_scenario_registries()
    sources = {registry["metadata"]["source"] for registry in registries}
    assert "domains/browser_ops/scenario_registry.yaml" in sources

    intent = detect_intent("sprawdz browser operator i pokaz stan runtime")
    assert intent["kind"] == "browser_ops"
    assert intent["subtype"] == "browser_status"
    assert "health://agent/browser-operator.local" in intent["planned_uris"]


def test_browser_operator_points_to_browser_ops_without_owning_scenarios(repo_root: Path):
    spec = _load_yaml(repo_root, "agents/operators/browser_operator.yaml")
    contracts = spec["contracts"]

    assert contracts["domain_pack"] == "domains/browser_ops/domain.yaml"
    assert contracts["operator_registry"] == "domains/browser_ops/operator_registry.yaml"
    assert contracts["scenario_registry"] == "domains/browser_ops/scenario_registry.yaml"

from __future__ import annotations

from pathlib import Path

import yaml


def _load_yaml(repo_root: Path, relpath: str) -> dict:
    return yaml.safe_load((repo_root / relpath).read_text(encoding="utf-8"))


def test_desktop_ops_domain_declares_operator_boundary(repo_root: Path):
    spec = _load_yaml(repo_root, "domains/desktop_ops/domain.yaml")

    assert spec["kind"] == "taskinity.domain_pack"
    assert spec["metadata"]["id"] == "desktop_ops"
    assert spec["boundary"]["control_plane"] == "hypervisor"
    assert spec["boundary"]["nl_router"] == "urish"
    assert spec["boundary"]["workflow_runner"] == "uri3"
    assert spec["boundary"]["execution_runtime"] == "uri2ops"
    assert spec["boundary"]["operator_agent"] == "agent://desktop-operator"
    assert spec["boundary"]["deployment_id"] == "desktop-operator.local"

    assert spec["contracts"]["operator_agent"] == "agents/operators/desktop_operator.yaml"
    assert spec["contracts"]["operator_registry"] == "domains/desktop_ops/operator_registry.yaml"
    assert spec["contracts"]["scenario_registry"] == "domains/desktop_ops/scenario_registry.yaml"
    assert {"browser", "screen", "input", "pcwin", "android"} <= set(spec["schemes"])
    assert spec["policy"]["enforcement"]["policy_module"] == "packages/urish/urish/policy.py"
    assert "browser.open" in spec["policy"]["enforcement"]["mutation_operations"]
    assert "screen.observe" in spec["policy"]["enforcement"]["read_operations"]
    assert {"dry_run", "approve"} <= set(spec["policy"]["enforcement"]["mutation_requires"])


def test_desktop_ops_operator_registry_matches_uri2ops_capabilities(repo_root: Path):
    registry = _load_yaml(repo_root, "domains/desktop_ops/operator_registry.yaml")

    assert registry["kind"] == "taskinity.operator_registry"
    assert registry["runtime"]["agent_ref"] == "agent://desktop-operator"
    assert registry["runtime"]["deployment_id"] == "desktop-operator.local"
    assert registry["runtime"]["package"] == "uri2ops"

    cards = {card["id"]: card for card in registry["cards"]}
    assert {"browser", "screen", "input", "pcwin", "android"} <= set(cards)

    operation_uris = {
        operation["uri"]
        for card in cards.values()
        for operation in card.get("operations", [])
    }
    assert "browser://chrome/page/open" in operation_uris
    assert "pcwin://window/{id}/focus" in operation_uris
    assert "android://device/{id}/screenshot" in operation_uris

    for card in cards.values():
        assert card["adapter_boundary"] == "packages/uri2ops"


def test_desktop_ops_scenario_registry_is_loaded_and_routable(repo_root: Path):
    from urish.intent import detect_intent
    from urish.scenario_registry import clear_scenario_registry_cache, load_scenario_registries

    clear_scenario_registry_cache()
    registries = load_scenario_registries()
    sources = {registry["metadata"]["source"] for registry in registries}
    assert "domains/desktop_ops/scenario_registry.yaml" in sources

    intent = detect_intent("sprawdz desktop operator i pokaz stan runtime")
    assert intent["kind"] == "desktop_ops"
    assert intent["subtype"] == "desktop_status"
    assert intent["registry_source"] == "domains/desktop_ops/scenario_registry.yaml"
    assert "health://agent/desktop-operator.local" in intent["planned_uris"]
    assert "agents/operators/desktop_operator.yaml" in intent["artifacts"]["contracts"]


def test_desktop_ops_does_not_embed_vertical_scenarios(repo_root: Path):
    paths = [
        repo_root / "domains/desktop_ops/domain.yaml",
        repo_root / "domains/desktop_ops/operator_registry.yaml",
        repo_root / "domains/desktop_ops/scenario_registry.yaml",
    ]
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

    for path in paths:
        source = path.read_text(encoding="utf-8").lower()
        for needle in forbidden:
            assert needle not in source, f"{path} embeds vertical term {needle!r}"


def test_desktop_operator_points_to_desktop_ops_without_owning_scenarios(repo_root: Path):
    spec = _load_yaml(repo_root, "agents/operators/desktop_operator.yaml")
    contracts = spec["contracts"]

    assert contracts["domain_pack"] == "domains/desktop_ops/domain.yaml"
    assert contracts["operator_registry"] == "domains/desktop_ops/operator_registry.yaml"
    assert contracts["scenario_registry"] == "domains/desktop_ops/scenario_registry.yaml"
    assert spec["domain_boundary"]["owns_domain_logic"] is False
    assert spec["domain_boundary"]["owns_routing"] is False
    assert spec["domain_boundary"]["owns_execution"] is True

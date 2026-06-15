from __future__ import annotations

from pathlib import Path

from hypervisor.deployment_registry.aliases import load_deployment_selector_aliases
from hypervisor.deployment_registry.selector import resolve_deployment


def test_load_weather_agent_alias_from_domain_fragment(repo_root: Path):
    aliases = load_deployment_selector_aliases(str(repo_root))
    assert aliases["weather-agent"] == "weather-map-agent.local"


def test_resolve_local_weather_agent_alias(repo_root: Path):
    deployment = resolve_deployment("weather-agent", root=repo_root, prefer_local=True)
    assert deployment.id == "weather-map-agent.local"


def test_weather_map_fragment_declares_alias(repo_root: Path):
    fragment = repo_root / "domains" / "weather_map" / "registry.fragment.yaml"
    text = fragment.read_text(encoding="utf-8")
    assert "weather-agent" in text
    assert "weather-map-agent.local" in text

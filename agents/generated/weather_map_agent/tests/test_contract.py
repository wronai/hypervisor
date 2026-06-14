# AUTO-GENERATED FILE. DO NOT EDIT.
# Source: /mnt/data/resource_agent_hypervisor_v0_4/contracts/agents/weather_map_agent.yaml
# Contract hash: sha256:47b69e7e4fc1b3b3e56e5778021526be07db596966aac1362c0782a766ca2485

from agents.generated.weather_map_agent.agent_card import AGENT_CARD


def test_agent_card_has_expected_name():
    assert AGENT_CARD["name"] == "weather-map-agent"


def test_agent_card_has_capabilities():
    names = {cap["name"] for cap in AGENT_CARD["capabilities"]}
    assert names == ["read_weather_map", "generate_weather_map"]


def test_agent_card_has_contract_hash():
    assert AGENT_CARD["generated_from"]["contract_hash"] == "sha256:47b69e7e4fc1b3b3e56e5778021526be07db596966aac1362c0782a766ca2485"
# AUTO-GENERATED FILE. DO NOT EDIT.
# Source: contracts/agents/gnome_programmer_agent.yaml
# Contract hash: sha256:7b1bcba0139f125676c81df01f1bc3a4296937cf3a4ee3f06fcd7ff9efd0943e

from agents.generated.gnome_programmer_agent.agent_card import AGENT_CARD


def test_agent_card_has_expected_name():
    assert AGENT_CARD["name"] == "gnome-programmer-agent"


def test_agent_card_has_capabilities():
    names = [cap["name"] for cap in AGENT_CARD["capabilities"]]
    assert names == ["observe_desktop", "type_on_desktop", "programmer_session"]


def test_agent_card_has_contract_hash():
    assert AGENT_CARD["generated_from"]["contract_hash"] == (
        "sha256:7b1bcba0139f125676c81df01f1bc3a4296937cf3a4ee3f06fcd7ff9efd0943e"
    )

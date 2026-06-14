# AUTO-GENERATED FILE. DO NOT EDIT.
# Source: contracts/agents/user_agent.yaml
# Contract hash: sha256:740801960691f1c4aefee04d0cc5a7e27aa3a9915ef2eb73a729f9226a10ce45

from agents.generated.user_agent.agent_card import AGENT_CARD


def test_agent_card_has_expected_name():
    assert AGENT_CARD["name"] == "user-agent"


def test_agent_card_has_capabilities():
    names = {cap["name"] for cap in AGENT_CARD["capabilities"]}
    assert names == ["read_user", "read_user_roles", "create_user", "assign_user_role"]


def test_agent_card_has_contract_hash():
    assert AGENT_CARD["generated_from"]["contract_hash"] == "sha256:740801960691f1c4aefee04d0cc5a7e27aa3a9915ef2eb73a729f9226a10ce45"
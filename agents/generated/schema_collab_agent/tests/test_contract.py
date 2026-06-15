# AUTO-GENERATED FILE. DO NOT EDIT.
# Source: contracts/agents/schema_collab_agent.yaml
# Contract hash: sha256:17b3d806a8ebef60fa04b5234c2f32ccc2b94d7745234e05cbbd5c7e51bb4bd3

from agents.generated.schema_collab_agent.agent_card import AGENT_CARD


def test_agent_card_has_expected_name():
    assert AGENT_CARD["name"] == "schema-collab-agent"


def test_agent_card_has_capabilities():
    names = [cap["name"] for cap in AGENT_CARD["capabilities"]]
    assert names == ["read_markpact_source", "read_device_status", "read_robot_state", "run_cron_monitor"]


def test_agent_card_has_contract_hash():
    assert AGENT_CARD["generated_from"]["contract_hash"] == (
        "sha256:17b3d806a8ebef60fa04b5234c2f32ccc2b94d7745234e05cbbd5c7e51bb4bd3"
    )

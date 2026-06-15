# AUTO-GENERATED FILE. DO NOT EDIT.
# Source: contracts/agents/codex_nl_plan_agent.yaml
# Contract hash: sha256:2d9bc1c0b851ce7acae3b9134afc15449ddc5fe881c3fdb439c4077b9df4c699

from agents.generated.codex_nl_plan_agent.agent_card import AGENT_CARD


def test_agent_card_has_expected_name():
    assert AGENT_CARD["name"] == "codex-nl-plan-agent"


def test_agent_card_has_capabilities():
    names = [cap["name"] for cap in AGENT_CARD["capabilities"]]
    assert names == ["read_markpact_source", "read_device_status", "run_cron_monitor"]


def test_agent_card_has_contract_hash():
    assert AGENT_CARD["generated_from"]["contract_hash"] == (
        "sha256:2d9bc1c0b851ce7acae3b9134afc15449ddc5fe881c3fdb439c4077b9df4c699"
    )

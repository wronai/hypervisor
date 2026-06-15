# AUTO-GENERATED FILE. DO NOT EDIT.
# Source: contracts/agents/codex_uri_smoke_agent.yaml
# Contract hash: sha256:92e4d835ecacc5e7138946e5012d5948102fc79fd492458ffb981bd857372c38

from agents.generated.codex_uri_smoke_agent.agent_card import AGENT_CARD


def test_agent_card_has_expected_name():
    assert AGENT_CARD["name"] == "codex-uri-smoke-agent"


def test_agent_card_has_capabilities():
    names = [cap["name"] for cap in AGENT_CARD["capabilities"]]
    assert names == ["read_markpact_source", "read_device_status", "run_cron_monitor"]


def test_agent_card_has_contract_hash():
    assert AGENT_CARD["generated_from"]["contract_hash"] == (
        "sha256:92e4d835ecacc5e7138946e5012d5948102fc79fd492458ffb981bd857372c38"
    )

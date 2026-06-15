# AUTO-GENERATED FILE. DO NOT EDIT.
# Source: contracts/agents/codex_nl_smoke_agent.yaml
# Contract hash: sha256:1e2da71bd316b85b830c1a1f69f333c7e5ac2b01e83258383005f0967dde488c

from agents.generated.codex_nl_smoke_agent.agent_card import AGENT_CARD


def test_agent_card_has_expected_name():
    assert AGENT_CARD["name"] == "codex-nl-smoke-agent"


def test_agent_card_has_capabilities():
    names = [cap["name"] for cap in AGENT_CARD["capabilities"]]
    assert names == ["read_markpact_source", "read_device_status", "run_cron_monitor"]


def test_agent_card_has_contract_hash():
    assert AGENT_CARD["generated_from"]["contract_hash"] == (
        "sha256:1e2da71bd316b85b830c1a1f69f333c7e5ac2b01e83258383005f0967dde488c"
    )

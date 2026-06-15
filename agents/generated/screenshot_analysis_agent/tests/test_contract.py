# AUTO-GENERATED FILE. DO NOT EDIT.
# Source: contracts/agents/screenshot_analysis_agent.yaml
# Contract hash: sha256:a541c061b26d8303d14f931b3ad48dea9ada37990cc1a9426d2c1c0a13fbc77e

from agents.generated.screenshot_analysis_agent.agent_card import AGENT_CARD


def test_agent_card_has_expected_name():
    assert AGENT_CARD["name"] == "screenshot-analysis-agent"


def test_agent_card_has_capabilities():
    names = [cap["name"] for cap in AGENT_CARD["capabilities"]]
    assert names == ["analyze_screenshot", "capture_and_analyze", "scheduled_capture_analysis"]


def test_agent_card_has_contract_hash():
    assert AGENT_CARD["generated_from"]["contract_hash"] == (
        "sha256:a541c061b26d8303d14f931b3ad48dea9ada37990cc1a9426d2c1c0a13fbc77e"
    )

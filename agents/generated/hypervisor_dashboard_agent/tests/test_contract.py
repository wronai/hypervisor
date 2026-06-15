# AUTO-GENERATED FILE. DO NOT EDIT.
# Source: contracts/agents/hypervisor_dashboard_agent.yaml
# Contract hash: sha256:e4ec619a25955f0c7cfe29270e603cf7256c7840417f77ca63fd48173bda14b5

from agents.generated.hypervisor_dashboard_agent.agent_card import AGENT_CARD


def test_agent_card_has_expected_name():
    assert AGENT_CARD["name"] == "hypervisor-dashboard"


def test_agent_card_has_capabilities():
    names = [cap["name"] for cap in AGENT_CARD["capabilities"]]
    assert names == ["process_view", "workflow_timeline", "incident_explain", "repair_diagnose", "repair_action", "uri_call"]


def test_agent_card_has_contract_hash():
    assert AGENT_CARD["generated_from"]["contract_hash"] == (
        "sha256:e4ec619a25955f0c7cfe29270e603cf7256c7840417f77ca63fd48173bda14b5"
    )

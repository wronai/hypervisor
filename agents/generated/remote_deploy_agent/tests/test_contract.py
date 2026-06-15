# AUTO-GENERATED FILE. DO NOT EDIT.
# Source: contracts/agents/remote_deploy_agent.yaml
# Contract hash: sha256:cb604273489ae8add7f97a4cad7786e18f628fcb1528369b992e7e437be6846e

from agents.generated.remote_deploy_agent.agent_card import AGENT_CARD


def test_agent_card_has_expected_name():
    assert AGENT_CARD["name"] == "remote-deploy-agent"


def test_agent_card_has_capabilities():
    names = [cap["name"] for cap in AGENT_CARD["capabilities"]]
    assert names == ["plan_remote_deploy", "apply_remote_deploy", "verify_remote_agent", "start_remote_agent", "deploy_verify_start"]


def test_agent_card_has_contract_hash():
    assert AGENT_CARD["generated_from"]["contract_hash"] == (
        "sha256:cb604273489ae8add7f97a4cad7786e18f628fcb1528369b992e7e437be6846e"
    )

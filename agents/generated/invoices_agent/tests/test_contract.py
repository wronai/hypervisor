# AUTO-GENERATED FILE. DO NOT EDIT.
# Source: contracts/agents/invoices_agent.yaml
# Contract hash: sha256:a536397207b68bed66eefb1defcfb80529b8d2aa4fe82645f2ffa38069c60960

from agents.generated.invoices_agent.agent_card import AGENT_CARD


def test_agent_card_has_expected_name():
    assert AGENT_CARD["name"] == "invoices-agent"


def test_agent_card_has_capabilities():
    names = [cap["name"] for cap in AGENT_CARD["capabilities"]]
    assert names == ["read_invoice", "read_invoice_events", "create_invoice"]


def test_agent_card_has_contract_hash():
    assert AGENT_CARD["generated_from"]["contract_hash"] == (
        "sha256:a536397207b68bed66eefb1defcfb80529b8d2aa4fe82645f2ffa38069c60960"
    )

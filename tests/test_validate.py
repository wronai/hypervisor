from pathlib import Path

from generator.validate import validate_agent


def test_user_agent_contract_is_valid():
    errors = validate_agent(Path("contracts/agents/user_agent.yaml"))
    assert errors == []

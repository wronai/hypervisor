from pathlib import Path

from generator.agent_generator import generate_agent


def test_generate_user_agent():
    output_dir = generate_agent(Path("contracts/agents/user_agent.yaml"))
    assert (output_dir / "main.py").exists()
    assert (output_dir / "routes.py").exists()
    assert (output_dir / "agent_card.py").exists()

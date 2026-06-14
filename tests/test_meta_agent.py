from pathlib import Path

import yaml

from generator.validate import validate_agent
from meta_agent.orchestrator import pipeline_from_prompt, save_proposal_from_prompt
from meta_agent.repair import repair_agent_spec


def test_save_proposal_from_prompt(tmp_path: Path):
    path = tmp_path / "orders_agent.yaml"
    result = save_proposal_from_prompt("Stwórz agenta do obsługi zamówień z odczytem i tworzeniem", path)
    data = yaml.safe_load(result.read_text(encoding="utf-8"))
    assert data["agent"]["name"] == "orders-agent"
    assert any(cap["type"] == "resource_read" for cap in data["capabilities"])
    assert validate_agent(result) == []


def test_repair_broken_agent(tmp_path: Path):
    broken = tmp_path / "broken_agent.yaml"
    broken.write_text(
        """
agent:
  name: broken-agent
capabilities:
  - name: read_thing
    type: resource_read
    uri: resource://things/{thing_id}
  - name: read_thing
    type: resource_read
    uri: resource://things/{thing_id}/events
  - name: create_thing
    type: command
""".strip(),
        encoding="utf-8",
    )
    before = validate_agent(broken)
    assert before
    result = repair_agent_spec(broken, write=True)
    assert result.changed
    assert result.errors_after == []
    repaired = yaml.safe_load(broken.read_text(encoding="utf-8"))
    names = [cap["name"] for cap in repaired["capabilities"]]
    assert len(names) == len(set(names))


def test_pipeline_from_prompt_generates_agent(tmp_path: Path):
    spec_path = Path("contracts/agents/test_orders_agent.yaml")
    generated_path = Path("agents/generated/orders_agent")
    try:
        result = pipeline_from_prompt(
            "Stwórz agenta do obsługi zamówień z odczytem zamówienia, historią i tworzeniem zamówienia",
            output_path=spec_path,
        )
        assert result.status == "generated"
        assert generated_path.exists()
        assert (generated_path / "main.py").exists()
    finally:
        spec_path.unlink(missing_ok=True)
        if generated_path.exists():
            import shutil
            shutil.rmtree(generated_path)

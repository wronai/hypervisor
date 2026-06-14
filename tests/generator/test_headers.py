"""Generated agent header tests."""

from __future__ import annotations

from pathlib import Path

import yaml

from generator.agent_generator import generate_agent
from generator.header import AUTO_GENERATED_MARKER, contract_source_ref
from generator.verify import verify_generated, verify_generated_agent


def test_generated_python_files_have_standard_header(tmp_path: Path, monkeypatch):
    monkeypatch.setattr("generator.agent_generator.ROOT", tmp_path)
    spec = tmp_path / "contracts" / "agents" / "demo_agent.yaml"
    spec.parent.mkdir(parents=True)
    spec.write_text(
        """
agent:
  name: demo-agent
  python_package: demo_agent
  version: 0.1.0
  description: Demo agent
capabilities:
  - name: run
    type: command
    command: Run
    input_schema: app.demo.v1.RunCommand
""".strip(),
        encoding="utf-8",
    )
    output_root = tmp_path / "agents" / "generated"
    output_dir = generate_agent(spec, output_root=output_root)

    for relative in ("main.py", "routes.py", "agent_card.py", "__init__.py", "tests/test_contract.py"):
        text = (output_dir / relative).read_text(encoding="utf-8")
        assert text.startswith(f"# {AUTO_GENERATED_MARKER}")
        assert "# Source: contracts/agents/demo_agent.yaml" in text
        assert "# Contract hash: sha256:" in text

    marker = yaml.safe_load((output_dir / ".generated.yaml").read_text(encoding="utf-8"))
    assert marker["auto_generated"] == "true"
    assert marker["source"] == "contracts/agents/demo_agent.yaml"
    assert marker["generator"] == "resource-agent-factory"
    assert verify_generated_agent(output_dir) == []


def test_contract_source_ref_is_repo_relative():
    root = Path(__file__).resolve().parents[2]
    spec = root / "contracts" / "agents" / "user_agent.yaml"
    assert contract_source_ref(spec, root) == "contracts/agents/user_agent.yaml"


def test_verify_generated_ignores_pycache(tmp_path: Path, monkeypatch):
    monkeypatch.setattr("generator.agent_generator.ROOT", tmp_path)
    spec = tmp_path / "contracts" / "agents" / "demo_agent.yaml"
    spec.parent.mkdir(parents=True)
    spec.write_text(
        """
agent:
  name: demo-agent
  python_package: demo_agent
  version: 0.1.0
  description: Demo agent
capabilities:
  - name: run
    type: command
    command: Run
    input_schema: app.demo.v1.RunCommand
""".strip(),
        encoding="utf-8",
    )
    output_root = tmp_path / "agents" / "generated"
    generate_agent(spec, output_root=output_root)
    (output_root / "__pycache__").mkdir()
    assert verify_generated(output_root) == []

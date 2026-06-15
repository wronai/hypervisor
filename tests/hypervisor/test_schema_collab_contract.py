from __future__ import annotations

from pathlib import Path

from hypervisor.contract_registry.cross_validator import validate_root


def test_schema_collab_contract_cross_refs(repo_root: Path):
    errors = validate_root(repo_root)
    assert errors == []


def test_operator_robot_state_proto_exists(repo_root: Path):
    proto_text = (repo_root / "contracts/proto/operator.proto").read_text(encoding="utf-8")
    assert "message RobotState" in proto_text

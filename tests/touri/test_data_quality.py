"""Tests for touri data_quality validation."""

from __future__ import annotations

from pathlib import Path

import yaml

from touri.executor import call_uri


def _write_capability(tmp_path: Path, manifest: dict) -> Path:
    path = tmp_path / "demo.uri.capability.yaml"
    path.write_text(yaml.safe_dump(manifest, sort_keys=False), encoding="utf-8")
    return tmp_path


def test_data_quality_validator_rejects_low_confidence(tmp_path: Path):
    manifest = {
        "version": 1,
        "capability": {
            "id": "demo.low_confidence",
            "scheme": "demo",
            "uri_template": "demo://check/{name}",
            "operation": "read",
            "kind": "query",
        },
        "backend": {
            "type": "python",
            "target": "python://touri_examples.validators:low_confidence_backend",
        },
        "data_quality": {
            "failure_code": "PRICE_RESULT_NOT_RELEVANT",
            "validators": ["python://touri_examples.validators:reject_low_confidence"],
        },
    }
    registry = _write_capability(tmp_path, manifest)
    result = call_uri("demo://check/item", registry)
    payload = result.to_dict()
    assert payload["ok"] is False
    assert payload["service_result_status"] == "failed"
    assert payload["errors"][0]["code"] == "PRICE_RESULT_NOT_RELEVANT"


def test_touri_call_includes_status_envelope(repo_root: Path):
    result = call_uri("echo://Adam", repo_root / "examples" / "20_touri_capabilities")
    payload = result.to_dict()
    assert payload["execution_status"] == "completed"
    assert payload["service_result_status"] == "succeeded"

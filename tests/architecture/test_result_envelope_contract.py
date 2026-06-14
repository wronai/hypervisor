"""Architecture: ServiceResult envelope consistency across runtimes."""

from __future__ import annotations

from pathlib import Path

import yaml
from touri.executor import call_uri
from uri3.graph import run_workflow

from tests.architecture.envelope_helpers import (
    assert_service_result_shape,
    assert_workflow_result_shape,
)


def test_touri_call_envelope(repo_root: Path):
    result = call_uri("echo://Adam", repo_root / "examples" / "20_touri_capabilities")
    assert_service_result_shape(result.to_dict())


def test_touri_data_quality_failure_envelope(tmp_path: Path):
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
    path = tmp_path / "demo.uri.capability.yaml"
    path.write_text(yaml.safe_dump(manifest, sort_keys=False), encoding="utf-8")
    payload = call_uri("demo://check/item", tmp_path).to_dict()
    assert_service_result_shape(payload)
    assert payload["ok"] is False
    assert payload["execution_status"] == "completed"
    assert payload["service_result_status"] == "failed"


def test_uri3_workflow_dry_run_envelope():
    task = {
        "task": {"id": "envelope-contract", "description": "dry run"},
        "steps": [
            {
                "id": "open_health",
                "uri": "browser://chrome/page/open",
                "operation": "open",
                "kind": "command",
                "payload": {"url": "http://localhost:8101/health"},
            }
        ],
    }
    payload = run_workflow(task, dry_run=True, browser_mode="mock").to_dict()
    assert_workflow_result_shape(payload["workflow_result"])

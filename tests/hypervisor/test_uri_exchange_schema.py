"""Validate uri_exchange.schema.json against Flow Chat session shapes."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
SCHEMA_PATH = ROOT / "schemas" / "uri_exchange.schema.json"


@pytest.fixture(scope="module")
def uri_exchange_schema() -> dict:
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


def _validate(schema: dict, payload: dict) -> list[str]:
    validator = Draft202012Validator(schema)
    return sorted(f"{'.'.join(str(p) for p in error.path)}: {error.message}" for error in validator.iter_errors(payload))


def test_uri_exchange_schema_accepts_single_planner_executor(uri_exchange_schema: dict):
    payload = {
        "session_id": "demo-1",
        "turns": [
            {"role": "user", "nl": "capture example.com"},
            {
                "role": "planner",
                "kind": "command",
                "subtype": "browser-capture",
                "uris": ["workflow://graph/website-screenshot-schedule/dry-run"],
            },
            {
                "role": "executor",
                "uri": "workflow://graph/website-screenshot-schedule/dry-run",
                "ok": True,
                "result_type": "plan",
                "workflow_steps": [
                    {
                        "id": "capture-home",
                        "uri": "browser://chrome/page/capture",
                        "payload": {"url": "https://example.com"},
                    }
                ],
            },
        ],
        "compact_flow": "flow:\n  id: tellmesh-session\n",
    }
    assert _validate(uri_exchange_schema, payload) == []


def test_uri_exchange_schema_accepts_batch_planner(uri_exchange_schema: dict):
    payload = {
        "session_id": "batch-1",
        "turns": [
            {"role": "user", "nl": "line one\nline two"},
            {
                "role": "planner",
                "batch": True,
                "plans": [
                    {"kind": "query", "uris": ["health://agent/user-agent.local"], "nl": "line one"},
                    {"kind": "command", "uris": ["repair://agent/user-agent.local/diagnose"], "nl": "line two"},
                ],
            },
        ],
    }
    assert _validate(uri_exchange_schema, payload) == []


def test_uri_exchange_schema_rejects_missing_session_id(uri_exchange_schema: dict):
    errors = _validate(uri_exchange_schema, {"turns": []})
    assert errors

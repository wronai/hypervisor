"""Tests for uri2run transport matrix."""

from __future__ import annotations

from pathlib import Path

import httpx
from touri.executor import call_uri
from uri2run import run_backend

from tests.architecture.envelope_helpers import assert_service_result_shape


def test_python_transport():
    result = run_backend(
        {"type": "python", "target": "python://touri_examples.weather:handler"},
        {"place": "Gdansk", "days": 14},
        {},
    )
    payload = result.to_dict()
    assert_service_result_shape(payload)
    assert payload["ok"] is True
    assert payload["meta"]["transport"] == "python"
    assert payload["meta"]["runtime"] == "uri2run"


def test_shell_transport_success():
    result = run_backend({"type": "shell", "command": "echo uri2run-ok"}, {}, {})
    payload = result.to_dict()
    assert payload["ok"] is True
    assert "uri2run-ok" in str(payload["data"]["stdout"])
    assert payload["meta"]["transport"] == "shell"
    assert payload["meta"]["runtime"] == "uri2run"


def test_shell_transport_failure():
    result = run_backend({"type": "shell", "command": "exit 7"}, {}, {})
    payload = result.to_dict()
    assert payload["ok"] is False
    assert payload["data"]["returncode"] == 7


def test_http_transport_success(monkeypatch):
    class FakeResponse:
        status_code = 200
        headers = {"content-type": "application/json"}

        def json(self):
            return {"status": "ok"}

    def fake_request(method, target, **kwargs):
        return FakeResponse()

    monkeypatch.setattr("uri2run.transports.http_transport.httpx.request", fake_request)
    result = run_backend({"type": "http", "url": "http://testserver/health"}, {}, {})
    payload = result.to_dict()
    assert payload["ok"] is True
    assert payload["meta"]["runtime"] == "uri2run"
    assert payload["meta"]["transport"] == "http"
    assert "duration_ms" in payload["meta"]
    assert payload["data"]["body"]["status"] == "ok"


def test_http_transport_uses_backend_options_and_retries(monkeypatch):
    calls: list[dict] = []

    class FakeResponse:
        status_code = 201
        headers = {"content-type": "application/json"}

        def json(self):
            return {"created": True}

    def fake_request(method, target, **kwargs):
        calls.append({"method": method, "target": target, **kwargs})
        if len(calls) == 1:
            raise httpx.ConnectError("temporary")
        return FakeResponse()

    monkeypatch.setattr("uri2run.transports.http_transport.httpx.request", fake_request)
    result = run_backend(
        {
            "type": "http",
            "url": "http://testserver/items",
            "method": "post",
            "headers": {"X-Test": "1"},
            "retries": 1,
        },
        {"json": {"name": "demo"}},
        {},
    )
    payload = result.to_dict()

    assert payload["ok"] is True
    assert payload["meta"]["method"] == "POST"
    assert payload["meta"]["attempts"] == 2
    assert len(calls) == 2
    assert calls[1]["headers"] == {"X-Test": "1"}
    assert calls[1]["json"] == {"name": "demo"}


def test_shell_transport_supports_argv_without_shell():
    result = run_backend(
        {"type": "shell", "command": "printf", "argv": ["printf"], "shell": False},
        {"args": ["safe"]},
        {},
    )
    payload = result.to_dict()

    assert payload["ok"] is True
    assert payload["data"]["stdout"] == "safe"
    assert payload["meta"]["shell"] is False


def test_flow_transport_dry_run(repo_root: Path):
    flow = repo_root / "examples" / "15_compact_uri_flow" / "weather.uri.flow.yaml"
    result = run_backend(
        {"type": "uri_flow", "flow": str(flow), "dry_run": True},
        {"dry_run": True},
        {"root": str(repo_root)},
    )
    payload = result.to_dict()
    assert payload["ok"] is True
    assert payload["result_type"] == "plan"
    assert payload["meta"]["transport"] == "uri_flow"


def test_touri_delegates_python_backend_to_uri2run(repo_root: Path):
    result = call_uri(
        "weather://forecast/Gdansk/14/html",
        repo_root / "examples" / "20_touri_capabilities",
    )
    payload = result.to_dict()
    assert payload["ok"] is True
    assert payload["meta"]["runtime"] == "uri2run"
    assert payload["meta"]["transport"] == "python"


def test_unsupported_transport():
    result = run_backend({"type": "grpc"}, {}, {})
    assert result.ok is False
    assert result.errors[0].code == "BACKEND_UNSUPPORTED"
    assert result.meta["runtime"] == "uri2run"
    assert result.meta["transport"] == "grpc"

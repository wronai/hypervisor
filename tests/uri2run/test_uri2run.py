from __future__ import annotations

import json
from typing import Any

from uri2run import run_backend, run_target
from uri2run.cli import main as uri2run_main
from uri3.results import service_result


def test_run_target_stt_mock_scheme():
    result = run_target("stt://mock/transcribe", payload={"text": "test"})
    payload = result.to_dict()

    assert payload["ok"] is True
    assert payload["result_type"] == "transcript"
    assert payload["data"]["text"] == "test"
    assert payload["meta"]["transport"] == "python"


def test_cli_call_stt_mock_scheme_outputs_json(capsys):
    code = uri2run_main(
        [
            "call",
            "stt://mock/transcribe",
            "--payload",
            '{"text":"cli-stt"}',
        ]
    )
    captured = capsys.readouterr()
    payload = json.loads(captured.out)

    assert code == 0
    assert payload["ok"] is True
    assert payload["data"]["text"] == "cli-stt"


def test_run_target_python_returns_service_result():
    result = run_target("python://uri2voice.stt:transcribe", payload={"text": "test"})
    payload = result.to_dict()

    assert payload["ok"] is True
    assert payload["result_type"] == "transcript"
    assert payload["data"]["text"] == "test"
    assert payload["service_result_status"] == "succeeded"


def test_run_target_shell_scheme_with_args():
    result = run_target("shell://printf", payload={"args": ["hello"]})
    payload = result.to_dict()

    assert payload["ok"] is True
    assert payload["result_type"] == "shell"
    assert payload["data"]["stdout"] == "hello"
    assert payload["data"]["returncode"] == 0


def test_run_backend_mock_returns_shared_envelope():
    result = run_backend({"type": "mock"}, {"x": 1}, {"capability": "demo"})
    payload = result.to_dict()

    assert payload["ok"] is True
    assert payload["result_type"] == "mock"
    assert payload["data"]["payload"] == {"x": 1}
    assert payload["data"]["context"]["capability"] == "demo"


def test_cli_call_python_outputs_json(capsys):
    code = uri2run_main(
        [
            "call",
            "python://uri2voice.stt:transcribe",
            "--payload",
            '{"text":"cli"}',
        ]
    )
    captured = capsys.readouterr()
    payload = json.loads(captured.out)

    assert code == 0
    assert payload["ok"] is True
    assert payload["data"]["text"] == "cli"


def test_touri_python_backend_delegates_to_uri2run(monkeypatch):
    from touri.backends import python_backend

    captured: dict[str, Any] = {}

    def fake_run_backend(
        backend: dict[str, Any],
        payload: dict[str, Any],
        context: dict[str, Any],
    ):
        captured["backend"] = backend
        captured["payload"] = payload
        captured["context"] = context
        return service_result(ok=True, result_type="fake", data={"delegated": True})

    monkeypatch.setattr(python_backend, "run_backend", fake_run_backend)

    result = python_backend.call_python_backend(
        "python://uri2voice.stt:transcribe",
        {"text": "delegated"},
        {"capability": "demo"},
    )

    assert result.ok is True
    assert captured["backend"] == {
        "type": "python",
        "target": "python://uri2voice.stt:transcribe",
    }
    assert captured["payload"] == {"text": "delegated"}
    assert captured["context"] == {"capability": "demo"}

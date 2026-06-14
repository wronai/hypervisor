"""Architecture: uri2run transport envelopes."""

from __future__ import annotations

from tests.architecture.envelope_helpers import assert_service_result_shape
from uri2run import run_backend


def test_uri2run_python_envelope():
    result = run_backend(
        {"type": "python", "target": "python://uri2voice.stt:transcribe"},
        {"text": "test"},
        {},
    ).to_dict()
    assert_service_result_shape(result)
    assert result["meta"]["runtime"] == "uri2run"
    assert result["meta"]["transport"] == "python"


def test_uri2run_shell_envelope():
    result = run_backend(
        {"type": "shell", "command": "echo"},
        {"args": ["hello"]},
        {},
    ).to_dict()
    assert_service_result_shape(result)
    assert result["meta"]["transport"] == "shell"

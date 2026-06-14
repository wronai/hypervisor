"""Architecture: uri2run transports must return standard ServiceResult envelope."""

from __future__ import annotations

from uri2run import run_backend

from tests.architecture.envelope_helpers import assert_service_result_shape


def test_uri2run_python_transport_envelope():
    result = run_backend(
        {"type": "python", "target": "python://touri_examples.weather:handler"},
        {"place": "Gdansk", "days": 14},
        {},
    )
    payload = result.to_dict()
    assert_service_result_shape(payload)
    assert payload["ok"] is True
    assert payload["execution_status"] == "completed"
    assert payload["service_result_status"] == "succeeded"
    assert payload["meta"]["runtime"] == "uri2run"
    assert payload["meta"]["transport"] == "python"


def test_uri2run_shell_transport_envelope():
    result = run_backend({"type": "shell", "command": "echo envelope-ok"}, {}, {})
    payload = result.to_dict()
    assert_service_result_shape(payload)
    assert payload["ok"] is True
    assert payload["meta"]["transport"] == "shell"


def test_uri2run_mock_transport_envelope():
    result = run_backend({"type": "mock"}, {"value": 1}, {"capability": "demo"})
    payload = result.to_dict()
    assert_service_result_shape(payload)
    assert payload["ok"] is True
    assert payload["meta"]["transport"] == "mock"


def test_uri2run_unsupported_transport_envelope():
    result = run_backend({"type": "grpc"}, {}, {})
    payload = result.to_dict()
    assert_service_result_shape(payload)
    assert payload["ok"] is False
    assert payload["service_result_status"] == "failed"
    assert payload["errors"][0]["code"] == "BACKEND_UNSUPPORTED"
    assert payload["meta"]["runtime"] == "uri2run"
    assert payload["meta"]["transport"] == "grpc"

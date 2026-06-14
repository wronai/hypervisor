from runtime_client.client import ResourceRuntimeClient


def test_runtime_client_returns_error_when_runtime_unavailable():
    client = ResourceRuntimeClient("http://127.0.0.1:9", timeout=0.1)
    result = client.read_resource("resource://users/123")
    assert result["ok"] is False
    assert result["error"] == "RESOURCE_RUNTIME_UNAVAILABLE"

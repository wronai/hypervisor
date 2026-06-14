"""Tests for uri2run docker/ssh/mcp/a2a protocol transports."""

from __future__ import annotations

from unittest.mock import MagicMock

import httpx
from uri2run import run_backend, run_target


def test_docker_transport_dry_run():
    result = run_backend(
        {"type": "docker", "target": "docker://stack/ssh-testenv?action=up&dry_run=1"},
        {},
        {"root": "."},
    )
    payload = result.to_dict()
    assert payload["ok"] is True
    assert payload["meta"]["transport"] == "docker"
    assert payload["meta"]["runtime"] == "uri2run"
    assert payload["data"]["dry_run"] is True
    assert payload["data"]["action"] == "up"


def test_run_target_docker_scheme():
    result = run_target("docker://stack/ssh-testenv?action=status&dry_run=1", {}, {"root": "."})
    assert result.ok is True
    assert result.meta.get("transport") == "docker"


def test_ssh_transport_resolve_mode():
    result = run_backend(
        {"type": "ssh", "target": "ssh://deploy@localhost:2222/opt/agents"},
        {},
        {},
    )
    payload = result.to_dict()
    assert payload["ok"] is True
    assert payload["data"]["host"] == "localhost"
    assert payload["data"]["port"] == 2222
    assert payload["meta"]["transport"] == "ssh"


def test_ssh_transport_exec_mode(monkeypatch):
    completed = MagicMock()
    completed.returncode = 0
    completed.stdout = "remote-ok"
    completed.stderr = ""

    monkeypatch.setattr(
        "uri3.resolvers.ssh_resolver.run_ssh",
        lambda ref, cmd, check=False: completed,
    )
    monkeypatch.setattr(
        "uri3.resolvers.ssh_resolver.build_ssh_command",
        lambda ref, cmd: ["ssh", ref["target"], cmd],
    )

    result = run_backend(
        {"type": "ssh", "target": "ssh://deploy@localhost:2222/opt/agents"},
        {"command": "echo remote-ok"},
        {},
    )
    payload = result.to_dict()
    assert payload["ok"] is True
    assert payload["data"]["stdout"] == "remote-ok"
    assert payload["meta"]["mode"] == "exec"


def test_mcp_transport_list_tools(monkeypatch):
    class FakeResponse:
        status_code = 200
        headers = {"content-type": "application/json"}

        def json(self):
            return {"tools": [{"name": "demo"}]}

    monkeypatch.setattr(
        "uri2run.transports.mcp_transport.httpx.request",
        lambda method, url, **kwargs: FakeResponse(),
    )
    result = run_backend(
        {"type": "mcp", "target": "mcp://localhost:8100"},
        {"action": "list_tools"},
        {},
    )
    payload = result.to_dict()
    assert payload["ok"] is True
    assert payload["data"]["method"] == "GET"
    assert payload["data"]["body"]["tools"][0]["name"] == "demo"


def test_mcp_transport_call_tool(monkeypatch):
    captured: dict = {}

    class FakeResponse:
        status_code = 200
        headers = {"content-type": "application/json"}

        def json(self):
            return {"ok": True}

    def fake_request(method, url, **kwargs):
        captured["method"] = method
        captured["url"] = url
        captured.update(kwargs)
        return FakeResponse()

    monkeypatch.setattr("uri2run.transports.mcp_transport.httpx.request", fake_request)
    result = run_backend(
        {"type": "mcp", "target": "mcp://localhost:8100"},
        {"name": "run_operator_task", "arguments": {"task": {"id": "demo"}}},
        {},
    )
    payload = result.to_dict()
    assert payload["ok"] is True
    assert captured["method"] == "POST"
    assert captured["url"].endswith("/mcp/tools/call")
    assert captured["json"]["name"] == "run_operator_task"


def test_a2a_transport_agent_card(monkeypatch):
    class FakeResponse:
        status_code = 200
        headers = {"content-type": "application/json"}

        def json(self):
            return {"name": "demo-agent"}

    monkeypatch.setattr(
        "uri2run.transports.a2a_transport.httpx.request",
        lambda method, url, **kwargs: FakeResponse(),
    )
    result = run_backend(
        {"type": "a2a", "target": "a2a://localhost:8100"},
        {"action": "agent_card"},
        {},
    )
    payload = result.to_dict()
    assert payload["ok"] is True
    assert "agent-card.json" in payload["data"]["url"]


def test_a2a_transport_tasks(monkeypatch):
    captured: dict = {}

    class FakeResponse:
        status_code = 200
        headers = {"content-type": "application/json"}

        def json(self):
            return {"ok": True}

    def fake_request(method, url, **kwargs):
        captured["method"] = method
        captured["url"] = url
        captured.update(kwargs)
        return FakeResponse()

    monkeypatch.setattr("uri2run.transports.a2a_transport.httpx.request", fake_request)
    result = run_backend(
        {"type": "a2a", "target": "a2a://localhost:8100"},
        {"task": {"id": "demo", "steps": []}},
        {},
    )
    payload = result.to_dict()
    assert payload["ok"] is True
    assert captured["method"] == "POST"
    assert captured["url"].endswith("/a2a/tasks")


def test_run_target_mcp_scheme(monkeypatch):
    class FakeResponse:
        status_code = 200
        headers = {"content-type": "application/json"}

        def json(self):
            return {"tools": []}

    monkeypatch.setattr(
        "uri2run.transports.mcp_transport.httpx.request",
        lambda method, url, **kwargs: FakeResponse(),
    )
    result = run_target("mcp://localhost:8100", {"action": "list_tools"}, {})
    assert result.ok is True


def test_mcp_transport_http_error(monkeypatch):
    def fake_request(method, url, **kwargs):
        raise httpx.ConnectError("refused")

    monkeypatch.setattr("uri2run.transports.mcp_transport.httpx.request", fake_request)
    result = run_backend(
        {"type": "mcp", "target": "mcp://localhost:8100"},
        {"action": "list_tools"},
        {},
    )
    payload = result.to_dict()
    assert payload["ok"] is False
    assert payload["errors"][0]["code"] == "MCP_TRANSPORT_FAILED"

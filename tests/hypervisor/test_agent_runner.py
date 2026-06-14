"""Tests for deployment registry agent runner."""

from __future__ import annotations

from pathlib import Path

import pytest
from hypervisor.deployment_registry.models import AgentDeployment
from hypervisor.deployment_registry.runner import (
    agent_status,
    build_run_plan,
    inspect_agent,
    local_target_to_module,
    resolve_deployment,
)


def test_local_target_to_module():
    assert local_target_to_module("local://agents/generated/weather_map_agent") == (
        "agents.generated.weather_map_agent.main:app"
    )


def test_build_run_plan_for_local_deployment():
    deployment = resolve_deployment("weather-map-agent.local")
    plan = build_run_plan(deployment)
    assert plan["module"] == "agents.generated.weather_map_agent.main:app"
    assert plan["port"] == 8101
    assert "uvicorn" in plan["command"]
    assert plan["health_uri"] == "http://localhost:8101/health"
    assert plan["env"]["RESOURCE_RUNTIME_URL"] == "http://localhost:8000"


def test_build_run_plan_with_port_override_updates_local_endpoints():
    deployment = resolve_deployment("weather-map-agent.local")
    plan = build_run_plan(deployment, port=8111)
    assert plan["port"] == 8111
    assert plan["health_uri"] == "http://localhost:8111/health"
    assert plan["card_uri"] == "http://localhost:8111/.well-known/agent-card.json"


def test_build_run_plan_missing_path(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.chdir(tmp_path)
    deployment = AgentDeployment(
        id="missing.local",
        agent_ref="agent://missing",
        target_uri="local://agents/generated/missing_agent",
        health_uri="http://localhost:8109/health",
    )
    with pytest.raises(FileNotFoundError):
        build_run_plan(deployment, root=tmp_path)


def test_agent_status_without_health():
    payload = agent_status("weather-map-agent.local", check_health=False)
    assert payload["id"] == "weather-map-agent.local"
    assert payload["status"] == "generated"


def test_ssh_run_plan_via_build_run_plan():
    deployment = resolve_deployment("weather-map-agent.ssh-dev")
    plan = build_run_plan(deployment)
    assert plan["transport"] == "ssh"
    assert "remote_command" in plan


def test_ssh_target_cannot_start_without_dry_run():
    with pytest.raises(ValueError, match="SSH targets support dry-run"):
        from hypervisor.deployment_registry.runner import run_agent

        run_agent("weather-map-agent.ssh-dev", dry_run=False)


def test_run_agent_detach_idempotent_when_already_running(monkeypatch: pytest.MonkeyPatch):
    existing = {
        "pid": 4242,
        "status": "running",
        "health_uri": "http://localhost:8101/health",
    }
    monkeypatch.setattr(
        "hypervisor.deployment_registry.lifecycle.load_runtime_state",
        lambda _deployment_id, _root=None: existing,
    )
    monkeypatch.setattr(
        "hypervisor.deployment_registry.lifecycle.is_process_alive",
        lambda pid: pid == 4242,
    )

    from hypervisor.deployment_registry.runner import run_agent

    result = run_agent("weather-map-agent.local", detach=True)
    assert result.get("already_running") is True
    assert result["pid"] == 4242
    assert result["health_uri"] == "http://localhost:8101/health"


def test_run_agent_reuse_syncs_health_uri_from_command(monkeypatch: pytest.MonkeyPatch):
    existing = {
        "pid": 4242,
        "status": "running",
        "health_uri": "http://localhost:8101/health",
        "command": (
            "python -m uvicorn agents.generated.weather_map_agent.main:app "
            "--host 0.0.0.0 --port 43773"
        ),
    }
    saved: list[dict[str, object]] = []
    monkeypatch.setattr(
        "hypervisor.deployment_registry.lifecycle.load_runtime_state",
        lambda _deployment_id, _root=None: existing,
    )
    monkeypatch.setattr(
        "hypervisor.deployment_registry.lifecycle.is_process_alive",
        lambda pid: pid == 4242,
    )
    monkeypatch.setattr(
        "hypervisor.deployment_registry.lifecycle.save_runtime_state",
        lambda _deployment_id, state, _root=None: saved.append(state),
    )

    from hypervisor.deployment_registry.runner import run_agent

    result = run_agent("weather-map-agent.local", detach=True)
    assert result.get("already_running") is True
    assert result["health_uri"] == "http://localhost:43773/health"
    assert saved and saved[0]["health_uri"] == "http://localhost:43773/health"


def test_run_agent_restarts_when_explicit_port_differs(monkeypatch: pytest.MonkeyPatch):
    existing = {
        "pid": 4242,
        "status": "running",
        "health_uri": "http://localhost:8101/health",
    }
    stopped: list[str] = []
    started: list[dict[str, object]] = []

    monkeypatch.setattr(
        "hypervisor.deployment_registry.lifecycle.load_runtime_state",
        lambda _deployment_id, _root=None: existing,
    )
    monkeypatch.setattr(
        "hypervisor.deployment_registry.lifecycle.is_process_alive",
        lambda pid: pid == 4242,
    )
    monkeypatch.setattr(
        "hypervisor.deployment_registry.lifecycle.stop_agent",
        lambda selector, **kwargs: stopped.append(selector) or {"status": "stopped"},
    )

    class _Proc:
        pid = 5151

    monkeypatch.setattr(
        "hypervisor.deployment_registry.lifecycle.start_process",
        lambda plan, **kwargs: started.append(plan) or _Proc(),
    )
    monkeypatch.setattr(
        "hypervisor.deployment_registry.lifecycle.save_runtime_state",
        lambda *_args, **_kwargs: None,
    )

    from hypervisor.deployment_registry.runner import run_agent

    result = run_agent("weather-map-agent.local", detach=True, port=8111)
    assert stopped == ["weather-map-agent.local"]
    assert result.get("already_running") is not True
    assert result["port"] == 8111
    assert result["health_uri"] == "http://localhost:8111/health"
    assert result["pid"] == 5151


def test_run_agent_if_running_fail(monkeypatch: pytest.MonkeyPatch):
    existing = {
        "pid": 4242,
        "status": "running",
        "health_uri": "http://localhost:8101/health",
    }
    monkeypatch.setattr(
        "hypervisor.deployment_registry.lifecycle.load_runtime_state",
        lambda _deployment_id, _root=None: existing,
    )
    monkeypatch.setattr(
        "hypervisor.deployment_registry.lifecycle.is_process_alive",
        lambda pid: pid == 4242,
    )

    from hypervisor.deployment_registry.runner import run_agent

    with pytest.raises(RuntimeError, match="already running"):
        run_agent("weather-map-agent.local", detach=True, if_running="fail")


def test_inspect_agent_separates_process_running_from_health(monkeypatch: pytest.MonkeyPatch):
    existing = {
        "pid": 4242,
        "status": "running",
        "health_uri": "http://localhost:40061/health",
        "log_uri": "log://hypervisor?grep=weather-map-agent.local",
    }

    monkeypatch.setattr(
        "hypervisor.deployment_registry.supervisor.load_runtime_state",
        lambda _deployment_id, _root=None: existing,
    )
    monkeypatch.setattr(
        "hypervisor.deployment_registry.supervisor.is_process_alive",
        lambda pid: pid == 4242,
    )
    monkeypatch.setattr(
        "hypervisor.deployment_registry.supervisor.runtime_status",
        lambda _deployment_id, _root=None: "running",
    )

    def fake_get(uri: str, timeout: float):
        raise RuntimeError(f"connection refused: {uri}")

    monkeypatch.setattr("hypervisor.deployment_registry.supervisor.httpx.get", fake_get)
    payload = inspect_agent("weather-map-agent.local")

    assert payload["process"]["running"] is True
    assert payload["health"]["ok"] is False
    assert payload["service_status"] == "unhealthy"
    codes = {item["code"] for item in payload["incidents"]}
    assert "PROCESS_RUNNING_BUT_UNHEALTHY" in codes
    assert payload["readiness"]["process"] == "running"
    assert payload["readiness"]["health"] == "failed"


def test_inspect_agent_detects_command_health_mismatch(monkeypatch: pytest.MonkeyPatch):
    existing = {
        "pid": 4242,
        "status": "running",
        "health_uri": "http://localhost:8101/health",
        "command": (
            "python -m uvicorn agents.generated.weather_map_agent.main:app "
            "--host 0.0.0.0 --port 43773"
        ),
        "log_uri": "log://hypervisor?grep=weather-map-agent.local",
    }

    monkeypatch.setattr(
        "hypervisor.deployment_registry.supervisor.load_runtime_state",
        lambda _deployment_id, _root=None: existing,
    )
    monkeypatch.setattr(
        "hypervisor.deployment_registry.supervisor.is_process_alive",
        lambda pid: pid == 4242,
    )
    monkeypatch.setattr(
        "hypervisor.deployment_registry.supervisor.runtime_status",
        lambda _deployment_id, _root=None: "running",
    )

    def fake_get(uri: str, timeout: float):
        if ":43773/" in uri:
            response = type("Resp", (), {})()
            response.is_success = True
            response.status_code = 200
            response.headers = {"content-type": "application/json"}
            response.json = lambda: {"ok": True, "agent": "weather-map-agent"}
            return response
        raise RuntimeError(f"connection refused: {uri}")

    monkeypatch.setattr("hypervisor.deployment_registry.supervisor.httpx.get", fake_get)
    payload = inspect_agent("weather-map-agent.local")

    assert payload["ok"] is False
    assert payload["readiness"]["health"] == "ok"
    assert payload["effective_health_uri"] == "http://localhost:43773/health"
    codes = {item["code"] for item in payload["incidents"]}
    assert "COMMAND_HEALTH_MISMATCH" in codes


def test_supervise_auto_syncs_health_uri(monkeypatch: pytest.MonkeyPatch):
    state = {
        "pid": 4242,
        "status": "running",
        "health_uri": "http://localhost:8101/health",
        "command": (
            "python -m uvicorn agents.generated.weather_map_agent.main:app "
            "--host 0.0.0.0 --port 43773"
        ),
    }
    sync_calls: list[str] = []

    monkeypatch.setattr(
        "hypervisor.deployment_registry.supervisor.load_runtime_state",
        lambda _deployment_id, _root=None: state,
    )
    monkeypatch.setattr(
        "hypervisor.deployment_registry.supervisor.is_process_alive",
        lambda pid: pid == 4242,
    )
    monkeypatch.setattr(
        "hypervisor.deployment_registry.supervisor.runtime_status",
        lambda _deployment_id, _root=None: "running",
    )

    def fake_get(uri: str, timeout: float):
        if ":43773/" in uri:
            response = type("Resp", (), {})()
            response.is_success = True
            response.status_code = 200
            response.headers = {"content-type": "application/json"}
            response.json = lambda: {"ok": True, "agent": "weather-map-agent"}
            return response
        return {"uri": uri, "ok": False, "error": "refused"}

    monkeypatch.setattr("hypervisor.deployment_registry.supervisor.httpx.get", fake_get)
    monkeypatch.setattr(
        "hypervisor.deployment_registry.supervisor._read_error_logs",
        lambda *_args, **_kwargs: {"error_count": 0, "entries": []},
    )
    monkeypatch.setattr(
        "hypervisor.deployment_registry.supervisor.run_agent",
        lambda selector, **kwargs: (
            sync_calls.append("sync")
            or state.update({"health_uri": "http://localhost:43773/health"})
            or {"ok": True}
        ),
    )

    from hypervisor.deployment_registry.supervisor import supervise_agent

    payload = supervise_agent("weather-map-agent.local", repair="auto", max_attempts=1)
    assert payload["ok"] is True
    assert sync_calls == ["sync"]

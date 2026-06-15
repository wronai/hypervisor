"""Tests for deployment registry agent runner."""

from __future__ import annotations

from pathlib import Path
from urllib.parse import urlparse

import pytest
from hypervisor.deployment_registry.models import AgentDeployment
from hypervisor.deployment_registry.runner import (
    agent_status,
    build_run_plan,
    inspect_agent,
    local_target_to_module,
    resolve_deployment,
)


def _deployment_port(deployment_id: str) -> int:
    deployment = resolve_deployment(deployment_id)
    health_uri = deployment.health_uri or ""
    parsed = urlparse(health_uri)
    if parsed.port is None:
        raise AssertionError(f"Deployment {deployment_id} has no health port")
    return parsed.port


def _mock_run_dependencies(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "hypervisor.deployment_registry.lifecycle.validate_run_dependencies",
        lambda plan: None,
    )


def test_local_target_to_module():
    assert local_target_to_module("local://agents/generated/weather_map_agent") == (
        "agents.generated.weather_map_agent.main:app"
    )


def test_build_run_plan_for_local_deployment():
    deployment = resolve_deployment("weather-map-agent.local")
    preferred_port = _deployment_port("weather-map-agent.local")
    plan = build_run_plan(deployment)
    assert plan["module"] == "agents.generated.weather_map_agent.main:app"
    assert plan["port"] == preferred_port
    assert "uvicorn" in plan["command"]
    assert plan["health_uri"] == f"http://localhost:{preferred_port}/health"
    assert plan["env"]["RESOURCE_RUNTIME_URL"] == "http://localhost:8000"


def test_build_run_plan_with_port_override_updates_local_endpoints():
    deployment = resolve_deployment("weather-map-agent.local")
    plan = build_run_plan(deployment, port=8111)
    assert plan["port"] == 8111
    assert plan["health_uri"] == "http://localhost:8111/health"
    assert plan["card_uri"] == "http://localhost:8111/.well-known/agent-card.json"


def test_run_agent_dry_run_emits_lifecycle_event(monkeypatch: pytest.MonkeyPatch):
    emitted: list[dict[str, object]] = []

    def fake_emit(code, message, **kwargs):
        emitted.append({"code": code, "message": message, **kwargs})

    monkeypatch.setattr(
        "hypervisor.deployment_registry.lifecycle.emit_operation_event",
        fake_emit,
    )
    monkeypatch.setattr(
        "hypervisor.deployment_registry.lifecycle.load_or_clear_runtime_state",
        lambda *_args, **_kwargs: None,
    )

    from hypervisor.deployment_registry.runner import run_agent

    result = run_agent("weather-map-agent.local", dry_run=True)

    assert result["result_type"] == "lifecycle"
    assert emitted
    assert emitted[0]["code"] == "AGENT_RUN_PLANNED"
    assert emitted[0]["selector"] == "weather-map-agent.local"


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


def test_ssh_target_starts_via_remote_runner(monkeypatch: pytest.MonkeyPatch):
    from hypervisor.deployment_registry.runner import run_agent

    monkeypatch.setattr(
        "hypervisor.deployment_registry.ssh_run.apply_ssh_run_plan",
        lambda plan, **kwargs: {"ok": True, "remote_pid": 1234, "health_uri": plan["health_uri"]},
    )
    result = run_agent("weather-map-agent.ssh-dev", dry_run=False, detach=True)
    assert result.get("ok") is True
    assert result.get("transport") == "ssh"


def test_run_agent_detach_idempotent_when_already_running(monkeypatch: pytest.MonkeyPatch):
    preferred_port = _deployment_port("weather-map-agent.local")
    existing = {
        "pid": 4242,
        "status": "running",
        "health_uri": f"http://localhost:{preferred_port}/health",
    }
    monkeypatch.setattr(
        "hypervisor.deployment_registry.run_executor.load_runtime_state",
        lambda _deployment_id, _root=None: existing,
    )
    monkeypatch.setattr(
        "hypervisor.deployment_registry.run_executor.is_process_alive",
        lambda pid: pid == 4242,
    )
    monkeypatch.setattr(
        "hypervisor.deployment_registry.lifecycle.is_process_alive",
        lambda pid: pid == 4242,
    )

    from hypervisor.deployment_registry.runner import run_agent

    result = run_agent("weather-map-agent.local", detach=True)
    assert result.get("already_running") is True
    assert result["pid"] == 4242
    assert result["health_uri"] == f"http://localhost:{preferred_port}/health"


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
        "hypervisor.deployment_registry.run_executor.load_runtime_state",
        lambda _deployment_id, _root=None: existing,
    )
    monkeypatch.setattr(
        "hypervisor.deployment_registry.run_executor.is_process_alive",
        lambda pid: pid == 4242,
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
    _mock_run_dependencies(monkeypatch)
    existing = {
        "pid": 4242,
        "status": "running",
        "health_uri": "http://localhost:8101/health",
    }
    stopped: list[str] = []
    started: list[dict[str, object]] = []

    monkeypatch.setattr(
        "hypervisor.deployment_registry.run_executor.load_runtime_state",
        lambda _deployment_id, _root=None: existing,
    )
    monkeypatch.setattr(
        "hypervisor.deployment_registry.run_executor.is_process_alive",
        lambda pid: pid in {4242, 5151},
    )
    monkeypatch.setattr(
        "hypervisor.deployment_registry.lifecycle.is_process_alive",
        lambda pid: pid in {4242, 5151},
    )
    monkeypatch.setattr(
        "hypervisor.deployment_registry.lifecycle.stop_agent",
        lambda selector, **kwargs: stopped.append(selector) or {"status": "stopped"},
    )
    monkeypatch.setattr(
        "hypervisor.deployment_registry.lifecycle.clear_runtime_state",
        lambda *_args, **_kwargs: None,
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
    monkeypatch.setattr(
        "hypervisor.deployment_registry.run_executor.save_runtime_state",
        lambda *_args, **_kwargs: None,
    )
    monkeypatch.setattr(
        "hypervisor.deployment_registry.run_executor.is_port_free",
        lambda port, **kwargs: True,
    )

    monkeypatch.setattr(
        "hypervisor.deployment_registry.run_executor.time.sleep", lambda *_args: None
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
        "hypervisor.deployment_registry.run_executor.load_runtime_state",
        lambda _deployment_id, _root=None: existing,
    )
    monkeypatch.setattr(
        "hypervisor.deployment_registry.run_executor.is_process_alive",
        lambda pid: pid == 4242,
    )
    monkeypatch.setattr(
        "hypervisor.deployment_registry.lifecycle.is_process_alive",
        lambda pid: pid == 4242,
    )

    from hypervisor.deployment_registry.runner import run_agent

    with pytest.raises(RuntimeError, match="already running"):
        run_agent("weather-map-agent.local", detach=True, if_running="fail")


def test_run_agent_rebinds_when_preferred_port_busy(monkeypatch: pytest.MonkeyPatch):
    _mock_run_dependencies(monkeypatch)
    started: list[dict[str, object]] = []
    synced: list[tuple[str, int]] = []
    preferred_port = _deployment_port("weather-map-agent.local")

    monkeypatch.setattr(
        "hypervisor.deployment_registry.run_executor.load_runtime_state",
        lambda _deployment_id, _root=None: None,
    )
    monkeypatch.setattr(
        "hypervisor.deployment_registry.run_executor.is_port_free",
        lambda port, **kwargs: port != preferred_port,
    )
    monkeypatch.setattr(
        "hypervisor.deployment_registry.run_executor.find_free_port",
        lambda preferred, **kwargs: 8110,
    )

    class _Proc:
        pid = 9001

    monkeypatch.setattr(
        "hypervisor.deployment_registry.lifecycle.start_process",
        lambda plan, **kwargs: started.append(plan) or _Proc(),
    )
    monkeypatch.setattr(
        "hypervisor.deployment_registry.lifecycle.save_runtime_state",
        lambda *_args, **_kwargs: None,
    )
    monkeypatch.setattr(
        "hypervisor.deployment_registry.run_executor.save_runtime_state",
        lambda *_args, **_kwargs: None,
    )
    monkeypatch.setattr(
        "hypervisor.deployment_registry.run_executor.is_process_alive",
        lambda pid: pid == 9001,
    )
    monkeypatch.setattr(
        "hypervisor.deployment_registry.lifecycle.is_process_alive",
        lambda pid: pid == 9001,
    )
    monkeypatch.setattr(
        "hypervisor.deployment_registry.run_executor.time.sleep", lambda *_args: None
    )
    monkeypatch.setattr(
        "hypervisor.deployment_registry.lifecycle.persist_rebound_port",
        lambda deployment, plan, **_kwargs: synced.append((deployment.id, plan["port"]))
        or {"ok": True, "port": plan["port"]},
    )

    from hypervisor.deployment_registry.runner import run_agent

    result = run_agent("weather-map-agent.local", detach=True)
    assert result["port"] == 8110
    assert result["health_uri"] == "http://localhost:8110/health"
    assert result["registry_sync"] == {"ok": True, "port": 8110}
    assert synced == [("weather-map-agent.local", 8110)]
    assert started and started[0]["port_rebound"] == {
        "from": preferred_port,
        "to": 8110,
        "reason": "port_in_use",
    }


def test_stop_agent_cleans_orphan_listener_from_stale_runtime(monkeypatch: pytest.MonkeyPatch):
    existing = {
        "pid": 9001,
        "status": "running",
        "health_uri": "http://localhost:8110/health",
        "command": (
            "python -m uvicorn agents.generated.weather_map_agent.main:app "
            "--host 0.0.0.0 --port 8110"
        ),
    }
    terminated: list[int] = []
    saved: list[dict[str, object]] = []

    monkeypatch.setattr(
        "hypervisor.deployment_registry.stopper.load_runtime_state",
        lambda _deployment_id, _root=None: existing,
    )
    monkeypatch.setattr(
        "hypervisor.deployment_registry.stopper.is_process_alive",
        lambda pid: False if pid == 9001 else pid == 447240,
    )
    monkeypatch.setattr(
        "hypervisor.deployment_registry.stopper.pids_listening_on_port",
        lambda port: {447240} if port == 8110 else set(),
    )
    monkeypatch.setattr(
        "hypervisor.deployment_registry.stopper.command_matches_plan",
        lambda pid, _plan: pid == 447240,
    )
    monkeypatch.setattr(
        "hypervisor.deployment_registry.stopper.terminate_pid",
        lambda pid, **_kwargs: terminated.append(pid) or True,
    )
    monkeypatch.setattr(
        "hypervisor.deployment_registry.stopper.save_runtime_state",
        lambda _deployment_id, state, _root=None: saved.append(state),
    )

    from hypervisor.deployment_registry.runner import stop_agent

    result = stop_agent("weather-map-agent.local")
    assert result["status"] == "stopped"
    assert result["terminated_pids"] == [447240]
    assert terminated == [447240]
    assert saved and saved[0]["terminated_pids"] == [447240]


def test_stop_agent_does_not_kill_foreign_listener_without_state(monkeypatch: pytest.MonkeyPatch):
    killed: list[int] = []

    monkeypatch.setattr(
        "hypervisor.deployment_registry.stopper.load_runtime_state",
        lambda _deployment_id, _root=None: None,
    )
    monkeypatch.setattr(
        "hypervisor.deployment_registry.stopper.pids_listening_on_port",
        lambda port: {12345} if port == 8101 else set(),
    )
    monkeypatch.setattr(
        "hypervisor.deployment_registry.stopper.command_matches_plan",
        lambda _pid, _plan: False,
    )
    monkeypatch.setattr(
        "hypervisor.deployment_registry.stopper.terminate_pid",
        lambda pid, **_kwargs: killed.append(pid) or True,
    )

    from hypervisor.deployment_registry.runner import stop_agent

    result = stop_agent("weather-map-agent.local")
    assert result["status"] == "stopped"
    assert result["message"] == "No runtime state found"
    assert killed == []


def test_inspect_agent_separates_process_running_from_health(monkeypatch: pytest.MonkeyPatch):
    existing = {
        "pid": 4242,
        "status": "running",
        "health_uri": "http://localhost:40061/health",
        "log_uri": "log://hypervisor?grep=weather-map-agent.local",
    }

    monkeypatch.setattr(
        "hypervisor.deployment_registry.inspection.pipeline.load_runtime_state",
        lambda _deployment_id, _root=None: existing,
    )
    monkeypatch.setattr(
        "hypervisor.deployment_registry.inspection.pipeline.is_process_alive",
        lambda pid: pid == 4242,
    )
    monkeypatch.setattr(
        "hypervisor.deployment_registry.inspection.pipeline.runtime_status",
        lambda _deployment_id, _root=None: "running",
    )

    def fake_get(uri: str, timeout: float):
        raise RuntimeError(f"connection refused: {uri}")

    monkeypatch.setattr("hypervisor.deployment_registry.inspection.probe.httpx.get", fake_get)
    payload = inspect_agent("weather-map-agent.local")

    assert payload["process"]["running"] is True
    assert payload["health"]["ok"] is False
    assert payload["service_status"] == "unhealthy"
    codes = {item["code"] for item in payload["incidents"]}
    assert "PROCESS_RUNNING_BUT_UNHEALTHY" in codes
    assert payload["readiness"]["process"] == "running"
    assert payload["readiness"]["health"] == "failed"
    assert payload["agent_readiness"]["process_status"] == "running"
    assert payload["agent_readiness"]["health_status"] == "failed"


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
        "hypervisor.deployment_registry.inspection.pipeline.load_runtime_state",
        lambda _deployment_id, _root=None: existing,
    )
    monkeypatch.setattr(
        "hypervisor.deployment_registry.inspection.pipeline.is_process_alive",
        lambda pid: pid == 4242,
    )
    monkeypatch.setattr(
        "hypervisor.deployment_registry.inspection.pipeline.runtime_status",
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

    monkeypatch.setattr("hypervisor.deployment_registry.inspection.probe.httpx.get", fake_get)
    payload = inspect_agent("weather-map-agent.local")

    assert payload["ok"] is False
    assert payload["readiness"]["health"] == "ok"
    assert payload["effective_health_uri"] == "http://localhost:43773/health"
    codes = {item["code"] for item in payload["incidents"]}
    assert "COMMAND_HEALTH_MISMATCH" in codes


def test_inspect_agent_reads_process_log_uri(monkeypatch: pytest.MonkeyPatch):
    existing = {
        "pid": 4242,
        "status": "running",
        "health_uri": "http://localhost:8101/health",
        "process_log_uri": "log://file/output/logs/agents/weather-map-agent.local.process.log",
        "log_uri": "log://hypervisor?grep=weather-map-agent.local",
    }

    monkeypatch.setattr(
        "hypervisor.deployment_registry.inspection.pipeline.load_runtime_state",
        lambda _deployment_id, _root=None: existing,
    )
    monkeypatch.setattr(
        "hypervisor.deployment_registry.inspection.pipeline.is_process_alive",
        lambda pid: pid == 4242,
    )
    monkeypatch.setattr(
        "hypervisor.deployment_registry.inspection.pipeline.runtime_status",
        lambda _deployment_id, _root=None: "running",
    )

    def fake_get(uri: str, timeout: float):
        response = type("Resp", (), {})()
        response.is_success = True
        response.status_code = 200
        response.headers = {"content-type": "application/json"}
        response.json = lambda: {"ok": True, "agent": "weather-map-agent"}
        return response

    def fake_read_error_logs(log_uri: str, **_kwargs):
        if "agents/weather-map-agent.local.process.log" in log_uri:
            return {
                "uri": log_uri,
                "summary": {"path": "process.log"},
                "entries": [{"level": "ERROR", "message": "uvicorn failed"}],
                "error_count": 1,
            }
        return {
            "uri": log_uri,
            "summary": {"path": "hypervisor.log"},
            "entries": [],
            "error_count": 0,
        }

    monkeypatch.setattr("hypervisor.deployment_registry.inspection.probe.httpx.get", fake_get)
    monkeypatch.setattr(
        "hypervisor.deployment_registry.inspection.pipeline.read_error_logs",
        fake_read_error_logs,
    )
    payload = inspect_agent("weather-map-agent.local")

    assert payload["process_log_uri"] == existing["process_log_uri"]
    assert payload["log_errors"]["error_count"] == 1
    assert len(payload["log_errors"]["sources"]) == 2


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
        "hypervisor.deployment_registry.inspection.pipeline.load_runtime_state",
        lambda _deployment_id, _root=None: state,
    )
    monkeypatch.setattr(
        "hypervisor.deployment_registry.inspection.pipeline.is_process_alive",
        lambda pid: pid == 4242,
    )
    monkeypatch.setattr(
        "hypervisor.deployment_registry.inspection.pipeline.runtime_status",
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

    monkeypatch.setattr("hypervisor.deployment_registry.inspection.probe.httpx.get", fake_get)
    monkeypatch.setattr(
        "hypervisor.deployment_registry.inspection.probe.read_error_logs",
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


def test_ensure_agent_healthy_waits_before_first_probe(monkeypatch: pytest.MonkeyPatch):
    sleeps: list[float] = []

    monkeypatch.setattr(
        "hypervisor.deployment_registry.supervisor.time.sleep",
        lambda seconds: sleeps.append(seconds),
    )
    monkeypatch.setattr(
        "hypervisor.deployment_registry.supervisor.inspect_agent",
        lambda *args, **kwargs: {
            "ok": True,
            "id": "weather-map-agent.local",
            "service_status": "healthy",
        },
    )

    from hypervisor.deployment_registry.supervisor import ensure_agent_healthy

    payload = ensure_agent_healthy("weather-map-agent.local", settle_seconds=0.25)
    assert payload["ok"] is True
    assert payload["attempts"] == 0
    assert sleeps == [0.25]


def test_verify_local_deployment(monkeypatch: pytest.MonkeyPatch):
    from hypervisor.deployment_registry.local_verify import verify_local_deployment

    deployment = resolve_deployment("weather-map-agent.local")
    monkeypatch.setattr(
        "hypervisor.deployment_registry.local_verify.runtime_status",
        lambda _deployment_id, _root=None: "running",
    )
    monkeypatch.setattr(
        "hypervisor.deployment_registry.local_verify.load_runtime_state",
        lambda _deployment_id, _root=None: {"pid": 4242},
    )
    monkeypatch.setattr(
        "hypervisor.deployment_registry.local_verify.health_scan_ok",
        lambda _items: True,
    )
    monkeypatch.setattr(
        "hypervisor.deployment_registry.local_verify.scan_http",
        lambda _uri: [],
    )

    payload = verify_local_deployment(deployment, check_health=True)
    assert payload["local_target_ok"] is True
    assert payload["runtime_status"] == "running"
    assert payload["health_ok"] is True
    assert payload["verified"] is True

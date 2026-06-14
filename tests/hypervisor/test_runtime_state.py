"""Tests for deployment runtime state and env resolution."""

from __future__ import annotations

from hypervisor.deployment_registry.env import resolve_deployment_env
from hypervisor.deployment_registry.run_executor import sync_runtime_health_uri
from hypervisor.deployment_registry.runner import build_run_plan, resolve_deployment
from hypervisor.deployment_registry.runtime_state import (
    is_process_alive,
    load_runtime_state,
    runtime_status,
    save_runtime_state,
)


def test_build_run_plan_includes_env_and_runtime_paths():
    deployment = resolve_deployment("weather-map-agent.local")
    plan = build_run_plan(deployment)
    assert plan["env"]["RESOURCE_RUNTIME_URL"] == "http://localhost:8000"
    assert plan["env"]["OPENROUTER_API_KEY"] == "env://OPENROUTER_API_KEY"
    assert "runtime_state_path" in plan
    assert plan["log_uri"].startswith("log://")


def test_resolve_deployment_env_merges_uri_yaml(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "config").mkdir()
    (tmp_path / "config" / "deployments.uri.yaml").write_text(
        """
version: 1
defaults:
  env:
    RESOURCE_RUNTIME_URL: http://localhost:9000
""",
        encoding="utf-8",
    )
    env = resolve_deployment_env("demo.local", "agent://demo-agent", {"FOO": "bar"}, root=tmp_path)
    assert env["RESOURCE_RUNTIME_URL"] == "http://localhost:9000"
    assert env["FOO"] == "bar"


def test_runtime_state_roundtrip(tmp_path):
    save_runtime_state(
        "weather-map-agent.local",
        {"id": "weather-map-agent.local", "pid": 999999, "status": "running"},
        tmp_path,
    )
    state = load_runtime_state("weather-map-agent.local", tmp_path)
    assert state["pid"] == 999999
    assert runtime_status("weather-map-agent.local", tmp_path) in {"stale", "stopped"}
    assert is_process_alive(999999) is False


def test_sync_runtime_health_uri_updates_network_fields():
    state = {
        "kind": "RuntimeState",
        "status": {"process_status": "running"},
        "health_uri": "http://localhost:8101/health",
        "network": {
            "effective_port": 8101,
            "effective_health_uri": "http://localhost:8101/health",
        },
    }

    updated = sync_runtime_health_uri(state, "http://localhost:43773/health")

    assert updated["health_uri"] == "http://localhost:43773/health"
    assert updated["network"]["effective_health_uri"] == "http://localhost:43773/health"
    assert updated["network"]["effective_port"] == 43773

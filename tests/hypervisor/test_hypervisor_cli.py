"""Hypervisor CLI tests."""

from __future__ import annotations

import json

from hypervisor.cli import main


def test_cli_deployments_and_run_agent_dry_run(capsys):
    rc = main(["deployments"])
    assert rc == 0
    deployments = json.loads(capsys.readouterr().out)
    assert any(item["id"] == "weather-map-agent.local" for item in deployments)

    rc = main(["run-agent", "weather-map-agent.local", "--dry-run"])
    assert rc == 0
    plan = json.loads(capsys.readouterr().out)
    assert plan["module"] == "agents.generated.weather_map_agent.main:app"
    assert plan["port"] == 8101
    assert plan["env"]["RESOURCE_RUNTIME_URL"] == "http://localhost:8000"


def test_cli_ssh_run_agent_dry_run(capsys):
    rc = main(["run-agent", "weather-map-agent.ssh-dev", "--dry-run"])
    assert rc == 0
    plan = json.loads(capsys.readouterr().out)
    assert plan["transport"] == "ssh"
    assert "remote_command" in plan


def test_cli_deploy_agent_dry_run(capsys):
    rc = main(["deploy-agent", "weather-map-agent.ssh-dev"])
    assert rc == 0
    plan = json.loads(capsys.readouterr().out)
    assert plan["steps"][0]["action"] == "rsync"


def test_cli_agent_status_includes_runtime_fields(capsys):
    rc = main(["agent-status", "weather-map-agent.local", "--no-health"])
    assert rc == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["runtime_status"] in {"stopped", "running", "stale"}
    assert "env" in payload


def test_cli_run_agent_dry_run_accepts_if_running(capsys):
    rc = main(["run-agent", "weather-map-agent.local", "--dry-run", "--if-running", "reuse"])
    assert rc == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["module"] == "agents.generated.weather_map_agent.main:app"


def test_cli_inspect_agent(monkeypatch, capsys):
    monkeypatch.setattr(
        "hypervisor.cli.inspect_agent",
        lambda selector, timeout=2.0, log_limit=20: {
            "ok": True,
            "id": selector,
            "service_status": "healthy",
        },
    )
    rc = main(["inspect-agent", "weather-map-agent.local"])
    assert rc == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["service_status"] == "healthy"

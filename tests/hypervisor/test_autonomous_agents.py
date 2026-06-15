from __future__ import annotations

from hypervisor.agent_describe import describe_agent


def test_describe_remote_deploy_custom_agent():
    report = describe_agent("remote-deploy-agent.local")
    md = report.markdown
    assert report.data["agent_kind"] == "custom"
    assert "Custom agent package" in md
    assert "deploy_verify_start" in md
    assert "http://localhost:8135/health" in md


def test_describe_gnome_programmer_custom_agent():
    report = describe_agent("gnome-programmer-agent.local")
    md = report.markdown
    assert report.data["agent_kind"] == "custom"
    assert "programmer_session" in md
    assert "http://localhost:8136/health" in md


def test_remote_deploy_plan_for_ssh_dev():
    from agents.custom.remote_deploy_agent.deploy import plan_remote_deploy

    payload = plan_remote_deploy("weather-map-agent.ssh-dev")
    assert payload["ok"] is True
    assert payload["plan"]["steps"][0]["action"] == "rsync"

from __future__ import annotations

from urish.backends.agent_factory import build_agent_contract, generate_agent_from_prompt
from urish.backends.ask import ask_prompt
from urish.intent import detect_intent

PROMPT = (
    "stworz nowego agenta codex-nl-smoke-agent, ktory czyta file:// README, "
    "sprawdza device://device/sensor-1/status i ma komende cron monitor"
)


def test_detect_agent_factory_intent():
    intent = detect_intent(PROMPT)

    assert intent["kind"] == "agent_factory"
    assert intent["subtype"] == "generate-agent"
    assert intent["agent_id"] == "codex-nl-smoke-agent"
    assert intent["deployment_id"] == "codex-nl-smoke-agent.local"


def test_dashboard_prompt_still_uses_ecosystem_intent():
    intent = detect_intent(
        "stwórz aplikację web UI jako agenta do pokazywania procesów hypervisora"
    )

    assert intent["kind"] == "ecosystem"
    assert intent["subtype"] == "dashboard-agent"


def test_build_agent_contract_from_uri_prompt():
    contract = build_agent_contract(PROMPT)
    capabilities = {item["name"]: item for item in contract["capabilities"]}

    assert contract["agent"]["name"] == "codex-nl-smoke-agent"
    assert capabilities["read_markpact_source"]["uri"].startswith("file://")
    assert capabilities["read_device_status"]["uri"] == "device://device/sensor-1/status"
    assert capabilities["run_cron_monitor"]["uri"] == "cron://www/monitor/landing"
    assert capabilities["run_cron_monitor"]["command"] == "RunCronMonitor"


def test_build_agent_contract_from_robot_uri_prompt():
    contract = build_agent_contract(
        "stworz agenta patrol-agent do sprawdzania robot://robot/amr-1/state"
    )
    capabilities = {item["name"]: item for item in contract["capabilities"]}

    assert contract["agent"]["name"] == "patrol-agent"
    assert capabilities["read_robot_state"]["uri"] == "robot://robot/amr-1/state"
    assert capabilities["read_robot_state"]["output_schema"] == "operator.robot.v1.RobotState"


def test_ask_agent_factory_returns_lifecycle_steps():
    result = ask_prompt(PROMPT)
    data = result["data"]

    assert data["detected_kind"] == "agent_factory"
    assert data["deployment_id"] == "codex-nl-smoke-agent.local"
    assert any("uri agent generate" in step for step in data["next_steps"])
    assert any("uri agent run codex-nl-smoke-agent.local" in step for step in data["next_steps"])
    assert data["planned_uris"][0].startswith("agent-factory://generate/codex-nl-smoke-agent")
    assert "hypervisor://agent/codex-nl-smoke-agent.local/run" in data["planned_uris"]
    assert "agent://codex-nl-smoke-agent" in data["generated"]["resource_uris"]


def test_generate_agent_dry_run_does_not_write(tmp_path):
    result = generate_agent_from_prompt(PROMPT, dry_run=True, root=tmp_path)

    assert result["ok"] is True
    assert result["result_type"] == "agent_generation_plan"
    assert result["planned"]["deployment_id"] == "codex-nl-smoke-agent.local"
    assert not (tmp_path / "contracts" / "agents" / "codex_nl_smoke_agent.yaml").exists()


SSH_PROMPT = (
    "stworz agenta edge-agent i wdroz go na ssh://deploy@localhost:2222/opt/agents/edge-agent"
)


def test_ssh_prompt_plans_remote_deployment(tmp_path):
    result = generate_agent_from_prompt(SSH_PROMPT, dry_run=True, root=tmp_path)

    assert result["planned"]["ssh_deployment_id"] == "edge-agent.ssh-dev"
    assert result["planned"]["ssh_target_uri"] == "ssh://deploy@localhost:2222/opt/agents/edge-agent"
    assert any("hypervisor deploy-agent edge-agent.ssh-dev" in step for step in result["next_steps"])
    assert any("deploy_verify_start" in step for step in result["next_steps"])


def test_ssh_keyword_uses_default_target(tmp_path):
    result = generate_agent_from_prompt(
        "stworz agenta remote-smoke-agent i wdroz na zdalnym serwerze ssh",
        dry_run=True,
        root=tmp_path,
    )

    assert result["planned"]["ssh_deployment_id"] == "remote-smoke-agent.ssh-dev"
    assert result["planned"]["ssh_target_uri"] == "ssh://deploy@localhost:2222/opt/agents/remote-smoke-agent"


def test_ask_ssh_prompt_includes_deploy_steps():
    result = ask_prompt(SSH_PROMPT)
    data = result["data"]

    assert data["generated"]["ssh_deployment_id"] == "edge-agent.ssh-dev"
    assert any("hypervisor deploy-agent edge-agent.ssh-dev" in step for step in data["next_steps"])

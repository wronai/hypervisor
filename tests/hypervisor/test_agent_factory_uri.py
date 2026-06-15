from __future__ import annotations

from urllib.parse import quote

from hypervisor_dashboard_agent.uri_client import call_system_uri


def test_agent_factory_generate_uri_dry_run(tmp_path):
    prompt = "stworz nowego agenta uri-plan-agent z file:// README"
    uri = f"agent-factory://generate/uri-plan-agent?prompt={quote(prompt, safe='')}"

    result = call_system_uri(uri, root=tmp_path, dry_run=True)

    assert result["ok"] is True
    assert result["result_type"] == "agent_generation_plan"
    assert result["planned"]["deployment_id"] == "uri-plan-agent.local"
    assert not (tmp_path / "contracts" / "agents" / "uri_plan_agent.yaml").exists()


def test_hypervisor_agent_run_uri_dry_run_waits_for_generated_deployment(tmp_path):
    result = call_system_uri(
        "hypervisor://agent/uri-plan-agent.local/run",
        root=tmp_path,
        dry_run=True,
    )

    assert result["ok"] is True
    assert result["result_type"] == "lifecycle_plan"
    assert result["service_result_status"] == "preview"
    assert result["pending_dependency"] == "deployment registry entry"


def test_schema_uri_returns_agent_contract_and_capability_refs(tmp_path):
    contract_path = tmp_path / "contracts" / "agents" / "schema_agent.yaml"
    contract_path.parent.mkdir(parents=True)
    contract_path.write_text(
        """
agent:
  name: schema-agent
  python_package: schema_agent
capabilities:
  - name: read_status
    type: resource_read
    uri: file:///tmp/status.json
    output_schema: app.schema.v1.StatusView
  - name: refresh_status
    type: command
    command: RefreshStatus
    input_schema: app.schema.v1.RefreshStatusCommand
""",
        encoding="utf-8",
    )
    registry_path = tmp_path / "deployments" / "agent_deployments.yaml"
    registry_path.parent.mkdir(parents=True)
    registry_path.write_text(
        """
deployments:
  - id: schema-agent.local
    agent_ref: agent://schema-agent
    target_uri: local://agents/generated/schema_agent
    status: generated
    health_uri: http://localhost:8999/health
    card_uri: http://localhost:8999/.well-known/agent-card.json
    metadata:
      contract: contracts/agents/schema_agent.yaml
""",
        encoding="utf-8",
    )

    result = call_system_uri("schema://agent/schema-agent.local", root=tmp_path)

    assert result["ok"] is True
    assert result["result_type"] == "agent_schema"
    assert result["contract_uri"].startswith("file://")
    assert result["schemas"]["input"] == ["app.schema.v1.RefreshStatusCommand"]
    assert result["schemas"]["output"] == ["app.schema.v1.StatusView"]
    assert result["related_uris"]["schema"] == "schema://agent/schema-agent.local"


def test_file_uri_returns_small_text_content(tmp_path):
    readme = tmp_path / "README.md"
    readme.write_text("# Demo\n\ncontent\n", encoding="utf-8")

    result = call_system_uri(f"file://{readme.as_posix()}", root=tmp_path)

    assert result["ok"] is True
    assert result["result_type"] == "file"
    assert result["data"]["exists"] is True
    assert result["data"]["content"] == "# Demo\n\ncontent\n"

from __future__ import annotations

from hypervisor_dashboard_agent.uri_client import call_system_uri


def _write_contract_fixture(tmp_path):
    contract_path = tmp_path / "contracts" / "agents" / "demo_agent.yaml"
    contract_path.parent.mkdir(parents=True)
    contract_path.write_text(
        """
agent:
  name: demo-agent
  python_package: demo_agent
capabilities:
  - name: read_status
    type: resource_read
    uri: resource://demo/status
    output_schema: app.demo.v1.StatusView
    renderer: detail
""",
        encoding="utf-8",
    )
    registry_path = tmp_path / "deployments" / "agent_deployments.yaml"
    registry_path.parent.mkdir(parents=True)
    registry_path.write_text(
        """
deployments:
  - id: demo-agent.local
    agent_ref: agent://demo-agent
    target_uri: local://agents/generated/demo_agent
    status: generated
    metadata:
      contract: contracts/agents/demo_agent.yaml
""",
        encoding="utf-8",
    )
    schemas = tmp_path / "schemas"
    schemas.mkdir(parents=True)
    (schemas / "agent_contract.schema.json").write_text(
        '{"type":"object","properties":{"agent":{"type":"object"},"capabilities":{"type":"array"}},"required":["agent","capabilities"]}',
        encoding="utf-8",
    )
    (tmp_path / "contracts" / "registry.yaml").write_text("registry: {}\n", encoding="utf-8")
    (tmp_path / "contracts" / "resources.yaml").write_text("resources: []\n", encoding="utf-8")
    (tmp_path / "contracts" / "views.yaml").write_text("views: []\n", encoding="utf-8")
    return contract_path


def test_contract_uri_fetch_by_agent_name(tmp_path):
    _write_contract_fixture(tmp_path)

    result = call_system_uri("contract://agent/demo-agent", root=tmp_path)

    assert result["ok"] is True
    assert result["result_type"] == "agent_contract"
    assert result["agent_name"] == "demo-agent"
    assert result["contract_path"] == "contracts/agents/demo_agent.yaml"
    assert result["related_uris"]["validate"] == "contract://agent/demo-agent/validate"
    assert result["related_uris"]["generate"] == "contract://agent/demo-agent/generate"
    assert result["related_uris"]["artifacts"] == "contract://agent/demo-agent/artifacts"
    assert result["related_uris"]["schema"] == "schema://agent/demo-agent.local"


def test_contract_uri_fetch_by_agents_slug(tmp_path):
    _write_contract_fixture(tmp_path)

    result = call_system_uri("contract://agents/demo_agent", root=tmp_path)

    assert result["ok"] is True
    assert result["agent_name"] == "demo-agent"


def test_contract_uri_validate_agent(tmp_path):
    _write_contract_fixture(tmp_path)

    result = call_system_uri("contract://agent/demo-agent/validate", root=tmp_path)

    assert result["ok"] is True
    assert result["result_type"] == "contract_validation"
    assert result["valid"] is True
    assert result["checks"]["schema"][0]["ok"] is True


def test_contract_uri_validate_registry(tmp_path):
    _write_contract_fixture(tmp_path)

    result = call_system_uri("contract://registry/validate", root=tmp_path)

    assert result["result_type"] == "contract_validation"
    assert "checks" in result


def test_contract_uri_fetch_weather_agent(repo_root):
    result = call_system_uri("contract://agent/weather-map-agent", root=repo_root)

    assert result["ok"] is True
    assert result["agent_name"] == "weather-map-agent"
    assert "generate_weather_map" in {cap["name"] for cap in result["capabilities"]}


def test_schema_uri_includes_contract_related_uri(tmp_path):
    _write_contract_fixture(tmp_path)

    result = call_system_uri("schema://agent/demo-agent.local", root=tmp_path)

    assert result["ok"] is True
    assert result["related_uris"]["contract"] == "contract://agent/demo-agent"


def test_contract_uri_generate_dry_run(tmp_path):
    _write_contract_fixture(tmp_path)

    result = call_system_uri("contract://agent/demo-agent/generate?dry_run=1", root=tmp_path)

    assert result["ok"] is True
    assert result["result_type"] == "contract_generate"
    assert result["dry_run"] is True
    assert result["contract_hash"].startswith("sha256:")
    assert "agents/generated/demo_agent/main.py" in result["planned_files"]


def test_contract_uri_generate_writes_package(tmp_path):
    _write_contract_fixture(tmp_path)

    result = call_system_uri("contract://agent/demo-agent/generate", root=tmp_path)

    assert result["ok"] is True
    assert result["result_type"] == "contract_generate"
    assert result["dry_run"] is False
    assert (tmp_path / "agents" / "generated" / "demo_agent" / "main.py").is_file()
    assert (tmp_path / "agents" / "generated" / "demo_agent" / ".generated.yaml").is_file()


def test_contract_uri_artifacts_manifest(tmp_path):
    _write_contract_fixture(tmp_path)
    call_system_uri("contract://agent/demo-agent/generate", root=tmp_path)

    result = call_system_uri(
        "contract://agent/demo-agent/artifacts?kinds=contract,agent,capability",
        root=tmp_path,
    )

    assert result["ok"] is True
    assert result["result_type"] == "contract_artifacts"
    kinds = {item["kind"] for item in result["artifacts"]}
    assert kinds >= {"contract", "agent", "capability"}
    assert any(item.get("name") == "read_status" for item in result["artifacts"] if item["kind"] == "capability")


def test_contract_uri_artifacts_includes_proto_for_user_agent(repo_root):
    result = call_system_uri(
        "contract://agent/user-agent/artifacts?kinds=proto",
        root=repo_root,
    )

    assert result["ok"] is True
    proto_paths = [item["path"] for item in result["artifacts"] if item["kind"] == "proto"]
    assert "contracts/proto/user.proto" in proto_paths

"""Tests for shared uri2run workflow transport helpers."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

from uri2run.transports.flow_transport import run_uri_flow
from uri2run.transports.graph_transport import run_uri_graph


def test_flow_and_graph_transports_share_dry_run_path(repo_root: Path):
    flow = repo_root / "examples" / "15_compact_uri_flow" / "weather.uri.flow.yaml"
    graph = repo_root / "examples" / "14_workflow_executor_mock" / "task_graph.yaml"
    context = {"root": str(repo_root)}
    payload = {"dry_run": True}

    flow_result = run_uri_flow(str(flow), payload, context).to_dict()
    graph_result = run_uri_graph(str(graph), payload, context).to_dict()

    assert flow_result["ok"] is True
    assert graph_result["ok"] is True
    assert flow_result["result_type"] == "plan"
    assert graph_result["result_type"] == "plan"
    assert flow_result["meta"]["transport"] == "uri_flow"
    assert graph_result["meta"]["transport"] == "uri_graph"
    assert "plan" in flow_result["data"]
    assert "plan" in graph_result["data"]


def test_workflow_transport_invalid_graph_uses_error_code():
    with patch(
        "uri2run.transports.workflow_transport.validate_workflow_graph",
        return_value=["missing steps"],
    ):
        result = run_uri_flow(
            "examples/15_compact_uri_flow/weather.uri.flow.yaml",
            {},
            {"root": "."},
        ).to_dict()

    assert result["ok"] is False
    assert result["errors"][0]["code"] == "FLOW_INVALID"

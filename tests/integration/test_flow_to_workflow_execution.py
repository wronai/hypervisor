"""Integration: compact URI flow -> expanded graph -> uri3 workflow."""

from __future__ import annotations

from pathlib import Path

from uri2flow import expand_flow
from uri3.graph import build_execution_plan, dry_run_workflow, load_workflow_graph, validate_workflow_graph


def test_compact_flow_to_dry_run(repo_root: Path) -> None:
    flow_path = repo_root / "examples/15_compact_uri_flow/weather.uri.flow.yaml"
    graph = expand_flow(flow_path)
    assert validate_workflow_graph(graph) == []
    plan = build_execution_plan(load_workflow_graph(graph))
    assert plan["steps"]
    simulation = dry_run_workflow(graph)
    assert simulation["workflow_result"]["ok"] is True


def test_branching_flow_has_expected_edges(repo_root: Path) -> None:
    flow_path = repo_root / "examples/15_compact_uri_flow/branching.uri.flow.yaml"
    graph = expand_flow(flow_path)
    nodes = {node["id"]: node for node in graph["graph"]["nodes"]}
    assert nodes["check_health"]["depends_on"] == ["run_agent"]
    assert nodes["read_card"]["depends_on"] == ["run_agent"]
    assert nodes["logs_if_failed"]["condition"]["if"] == "check_health.ok == false"


def test_nl2uri_flow_expands_and_validates() -> None:
    from nl2uri.flow_planner import plan_flow

    payload = plan_flow(
        "wygeneruj agenta pogodowego, uruchom go lokalnie i sprawdź health w Chrome"
    )
    graph = expand_flow(payload)
    assert validate_workflow_graph(graph) == []
    assert dry_run_workflow(graph)["workflow_result"]["ok"] is True

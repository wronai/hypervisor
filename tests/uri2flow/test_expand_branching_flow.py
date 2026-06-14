from pathlib import Path

from uri2flow import expand_flow


def test_expand_branching_flow(repo_root: Path) -> None:
    graph = expand_flow(repo_root / "examples/15_compact_uri_flow/branching.uri.flow.yaml")
    nodes = {n["id"]: n for n in graph["graph"]["nodes"]}
    assert nodes["check_health"]["depends_on"] == ["run_agent"]
    assert nodes["read_card"]["depends_on"] == ["run_agent"]
    assert nodes["logs_if_failed"]["condition"]["if"] == "check_health.ok == false"
    edges = graph["graph"]["edges"]
    assert {"from": "run_agent", "to": "check_health", "type": "depends_on"} in edges

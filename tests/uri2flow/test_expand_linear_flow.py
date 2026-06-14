from pathlib import Path

from uri2flow import expand_flow


def test_expand_linear_flow(repo_root: Path) -> None:
    graph = expand_flow(repo_root / "examples/15_compact_uri_flow/weather.uri.flow.yaml")
    nodes = graph["graph"]["nodes"]
    assert graph["nl2uri"]["kind"] == "workflow_graph"
    assert nodes[0]["operation"] == "generate"
    assert nodes[0]["kind"] == "command"
    assert nodes[1]["depends_on"] == [nodes[0]["id"]]
    assert nodes[2]["payload"]["url"] == "http://localhost:8101/health"
    assert nodes[2]["operation"] == "open"

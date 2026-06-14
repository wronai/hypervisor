from pathlib import Path

from uri2flow.cli import main


def test_cli_expand(repo_root: Path, tmp_path: Path) -> None:
    out = tmp_path / "graph.yaml"
    flow = repo_root / "examples/15_compact_uri_flow/weather.uri.flow.yaml"
    assert main(["expand", str(flow), "--out", str(out)]) == 0
    text = out.read_text(encoding="utf-8")
    assert "workflow_graph" in text
    assert "browser://chrome/page/open" in text

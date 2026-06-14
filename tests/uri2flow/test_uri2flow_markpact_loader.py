"""Tests for markpact:// uri2flow registries."""

from __future__ import annotations

from pathlib import Path

import pytest
from uri2flow import expand_flow, load_flow
from uri2flow.cli import main as uri2flow_main
from uri2flow.loaders.markpact_loader import (
    extract_markpact_blocks,
    is_markpact_registry,
    load_markpact_flow_dict,
    resolve_markpact_ref,
)
from uri3.graph import validate_workflow_graph


def _markpact_ref(repo_root: Path, fragment: str | None = None) -> str:
    ref = f"markpact://{repo_root / 'examples' / '22_markpact_weather' / 'README.md'}"
    if fragment:
        return f"{ref}#{fragment}"
    return ref


def test_is_markpact_registry():
    assert is_markpact_registry("markpact://examples/22/README.md") is True
    assert is_markpact_registry("examples/22/README.md") is False


def test_extract_markpact_flow_blocks():
    markdown = """
```markpact:flow demo-flow
flow:
  id: demo-flow
do:
  - echo://hello
```
"""
    blocks = extract_markpact_blocks(markdown, "flow")
    assert len(blocks) == 1
    assert blocks[0]["meta"] == "demo-flow"
    assert "flow:" in blocks[0]["body"]


def test_load_markpact_flow_dict(repo_root: Path):
    data = load_markpact_flow_dict(_markpact_ref(repo_root, "weather-health"), root=repo_root)
    assert data["flow"]["id"] == "weather-health"
    assert len(data["do"]) == 3


def test_load_flow_markpact_ref(repo_root: Path):
    flow = load_flow(_markpact_ref(repo_root, "weather-health"))
    assert flow.id == "weather-health"
    assert flow.steps[-1].uri == "browser://chrome/page/open"
    assert flow.steps[-1].payload["url"] == "http://localhost:8101/health"


def test_expand_flow_markpact_ref(repo_root: Path):
    graph = expand_flow(_markpact_ref(repo_root, "weather-health"))
    assert graph["nl2uri"]["kind"] == "workflow_graph"
    assert validate_workflow_graph(graph) == []
    nodes = graph["graph"]["nodes"]
    assert nodes[0]["uri"] == "agent://weather-generator"
    assert nodes[2]["payload"]["url"] == "http://localhost:8101/health"


def test_markpact_flow_requires_fragment_when_ambiguous(tmp_path: Path):
    readme = tmp_path / "README.md"
    readme.write_text(
        """
```markpact:flow one
flow: {id: one}
do: [http://localhost:8101/one]
```

```markpact:flow two
flow: {id: two}
do: [http://localhost:8101/two]
```
""",
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="Multiple markpact:flow"):
        load_markpact_flow_dict(f"markpact://{readme}")


def test_markpact_flow_matches_yaml_flow(repo_root: Path):
    yaml_graph = expand_flow(repo_root / "examples/15_compact_uri_flow/weather.uri.flow.yaml")
    markpact_graph = expand_flow(_markpact_ref(repo_root, "weather-health"))
    assert yaml_graph["graph"]["nodes"] == markpact_graph["graph"]["nodes"]


def test_resolve_markpact_ref(repo_root: Path):
    path, fragment = resolve_markpact_ref(
        _markpact_ref(repo_root, "weather-health"),
        root=repo_root,
    )
    assert path == (repo_root / "examples/22_markpact_weather/README.md").resolve()
    assert fragment == "weather-health"


def test_uri2flow_expand_cli(repo_root: Path, tmp_path: Path):
    out = tmp_path / "graph.yaml"
    exit_code = uri2flow_main(
        ["expand", _markpact_ref(repo_root, "weather-health"), "--out", str(out)]
    )
    text = out.read_text(encoding="utf-8")
    assert exit_code == 0
    assert "workflow_graph" in text
    assert "browser://chrome/page/open" in text


def test_missing_flow_fragment_raises(repo_root: Path):
    with pytest.raises(ValueError, match="matching #missing"):
        load_flow(_markpact_ref(repo_root, "missing"))


def test_missing_markpact_readme_raises(repo_root: Path):
    with pytest.raises(FileNotFoundError):
        load_markpact_flow_dict(
            "markpact://examples/does-not-exist/README.md#weather-health",
            root=repo_root,
        )

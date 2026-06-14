"""Tests for markpact:// touri registries."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from touri.cli import main as touri_main
from touri.executor import call_uri
from touri.loader import load_registry
from touri.loaders.markpact_loader import extract_markpact_blocks


def _markpact_ref(repo_root: Path, fragment: str | None = None) -> str:
    ref = f"markpact://{repo_root / 'examples' / '22_markpact_weather' / 'README.md'}"
    if fragment:
        return f"{ref}#{fragment}"
    return ref


def test_extract_markpact_capability_blocks():
    markdown = """
```markpact:capability demo.echo
version: 1
capability:
  id: demo.echo
backend:
  type: mock
```
"""
    blocks = extract_markpact_blocks(markdown, "capability")
    assert len(blocks) == 1
    assert blocks[0]["meta"] == "demo.echo"
    assert "capability:" in blocks[0]["body"]


def test_load_registry_from_markpact_readme(repo_root: Path):
    registry = load_registry(_markpact_ref(repo_root))
    assert len(registry) == 1
    manifest = registry[0]
    assert manifest.capability.id == "weather.forecast.markpact"
    assert manifest.capability.uri_template == "weather://markpact/{place}/{days}/html"
    assert manifest.backend.type == "python"


def test_load_registry_from_markpact_fragment(repo_root: Path):
    registry = load_registry(_markpact_ref(repo_root, "weather.forecast.markpact"))
    assert [item.capability.id for item in registry] == ["weather.forecast.markpact"]


def test_missing_markpact_capability_fragment_raises(repo_root: Path):
    with pytest.raises(ValueError, match="matching #missing"):
        load_registry(_markpact_ref(repo_root, "missing"))


def test_call_uri_from_markpact_registry(repo_root: Path):
    result = call_uri("weather://markpact/Gdansk/14/html", _markpact_ref(repo_root))
    payload = result.to_dict()
    assert payload["ok"] is True
    assert payload["capability"] == "weather.forecast.markpact"
    assert payload["data"]["place"] == "Gdansk"
    assert payload["artifact_uri"] == "artifact://weather/Gdansk/14/index.html"


def test_touri_list_markpact_registry_cli(repo_root: Path, capsys):
    exit_code = touri_main(["list", _markpact_ref(repo_root)])
    output = capsys.readouterr().out
    payload = json.loads(output)
    assert exit_code == 0
    assert payload[0]["capability"]["id"] == "weather.forecast.markpact"

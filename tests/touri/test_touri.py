from pathlib import Path

import pytest

from touri.loader import load_registry
from touri.matcher import match_uri
from touri.executor import call_uri


def test_load_registry(repo_root: Path):
    registry = load_registry(repo_root / "examples" / "20_touri_capabilities")
    ids = {m.capability.id for m in registry}
    assert "weather.forecast.html" in ids
    assert "echo.mock" in ids


def test_match_weather_uri(repo_root: Path):
    registry = load_registry(repo_root / "examples" / "20_touri_capabilities")
    match = match_uri("weather://forecast/Gdansk/14/html", registry)
    assert match is not None
    assert match.params == {"place": "Gdansk", "days": "14"}


def test_call_mock_uri(repo_root: Path):
    registry_dir = repo_root / "examples" / "20_touri_capabilities"
    result = call_uri("echo://Adam", registry_dir)
    assert result.ok is True
    assert result.capability == "echo.mock"


def test_call_python_weather_uri(repo_root: Path):
    registry_dir = repo_root / "examples" / "20_touri_capabilities"
    result = call_uri("weather://forecast/Gdansk/14/html", registry_dir)
    assert result.ok is True
    assert result.result_type == "artifact"
    assert result.data["place"] == "Gdansk"
    assert result.artifact_uri == "artifact://weather/Gdansk/14/index.html"

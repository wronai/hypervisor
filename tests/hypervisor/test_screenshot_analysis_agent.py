from __future__ import annotations

import json

from uri2ops.operator.artifacts import write_artifact
from uri3.graph.artifacts import mock_screenshot_png

from agents.custom.screenshot_analysis_agent.analysis import (
    _extract_screenshot_artifact,
    analyze_artifact,
)


def test_screenshot_analysis_agent_analyzes_operator_json_artifact(tmp_path):
    artifact_uri = write_artifact(
        "screenshot_page",
        {"screenshot": "mock", "target_uri": "browser://chrome/page/screenshot"},
        root=tmp_path,
    )

    result = analyze_artifact(
        artifact_uri,
        source_url="http://localhost:8788/www/",
        run_label="test-json",
        root=tmp_path,
    )

    assert result["ok"] is True
    assert result["media_type"] == "application/json"
    assert "target_uri=browser://chrome/page/screenshot" in result["summary"]
    jsonl_path = tmp_path / "output" / "analysis" / "screenshots" / "screenshot-analysis.jsonl"
    line = jsonl_path.read_text(encoding="utf-8").strip()
    assert json.loads(line)["artifact_uri"] == artifact_uri


def test_screenshot_analysis_agent_analyzes_png_and_detects_repeated_frame(tmp_path):
    path = tmp_path / "output" / "artifacts" / "operator" / "screenshots" / "frame.png"
    path.parent.mkdir(parents=True)
    path.write_bytes(mock_screenshot_png(width=320, height=180))
    artifact_uri = "artifact://operator/screenshots/frame.png"

    first = analyze_artifact(artifact_uri, run_label="test-png", root=tmp_path)
    second = analyze_artifact(artifact_uri, run_label="test-png", root=tmp_path)

    assert first["ok"] is True
    assert first["media_type"] == "image/png"
    assert first["image"] == {"width": 320, "height": 180}
    assert first["changed_from_previous"] is False
    assert second["previous_sha256"] == first["sha256"]
    assert second["changed_from_previous"] is False


def test_screenshot_analysis_agent_prefers_screenshot_step_artifact():
    result = {
        "steps": [
            {
                "id": "open_page",
                "uri": "browser://chrome/page/open",
                "operation": "open",
                "result": {"artifact_uri": "artifact://operator/open.json"},
            },
            {
                "id": "screenshot_page",
                "uri": "browser://chrome/page/screenshot",
                "operation": "screenshot",
                "result": {"artifact_uri": "artifact://operator/screenshot.json"},
            },
        ]
    }

    assert _extract_screenshot_artifact(result) == "artifact://operator/screenshot.json"

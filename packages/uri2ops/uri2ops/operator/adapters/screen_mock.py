from __future__ import annotations

from typing import Any

from uri2ops.operator.artifacts import write_artifact


def observe(payload: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    artifact_uri = write_artifact(payload.get("step_id", "screen_observe"), {"screen": "mock", "target_uri": payload.get("target_uri")})
    return {"ok": True, "screenshot_uri": artifact_uri, "artifact_uri": artifact_uri, "tree_json": "{}"}

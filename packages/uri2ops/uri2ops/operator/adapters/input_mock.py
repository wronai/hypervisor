from __future__ import annotations

from typing import Any

from uri2ops.operator.artifacts import write_artifact


def type_text(payload: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    secret = bool(payload.get("secret", False))
    text = "***" if secret else payload.get("text", "")
    artifact_uri = write_artifact(payload.get("step_id", "type_text"), {"text": text, "secret": secret})
    return {"ok": True, "typed": text, "artifact_uri": artifact_uri}

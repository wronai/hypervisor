from __future__ import annotations

from typing import Any

from uri2ops.operator.artifacts import write_artifact


def _artifact_root(context: dict[str, Any] | None) -> str | None:
    if not context:
        return None
    return context.get("root")


def open_page(payload: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    url = payload.get("url") or payload.get("target_uri")
    artifact_uri = write_artifact(
        payload.get("step_id", "open_page"),
        {"url": url, "adapter": "mock"},
        root=_artifact_root(context),
    )
    return {"ok": True, "url": url, "artifact_uri": artifact_uri, "text": "ok"}


def extract_dom(payload: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    text = payload.get("mock_text", "ok")
    artifact_uri = write_artifact(
        payload.get("step_id", "extract_dom"),
        {"text": text, "html": f"<body>{text}</body>"},
        root=_artifact_root(context),
    )
    return {"ok": True, "text": text, "html": f"<body>{text}</body>", "artifact_uri": artifact_uri}


def screenshot(payload: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    artifact_uri = write_artifact(
        payload.get("step_id", "screenshot"),
        {"screenshot": "mock", "target_uri": payload.get("target_uri")},
        root=_artifact_root(context),
    )
    return {"ok": True, "screenshot_uri": artifact_uri, "artifact_uri": artifact_uri}


def click(payload: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    artifact_uri = write_artifact(
        payload.get("step_id", "click"),
        {"selector": payload.get("selector"), "x": payload.get("x"), "y": payload.get("y")},
        root=_artifact_root(context),
    )
    return {"ok": True, "artifact_uri": artifact_uri}

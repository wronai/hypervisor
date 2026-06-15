from __future__ import annotations

from typing import Any

from uri2ops.operator.artifacts import write_artifact


def _artifact_root(context: dict[str, Any] | None) -> str | None:
    if not context:
        return None
    return context.get("root")


def _session(context: dict[str, Any] | None) -> dict[str, Any]:
    if not context:
        return {}
    session = context.setdefault("session", {})
    return session if isinstance(session, dict) else {}


def _mock_page_text(url: Any) -> str:
    text_url = str(url or "")
    if "supplier-portal.example.local/reports/monthly" in text_url:
        return "supplier portal monthly report: csv export ready"
    return "ok"


def open_page(payload: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    url = payload.get("url") or payload.get("target_uri")
    text = _mock_page_text(url)
    session = _session(context)
    session["last_url"] = url
    session["page_text"] = text
    artifact_uri = write_artifact(
        payload.get("step_id", "open_page"),
        {"url": url, "adapter": "mock", "text": text},
        root=_artifact_root(context),
    )
    return {"ok": True, "url": url, "artifact_uri": artifact_uri, "text": text}


def extract_dom(payload: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    session = _session(context)
    text = payload.get("mock_text") or session.get("page_text") or _mock_page_text(
        session.get("last_url")
    )
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


def capture_page(payload: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    opened = open_page(payload, context)
    if not opened.get("ok"):
        return opened
    return screenshot(payload, context)


def click(payload: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    artifact_uri = write_artifact(
        payload.get("step_id", "click"),
        {"selector": payload.get("selector"), "x": payload.get("x"), "y": payload.get("y")},
        root=_artifact_root(context),
    )
    return {"ok": True, "artifact_uri": artifact_uri}

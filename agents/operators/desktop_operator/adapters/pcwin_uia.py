from __future__ import annotations

import json
import sys
from typing import Any

from agents.operators.desktop_operator.adapters.pcwin_uri import automation_id_from_payload, window_id_from_payload
from uri2ops.operator.artifacts import write_step_artifact


def _task_context(context: dict[str, Any] | None) -> tuple[str, str, str | None]:
    ctx = context or {}
    return str(ctx.get("task_id") or "task"), str(ctx.get("run_id") or "run"), ctx.get("root")


def uia_available() -> bool:
    if sys.platform != "win32":
        return False
    try:
        import pywinauto  # noqa: F401

        return True
    except ImportError:
        return False


def _session(context: dict[str, Any] | None) -> dict[str, Any]:
    return (context or {}).setdefault("session", {})


def _focused_window(context: dict[str, Any] | None):
    from pywinauto import Desktop

    session = _session(context)
    window = session.get("pcwin_window")
    if window is not None:
        return window
    raise RuntimeError("No focused window; run pcwin://window/{id}/focus first")


def focus(payload: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    if not uia_available():
        return {"ok": False, "error": "Windows UIA adapter requires Windows with pywinauto installed"}
    window_id = window_id_from_payload(payload)
    title = str(payload.get("title") or window_id)
    task_id, run_id, root = _task_context(context)
    step_id = str(payload.get("step_id") or "focus")
    from pywinauto import Desktop

    desktop = Desktop(backend="uia")
    matches = [item for item in desktop.windows() if title.lower() in item.window_text().lower()]
    if not matches and window_id.isdigit():
        matches = [item for item in desktop.windows() if str(item.handle) == window_id]
    if not matches:
        return {"ok": False, "error": f"window not found: {window_id!r}"}
    window = matches[0]
    window.set_focus()
    _session(context)["pcwin_window"] = window
    meta = {
        "ok": True,
        "window_id": window_id,
        "title": window.window_text(),
        "handle": window.handle,
        "focused": True,
    }
    _, artifact_uri = write_step_artifact(task_id, run_id, step_id, "focus.json", json.dumps(meta, indent=2), root=root)
    return {**meta, "artifact_uri": artifact_uri}


def click(payload: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    if not uia_available():
        return {"ok": False, "error": "Windows UIA adapter requires Windows with pywinauto installed"}
    automation_id = automation_id_from_payload(payload)
    task_id, run_id, root = _task_context(context)
    step_id = str(payload.get("step_id") or "click")
    try:
        window = _focused_window(context)
    except RuntimeError as exc:
        return {"ok": False, "error": str(exc)}
    control = None
    for candidate in window.descendants():
        element = candidate.element_info
        auto_id = getattr(element, "automation_id", "") or ""
        name = getattr(element, "name", "") or ""
        if automation_id in {auto_id, name}:
            control = candidate
            break
    if control is None:
        return {"ok": False, "error": f"control not found: {automation_id!r}"}
    control.click_input()
    meta = {"ok": True, "automation_id": automation_id, "clicked": True, "control_name": control.window_text()}
    _, artifact_uri = write_step_artifact(task_id, run_id, step_id, "click.json", json.dumps(meta, indent=2), root=root)
    return {**meta, "artifact_uri": artifact_uri}

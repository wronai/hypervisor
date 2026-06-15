from __future__ import annotations

import json
import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

WEBHOOK_LOG_RELATIVE = "output/logs/hypervisor-webhook.jsonl"
LOG_EVENT_SCHEMA = "schemas/log_event.schema.json"


# Prefer shared if available (from main hypervisor package); fallback for standalone.
try:
    from hypervisor.deployment_registry.runtime_state import now_iso as _now_iso
except Exception:  # noqa: BLE001
    from datetime import UTC, datetime
    def _now_iso() -> str:
        return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _safe_slug(value: Any, default: str = "webhook") -> str:
    text = str(value or default).strip().lower()
    text = re.sub(r"[^a-z0-9_.-]+", "-", text).strip("-._")
    return text[:80] or default


def _event_name(payload: dict[str, Any]) -> str:
    return str(
        payload.get("event")
        or payload.get("status")
        or payload.get("alert")
        or payload.get("type")
        or "monitor.webhook"
    )


def _summary(payload: dict[str, Any], event: str) -> str:
    return str(
        payload.get("summary")
        or payload.get("message")
        or payload.get("detail")
        or event
    )[:240]


def _monitor_path(root: Path, source: str) -> Path:
    return root / "output" / "monitoring" / f"webhook-{_safe_slug(source)}.json"


def _write_log_event(
    root: Path,
    *,
    event: str,
    summary: str,
    source: str,
    snapshot_path: Path,
    payload: dict[str, Any],
) -> Path:
    path = root / WEBHOOK_LOG_RELATIVE
    path.parent.mkdir(parents=True, exist_ok=True)
    level = "INFO" if bool(payload.get("ok", True)) else "WARNING"
    entry: dict[str, Any] = {
        "$schema": LOG_EVENT_SCHEMA,
        "apiVersion": "uri3.io/v1",
        "kind": "LogEvent",
        "timestamp": _now_iso(),
        "level": level,
        "logger": "hypervisor.monitor.webhook",
        "message": summary,
        "uri": {
            "self": f"log://file/{WEBHOOK_LOG_RELATIVE}",
            "subject": payload.get("uri") or payload.get("url") or f"monitor://{source}",
        },
        "event": {
            "code": "MONITOR_WEBHOOK_RECEIVED",
            "message": summary,
        },
        "fields": {
            "event": event,
            "source": source,
            "snapshot": str(snapshot_path.relative_to(root)),
        },
    }
    with open(path, "a", encoding="utf-8") as handle:
        handle.write(json.dumps(entry, ensure_ascii=False) + "\n")
    return path


def write_monitor_webhook(payload: dict[str, Any], *, root: Path) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise ValueError("webhook payload must be a JSON object")
    source = str(payload.get("source") or payload.get("monitor") or payload.get("agent_id") or "webhook")
    event = _event_name(payload)
    summary = _summary(payload, event)
    checked_at = str(payload.get("checked_at") or payload.get("timestamp") or _now_iso())
    snapshot = {
        "status": event,
        "alert": payload.get("alert") or event,
        "summary": summary,
        "checked_at": checked_at,
        "url": payload.get("url") or payload.get("uri"),
        "agent_id": payload.get("agent_id"),
        "source": source,
        "webhook": payload,
    }
    path = _monitor_path(root, source)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(snapshot, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    log_path = _write_log_event(
        root,
        event=event,
        summary=summary,
        source=source,
        snapshot_path=path,
        payload=payload,
    )
    return {
        "ok": True,
        "result_type": "monitor_webhook",
        "event": event,
        "summary": summary,
        "source": source,
        "snapshot_path": str(path),
        "log_path": str(log_path),
        "view_hint": "/api/events",
    }

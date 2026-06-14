from __future__ import annotations

import json
import time
from typing import Any, Callable

from urish.backends.call import call_uri
from urish.backends.logs import read_log_uri


def watch_uri(
    target: str,
    *,
    interval: float = 2.0,
    max_events: int = 0,
    on_event: Callable[[dict[str, Any]], None] | None = None,
) -> dict[str, Any]:
    uri = _normalize_watch_uri(target)
    events: list[dict[str, Any]] = []
    seen = 0
    while True:
        event = _poll_once(uri)
        events.append(event)
        seen += 1
        if on_event is not None:
            on_event(event)
        if max_events and seen >= max_events:
            break
        time.sleep(interval)
    return {
        "ok": True,
        "workflow_status": "completed",
        "execution_status": "completed",
        "service_result_status": "succeeded",
        "result_type": "watch",
        "data": {"uri": uri, "events": events, "count": len(events)},
        "meta": {"runtime": "urish", "transport": "watch", "target": uri},
    }


def _normalize_watch_uri(target: str) -> str:
    if "://" in target:
        return target
    return f"health://agent/{target}"


def _poll_once(uri: str) -> dict[str, Any]:
    if uri.startswith("log://"):
        result = read_log_uri(uri)
        payload = result.get("data") or {}
        return {
            "kind": "RuntimeEvent",
            "event_type": "log.snapshot",
            "uri": uri,
            "data": payload.get("summary") or payload,
        }
    result = call_uri(uri, {})
    return {
        "kind": "RuntimeEvent",
        "event_type": _event_type(result),
        "uri": uri,
        "correlation_id": (result.get("meta") or {}).get("correlation_id"),
        "data": result.get("data") or {},
        "ok": result.get("ok"),
    }


def _event_type(result: dict[str, Any]) -> str:
    if not result.get("ok"):
        return "agent.health.failed"
    return "agent.health.ok"


def render_event(event: dict[str, Any], *, json_out: bool = False) -> str:
    if json_out:
        return json.dumps(event, indent=2, ensure_ascii=False)
    ok = event.get("ok")
    prefix = "OK" if ok is not False else "FAIL"
    return f"{prefix} {event.get('event_type', 'event')} {event.get('uri', '')}"

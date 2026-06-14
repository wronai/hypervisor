from __future__ import annotations

import asyncio
import json
from typing import Any, Callable

import httpx


def stream_uri(
    target: str,
    *,
    max_events: int = 0,
    timeout: float = 30.0,
    on_event: Callable[[dict[str, Any]], None] | None = None,
) -> dict[str, Any]:
    if target.startswith("ws://") or target.startswith("wss://"):
        return _stream_ws(target, max_events=max_events, timeout=timeout, on_event=on_event)
    url = target if target.startswith(("http://", "https://", "sse://")) else target.replace("sse://", "http://", 1)
    if url.startswith("sse://"):
        url = url.replace("sse://", "http://", 1)
    return _stream_sse(url, max_events=max_events, timeout=timeout, on_event=on_event)


def _stream_sse(
    url: str,
    *,
    max_events: int,
    timeout: float,
    on_event: Callable[[dict[str, Any]], None] | None,
) -> dict[str, Any]:
    events: list[dict[str, Any]] = []
    try:
        with httpx.stream("GET", url, timeout=timeout) as response:
            if response.status_code >= 400:
                return _error(f"HTTP {response.status_code} for {url}")
            for line in response.iter_lines():
                if not line or not line.startswith("data:"):
                    continue
                body = line.split(":", 1)[1].strip()
                if not body:
                    continue
                try:
                    parsed = json.loads(body)
                    event = parsed if isinstance(parsed, dict) else {"data": parsed}
                except json.JSONDecodeError:
                    event = {"data": body}
                envelope = _runtime_event(url, event)
                events.append(envelope)
                if on_event is not None:
                    on_event(envelope)
                if max_events and len(events) >= max_events:
                    break
    except httpx.HTTPError as exc:
        return _error(str(exc))
    return _success(url, events, transport="sse")


def _stream_ws(
    target: str,
    *,
    max_events: int,
    timeout: float,
    on_event: Callable[[dict[str, Any]], None] | None,
) -> dict[str, Any]:
    try:
        import websockets
    except ImportError:
        return _error("install websockets package for ws:// stream")

    events: list[dict[str, Any]] = []

    async def _run() -> None:
        async with websockets.connect(target) as websocket:
            while True:
                raw = await asyncio.wait_for(websocket.recv(), timeout=timeout)
                try:
                    parsed = json.loads(raw)
                    payload = parsed if isinstance(parsed, dict) else {"data": parsed}
                except json.JSONDecodeError:
                    payload = {"data": raw}
                envelope = _runtime_event(target, payload)
                events.append(envelope)
                if on_event is not None:
                    on_event(envelope)
                if max_events and len(events) >= max_events:
                    break

    try:
        asyncio.run(_run())
    except Exception as exc:  # noqa: BLE001
        return _error(str(exc))
    return _success(target, events, transport="ws")


def _runtime_event(uri: str, payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "kind": "RuntimeEvent",
        "event_type": payload.get("event_type") or payload.get("type") or "stream.event",
        "uri": uri,
        "correlation_id": payload.get("correlation_id"),
        "data": payload.get("data", payload),
    }


def _success(uri: str, events: list[dict[str, Any]], *, transport: str) -> dict[str, Any]:
    return {
        "ok": True,
        "workflow_status": "completed",
        "execution_status": "completed",
        "service_result_status": "succeeded",
        "result_type": "stream",
        "data": {"events": events, "count": len(events), "uri": uri},
        "meta": {"runtime": "urish", "transport": transport, "target": uri},
    }


def _error(message: str) -> dict[str, Any]:
    return {
        "ok": False,
        "workflow_status": "failed",
        "execution_status": "failed",
        "service_result_status": "failed",
        "result_type": "stream",
        "error": message,
        "meta": {"runtime": "urish", "transport": "stream"},
    }

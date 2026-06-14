from __future__ import annotations

from pathlib import Path
from typing import Any
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

import httpx

from hypervisor.deployment_registry.port_utils import foreign_service_detail


def _probe_payload_ok(
    payload: Any,
    *,
    response_ok: bool,
    expected_agent: str | None,
) -> bool:
    if not response_ok:
        return False
    if not isinstance(payload, dict):
        return True
    if payload.get("ok") is False:
        return False
    if not expected_agent:
        return True
    agent_name = payload.get("agent")
    if agent_name is not None and str(agent_name) != expected_agent:
        return False
    if agent_name is None and response_ok and payload.get("service"):
        return False
    return True


def _probe_response(uri: str, response: httpx.Response, *, expected_agent: str | None) -> dict[str, Any]:
    content_type = response.headers.get("content-type", "")
    payload = response.json() if "json" in content_type else None
    json_ok = payload.get("ok") if isinstance(payload, dict) else None
    agent_name = payload.get("agent") if isinstance(payload, dict) else None
    ok = _probe_payload_ok(payload, response_ok=response.is_success, expected_agent=expected_agent)
    foreign = None
    if not ok and isinstance(payload, dict):
        foreign = foreign_service_detail({"payload": payload})
    return {
        "uri": uri,
        "ok": ok,
        "status_code": response.status_code,
        "json_ok": json_ok,
        "agent": agent_name,
        "payload": payload if isinstance(payload, dict) else None,
        "foreign_service": foreign,
    }


def probe_http(
    uri: str | None,
    *,
    timeout: float,
    expected_agent: str | None = None,
) -> dict[str, Any]:
    if not uri or not uri.startswith(("http://", "https://")):
        return {"uri": uri, "ok": False, "skipped": True, "reason": "missing http uri"}
    try:
        response = httpx.get(uri, timeout=timeout)
        return _probe_response(uri, response, expected_agent=expected_agent)
    except Exception as exc:
        return {"uri": uri, "ok": False, "error": str(exc)}


def log_uri_with_filters(log_uri: str, *, limit: int, level: str = "ERROR") -> str:
    parsed = urlsplit(log_uri)
    query = dict(parse_qsl(parsed.query, keep_blank_values=True))
    query.setdefault("level", level)
    query["limit"] = str(limit)
    return urlunsplit((parsed.scheme, parsed.netloc, parsed.path, urlencode(query), parsed.fragment))


def read_error_logs(log_uri: str, *, root: Path, limit: int) -> dict[str, Any]:
    filtered = log_uri_with_filters(log_uri, limit=limit)
    try:
        from uri3.logs.reader import read_logs_result, summarize_logs

        summary = summarize_logs(filtered, root=root)
        entries = read_logs_result(filtered, root=root)
        if isinstance(entries, dict):
            log_entries = entries.get("entries") or []
            hint = entries.get("hint")
        else:
            log_entries = entries
            hint = ""
        return {
            "uri": filtered,
            "summary": summary,
            "entries": log_entries[-limit:],
            "hint": hint,
            "error_count": len(log_entries),
        }
    except Exception as exc:
        return {"uri": filtered, "summary": {}, "entries": [], "error": str(exc), "error_count": 0}

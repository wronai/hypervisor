from __future__ import annotations

from typing import Any

import httpx
from uri3.results import ServiceResult, service_result

from uri2run.result import error_result
from uri2run.transports.protocol_url import protocol_to_http_url


def _a2a_endpoint(target: str, payload: dict[str, Any]) -> tuple[str, str]:
    action = str(payload.get("action") or "").lower()
    base = protocol_to_http_url(target)
    if action == "agent_card" or "agent-card" in base:
        if base.endswith("agent-card.json"):
            return "GET", base
        return "GET", f"{base.rstrip('/')}/.well-known/agent-card.json"
    if action == "tasks" or payload.get("task") is not None:
        return "POST", base if base.endswith("/a2a/tasks") else f"{base.rstrip('/')}/a2a/tasks"
    if base.endswith("/tasks"):
        return "POST", base
    return "GET", f"{base.rstrip('/')}/.well-known/agent-card.json"


def run_a2a(target: str, payload: dict[str, Any], context: dict[str, Any]) -> ServiceResult:
    timeout = float(payload.get("timeout", context.get("timeout", 10.0)))
    try:
        method, url = _a2a_endpoint(target, payload)
    except ValueError as exc:
        return error_result("A2A_URI_INVALID", str(exc), result_type="a2a")

    headers = payload.get("headers") if isinstance(payload.get("headers"), dict) else None
    request_kwargs: dict[str, Any] = {"timeout": timeout}
    if headers:
        request_kwargs["headers"] = headers

    if method == "GET":
        params = payload.get("params")
        request_kwargs["params"] = params if isinstance(params, dict) else None
    else:
        body = payload.get("json")
        if body is None:
            body = {
                "task": payload.get("task"),
                "dry_run": payload.get("dry_run", False),
                "approve": payload.get("approve", False),
                "adapter": payload.get("adapter", "mock"),
            }
        request_kwargs["json"] = body

    try:
        request_kwargs = {key: value for key, value in request_kwargs.items() if value is not None}
        response = httpx.request(method, url, **request_kwargs)
    except httpx.HTTPError as exc:
        return error_result("A2A_TRANSPORT_FAILED", str(exc), result_type="a2a")

    content_type = response.headers.get("content-type", "")
    if "application/json" in content_type:
        try:
            body = response.json()
        except ValueError:
            body = {"raw": response.text}
    else:
        body = response.text

    return service_result(
        ok=200 <= response.status_code < 400,
        result_type="a2a",
        data={
            "status_code": response.status_code,
            "url": url,
            "method": method,
            "body": body,
        },
        meta={"transport": "a2a", "target": target},
    )


def run_a2a_transport(
    backend: dict[str, Any],
    payload: dict[str, Any],
    context: dict[str, Any],
) -> ServiceResult:
    target = backend.get("target") or backend.get("url")
    if not target:
        return error_result("BACKEND_INVALID", "a2a backend missing target/url")
    return run_a2a(str(target), payload, context)

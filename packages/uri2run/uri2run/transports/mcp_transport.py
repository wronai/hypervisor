from __future__ import annotations

from typing import Any

import httpx
from uri3.results import ServiceResult, service_result

from uri2run.result import error_result
from uri2run.transports.protocol_url import protocol_to_http_url


def _mcp_endpoint(target: str, payload: dict[str, Any]) -> tuple[str, str]:
    action = str(payload.get("action") or "").lower()
    base = protocol_to_http_url(target)
    if action == "list_tools" or base.endswith("/tools"):
        return "GET", base if base.endswith("/tools") else f"{base.rstrip('/')}/mcp/tools"
    if action == "call_tool" or payload.get("name"):
        return "POST", (
            base if base.endswith("/tools/call") else f"{base.rstrip('/')}/mcp/tools/call"
        )
    if base.endswith("/tools/list"):
        return "GET", base
    return "POST", f"{base.rstrip('/')}/mcp/tools/call"


def run_mcp(target: str, payload: dict[str, Any], context: dict[str, Any]) -> ServiceResult:
    timeout = float(payload.get("timeout", context.get("timeout", 10.0)))
    try:
        method, url = _mcp_endpoint(target, payload)
    except ValueError as exc:
        return error_result("MCP_URI_INVALID", str(exc), result_type="mcp")

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
                "name": payload.get("name"),
                "arguments": payload.get("arguments") or payload.get("args") or {},
            }
        request_kwargs["json"] = body

    try:
        request_kwargs = {key: value for key, value in request_kwargs.items() if value is not None}
        response = httpx.request(method, url, **request_kwargs)
    except httpx.HTTPError as exc:
        return error_result("MCP_TRANSPORT_FAILED", str(exc), result_type="mcp")

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
        result_type="mcp",
        data={
            "status_code": response.status_code,
            "url": url,
            "method": method,
            "body": body,
        },
        meta={"transport": "mcp", "target": target},
    )


def run_mcp_transport(
    backend: dict[str, Any],
    payload: dict[str, Any],
    context: dict[str, Any],
) -> ServiceResult:
    target = backend.get("target") or backend.get("url")
    if not target:
        return error_result("BACKEND_INVALID", "mcp backend missing target/url")
    return run_mcp(str(target), payload, context)

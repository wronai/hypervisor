from __future__ import annotations

from typing import Any

import httpx

from uri3.results import service_result


def _response_data(response: httpx.Response) -> Any:
    content_type = response.headers.get("content-type", "")
    if "application/json" in content_type:
        return response.json()
    return response.text


def run_http(target: str, payload: dict[str, Any], context: dict[str, Any]):
    del context
    method = str(payload.get("method") or "GET").upper()
    timeout = float(payload.get("timeout", 10.0))
    json_body = payload.get("json")
    params = payload.get("params") if isinstance(payload.get("params"), dict) else None
    response = httpx.request(method, target, json=json_body, params=params, timeout=timeout)
    return service_result(
        ok=200 <= response.status_code < 400,
        result_type="http",
        data={
            "status_code": response.status_code,
            "headers": dict(response.headers),
            "body": _response_data(response),
        },
        meta={"transport": "http", "method": method},
    )

from __future__ import annotations

import json
from typing import Any

import yaml

_SUMMARY_RESULT_TYPES = frozenset(
    {
        "view",
        "health",
        "repair",
        "diagnosis",
        "runtime_state",
        "logs",
        "http",
        "plan",
        "workflow",
        "system_uri",
        "dry_run",
    }
)


def _render_browser_page_result(result: dict[str, Any], output: str) -> str | None:
    try:
        from uri2ops.server.renderers.browser_page import (
            is_browser_page_result,
            normalize_render_format,
            render_browser_page,
        )
    except ImportError:
        return None

    data = result.get("data")
    page = data if isinstance(data, dict) and is_browser_page_result(data) else None
    if page is None and is_browser_page_result(result):
        page = result
    if page is None:
        return None
    try:
        fmt = normalize_render_format(output)
        if fmt is None:
            return None
        body, _media_type = render_browser_page(page, fmt)
        if isinstance(body, bytes):
            return body.decode("utf-8", errors="replace")
        return body
    except (ValueError, RuntimeError):
        return None


def render_result(result: dict[str, Any], *, output: str = "json", quiet: bool = False) -> str:
    if output == "json":
        return json.dumps(result, indent=2, ensure_ascii=False)
    if output == "yaml":
        return yaml.safe_dump(result, sort_keys=False, allow_unicode=True)
    if output == "raw":
        data = result.get("data")
        if isinstance(data, str):
            return data
        if isinstance(data, dict) and "stdout" in data:
            return str(data.get("stdout") or "")
        return json.dumps(data, ensure_ascii=False)
    browser_render = _render_browser_page_result(result, output)
    if browser_render is not None:
        return browser_render
    if output == "text" or quiet:
        return _render_text(result, quiet=quiet)
    return _render_table(result)


def _unwrap_system_body(result: dict[str, Any]) -> dict[str, Any] | None:
    # Use centralized unwrap_data where possible to reduce cross-boundary dup.
    try:
        from uri3.results.envelope import unwrap_data
        candidate = unwrap_data(result)
        if isinstance(candidate, dict):
            inner_type = candidate.get("result_type")
            if inner_type in _SUMMARY_RESULT_TYPES:
                return candidate
            if result.get("result_type") in _SUMMARY_RESULT_TYPES:
                return result
    except Exception:  # noqa: BLE001
        pass
    # Fallback original logic
    data = result.get("data")
    if isinstance(data, dict):
        inner_type = data.get("result_type")
        if inner_type in _SUMMARY_RESULT_TYPES:
            return data
    if result.get("result_type") in _SUMMARY_RESULT_TYPES:
        return result
    return None


def _view_model(body: dict[str, Any]) -> dict[str, Any]:
    nested = body.get("data")
    return nested if isinstance(nested, dict) else body


def _render_view_fallback(body: dict[str, Any]) -> str | None:
    if body.get("result_type") != "view":
        return None
    model = _view_model(body)
    lines = [f"## {body.get('title') or 'View'}"]
    if body.get("view_uri"):
        lines.append(f"View: `{body['view_uri']}`")
    lines.append("")
    fields = {
        "agent": model.get("agent_id"),
        "service": model.get("service_status"),
        "process": model.get("process_status"),
        "health": model.get("health_status"),
        "port": model.get("effective_port"),
        "health_uri": model.get("effective_health_uri"),
        "recommended": model.get("recommended_action"),
    }
    for label, value in fields.items():
        if value not in (None, ""):
            lines.append(f"- **{label}:** `{value}`")
    incidents = model.get("incidents") or []
    if incidents:
        lines.append("\n### Incidents")
        for item in incidents[:6]:
            if isinstance(item, dict):
                lines.append(f"- `{item.get('code')}` {item.get('detail', '')}".rstrip())
    return "\n".join(lines).strip()


def _render_system_summary(body: dict[str, Any]) -> str | None:
    try:
        from hypervisor_dashboard_agent.chat_format import format_uri_result_summary

        return format_uri_result_summary(body)
    except ImportError:
        return _render_view_fallback(body)


def _render_data_dict_lines(data: dict[str, Any]) -> list[str]:
    if "stdout" in data and data["stdout"]:
        return ["stdout:", str(data["stdout"]).rstrip()]
    if "text" in data:
        return [str(data["text"])]
    if "message_markdown" in data:
        return [str(data["message_markdown"])]
    if "planned_uris" in data:
        planned = data.get("planned_uris") or []
        return ["planned URIs:", *(f"- {uri}" for uri in planned[:8])]
    if "detected_kind" in data:
        lines = [f"detected: {data.get('detected_kind')} / {data.get('detected_subtype')}"]
        lines.extend(f"- {uri}" for uri in (data.get("planned_uris") or [])[:6])
        return lines
    return []


def _render_envelope_text(result: dict[str, Any]) -> str:
    ok = "OK" if result.get("ok") else "FAIL"
    wf = result.get("workflow_status", "-")
    svc = result.get("service_result_status", "-")
    rtype = result.get("result_type", "-")
    duration = (result.get("meta") or {}).get("duration_ms", "-")
    lines = [f"{ok} {wf}/{svc} {rtype} {duration}ms"]
    data = result.get("data")
    if isinstance(data, dict):
        lines.extend(_render_data_dict_lines(data))
    elif data is not None:
        lines.append(str(data))
    error = result.get("error")
    if error:
        lines.append(f"error: {error}")
    return "\n".join(lines)


def _render_text(result: dict[str, Any], *, quiet: bool) -> str:
    if quiet:
        return "ok" if result.get("ok") else "failed"

    body = _unwrap_system_body(result)
    if body is not None:
        summary = _render_system_summary(body)
        if summary:
            return summary

    return _render_envelope_text(result)


def _render_table(result: dict[str, Any]) -> str:
    return _render_text(result, quiet=False)

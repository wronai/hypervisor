from __future__ import annotations

from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from hypervisor_dashboard_agent.chat_format import format_uri_result_markdown
from hypervisor_dashboard_agent.uri_client import resolve_view_uri


def _uri_path_parts(uri: str) -> list[str]:
    parsed = urlparse(uri)
    if parsed.netloc:
        combined = f"{parsed.netloc}/{parsed.path.lstrip('/')}"
    else:
        combined = parsed.path.lstrip("/")
    return [part for part in combined.split("/") if part]


def source_view_uri(presentation_uri: str) -> str:
    """Map html:// or markdown:// URIs to their underlying view:// source."""
    parsed = urlparse(presentation_uri)
    if parsed.scheme not in {"html", "markdown"}:
        raise ValueError(f"unsupported presentation URI scheme: {presentation_uri}")
    parts = _uri_path_parts(presentation_uri)
    if parts[:1] == ["view"]:
        parts = parts[1:]
    if len(parts) < 4 or parts[0] != "process" or parts[1] != "agent" or parts[3] != "latest":
        raise ValueError(
            "presentation URI must target a process view, e.g. "
            "html://view/process/agent/weather-map-agent.local/latest"
        )
    return "view://" + "/".join(parts)


def resolve_html_presentation(presentation_uri: str, *, root: Path | None = None) -> dict[str, Any]:
    source_uri = source_view_uri(presentation_uri)
    envelope = resolve_view_uri(source_uri, root=root)
    payload = envelope.to_dict()
    payload.update(
        {
            "ok": True,
            "workflow_status": "completed",
            "service_result_status": "succeeded",
            "result_type": "html",
            "presentation_uri": presentation_uri,
            "source_uri": source_uri,
            "content_type": "text/html",
        }
    )
    return payload


def resolve_markdown_presentation(
    presentation_uri: str,
    *,
    root: Path | None = None,
) -> dict[str, Any]:
    source_uri = source_view_uri(presentation_uri)
    envelope = resolve_view_uri(source_uri, root=root)
    view_payload = envelope.to_dict()
    view_payload.update(
        {
            "ok": True,
            "workflow_status": "completed",
            "service_result_status": "succeeded",
        }
    )
    markdown = format_uri_result_markdown(view_payload, include_envelope=False)
    return {
        "ok": True,
        "workflow_status": "completed",
        "service_result_status": "succeeded",
        "result_type": "markdown",
        "presentation_uri": presentation_uri,
        "source_uri": source_uri,
        "content_type": "text/markdown",
        "presentation_markdown": markdown,
        "title": envelope.title,
        "view_uri": envelope.view_uri,
        "data": envelope.data,
    }

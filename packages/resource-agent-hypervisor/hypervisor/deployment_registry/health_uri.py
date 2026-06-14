from __future__ import annotations

import re
from typing import Any
from urllib.parse import urlparse


def port_from_http_uri(uri: str | None) -> int | None:
    if not uri:
        return None
    parsed = urlparse(uri)
    if parsed.port is not None:
        return parsed.port
    if parsed.scheme == "http":
        return 80
    if parsed.scheme == "https":
        return 443
    return None


def port_from_command(command: str | None) -> int | None:
    if not command:
        return None
    match = re.search(r"--port(?:=|\s+)(\d+)", command)
    return int(match.group(1)) if match else None


def health_uri_for_port(port: int) -> str:
    return f"http://localhost:{port}/health"


def resolve_effective_health_uri(state: dict[str, Any], plan: dict[str, Any]) -> str:
    command = str(state.get("command") or plan.get("command_string") or "")
    command_port = port_from_command(command)
    if command_port is not None:
        return health_uri_for_port(command_port)
    return str(state.get("health_uri") or plan.get("health_uri") or "")


def command_port_from_runtime(state: dict[str, Any], plan: dict[str, Any]) -> int | None:
    command = str(state.get("command") or plan.get("command_string") or "")
    return port_from_command(command)

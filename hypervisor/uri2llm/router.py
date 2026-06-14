from __future__ import annotations

from dataclasses import dataclass
from urllib.parse import urlparse
from typing import Any

from .env_resolver import resolve_env
from .llm_resolver import resolve_llm
from .function_resolver import call_python, resolve_python
from .protocol_resolver import resolve_http_like, resolve_a2a, resolve_mcp, resolve_resource
from .pypi_resolver import resolve_pypi


@dataclass
class UriResolution:
    uri: str
    scheme: str
    kind: str
    target: Any
    metadata: dict[str, Any]


def resolve(uri: str) -> UriResolution:
    parsed = urlparse(uri)
    scheme = parsed.scheme
    if not scheme:
        raise ValueError(f"URI has no scheme: {uri}")
    if scheme == "env":
        return UriResolution(uri, scheme, "env", resolve_env(uri), {})
    if scheme == "llm":
        return UriResolution(uri, scheme, "llm", resolve_llm(uri), {})
    if scheme == "python":
        return UriResolution(uri, scheme, "python", resolve_python(uri), {})
    if scheme == "pypi":
        return UriResolution(uri, scheme, "pypi", resolve_pypi(uri), {})
    if scheme in {"http", "https"}:
        return UriResolution(uri, scheme, "http", resolve_http_like(uri), {})
    if scheme == "a2a":
        return UriResolution(uri, scheme, "a2a", resolve_a2a(uri), {})
    if scheme == "mcp":
        return UriResolution(uri, scheme, "mcp", resolve_mcp(uri), {})
    if scheme in {"resource", "domain", "artifact", "command", "event", "input"}:
        return UriResolution(uri, scheme, scheme, resolve_resource(uri), {})
    raise ValueError(f"Unsupported URI scheme: {scheme}")


def call(uri: str, payload: dict[str, Any] | None = None) -> Any:
    parsed = urlparse(uri)
    if parsed.scheme == "python":
        return call_python(uri, payload or {})
    raise ValueError(f"URI scheme is resolvable but not callable by local router: {parsed.scheme}")

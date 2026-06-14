from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from urllib.parse import urlparse

from uri3.resolvers.env_resolver import call_env, resolve_env
from uri3.resolvers.log_resolver import resolve_log
from uri3.resolvers.llm_resolver import resolve_llm
from uri3.resolvers.python_resolver import call_python, resolve_python
from uri3.resolvers.protocol_resolver import (
    resolve_a2a,
    resolve_http_like,
    resolve_mcp,
    resolve_resource,
)
from uri3.resolvers.pypi_resolver import resolve_pypi


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
    if scheme == "log":
        return UriResolution(uri, scheme, "log", resolve_log(uri), {})
    if scheme in {"http", "https"}:
        return UriResolution(uri, scheme, "http", resolve_http_like(uri), {})
    if scheme == "a2a":
        return UriResolution(uri, scheme, "a2a", resolve_a2a(uri), {})
    if scheme == "mcp":
        return UriResolution(uri, scheme, "mcp", resolve_mcp(uri), {})
    if scheme == "docker":
        from uri3.resolvers.docker_resolver import resolve_docker

        return UriResolution(uri, scheme, "docker", resolve_docker(uri), {})
    if scheme in {"resource", "domain", "artifact", "command", "event", "input", "agent", "local", "ssh", "git"}:
        return UriResolution(uri, scheme, scheme, resolve_resource(uri), {})
    raise ValueError(f"Unsupported URI scheme: {scheme}")


def call(uri: str, payload: dict[str, Any] | None = None) -> Any:
    parsed = urlparse(uri)
    if parsed.scheme == "python":
        return call_python(uri, payload or {})
    if parsed.scheme == "env":
        return call_env(uri, payload)
    if parsed.scheme == "docker":
        from uri3.docker.controller import control_docker

        return control_docker(uri, payload=payload)
    if parsed.scheme == "log":
        from uri3.logs.reader import read_logs, summarize_logs

        options = payload or {}
        if options.get("summary"):
            return summarize_logs(uri)
        return read_logs(uri)
    raise ValueError(f"URI scheme is resolvable but not callable by local router: {parsed.scheme}")


class Uri3Router:
    def __init__(self):
        from uri3.resolvers.env_resolver import EnvResolver
        from uri3.resolvers.http_resolver import HttpResolver
        from uri3.resolvers.log_resolver import LogResolver
        from uri3.resolvers.llm_resolver import LLMResolver
        from uri3.resolvers.python_resolver import PythonResolver

        self.resolvers = {
            "env": EnvResolver(),
            "llm": LLMResolver(),
            "log": LogResolver(),
            "python": PythonResolver(),
            "http": HttpResolver(),
            "https": HttpResolver(),
        }

    def resolve(self, uri):
        try:
            return resolve(uri)
        except ValueError as exc:
            scheme = urlparse(uri).scheme
            return {
                "uri": uri,
                "scheme": scheme,
                "status": "unresolved",
                "reason": str(exc),
            }

    def call(self, uri, payload=None):
        return call(uri, payload)

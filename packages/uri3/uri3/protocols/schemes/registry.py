from __future__ import annotations

from typing import Any
from urllib.parse import urlparse

from uri3.protocols.schemes.constants import SUPPORTED_SCHEMES
from uri3.protocols.schemes.base import SchemeSpec
from uri3.protocols.schemes import a2a, docker, env, http, llm, log, mcp, python, pypi, resource_like


def _build_registry() -> dict[str, SchemeSpec]:
    specs = [
        log.spec(),
        env.spec(),
        python.spec(),
        llm.spec(),
        pypi.spec(),
        http.spec("http"),
        http.spec("https"),
        a2a.spec(),
        mcp.spec(),
        resource_like.resource_like_spec("resource", "Generic in-repo or logical resource reference."),
        resource_like.resource_like_spec("artifact", "Build or generation artifact reference."),
        resource_like.resource_like_spec("domain", "Domain pack or bounded context reference."),
        resource_like.resource_like_spec("agent", "Generated or deployed agent reference."),
        resource_like.resource_like_spec("local", "Local filesystem resource reference."),
        resource_like.resource_like_spec("input", "Pipeline input reference."),
        resource_like.resource_like_spec("command", "Command or action reference."),
        resource_like.resource_like_spec("event", "Event source or channel reference."),
        resource_like.resource_like_spec("ssh", "Remote host path accessed over SSH."),
        docker.spec(),
        resource_like.resource_like_spec("git", "Git repository reference."),
    ]
    return {spec.scheme: spec for spec in specs}


SCHEME_REGISTRY: dict[str, SchemeSpec] = _build_registry()


def normalize_scheme(value: str) -> str:
    raw = value.strip()
    if not raw:
        raise ValueError("Scheme or URI is required")
    if "://" in raw:
        scheme = urlparse(raw).scheme
        if scheme:
            return scheme.lower()
    return raw.rstrip(":/").lower()


def is_concrete_uri(value: str) -> bool:
    if "://" not in value:
        return False
    parsed = urlparse(value)
    return bool(parsed.netloc or parsed.path.strip("/") or parsed.query)


def get_scheme_schema(scheme_or_uri: str) -> dict[str, Any]:
    scheme = normalize_scheme(scheme_or_uri)
    if scheme not in SUPPORTED_SCHEMES:
        raise ValueError(f"Unsupported URI scheme: {scheme}")
    spec = SCHEME_REGISTRY.get(scheme)
    if spec is None:
        spec = resource_like.resource_like_spec(scheme, f"Supported scheme `{scheme}` without detailed schema yet.")
    return spec.to_dict()


def list_schemes(*, documented_only: bool = False) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for scheme in sorted(SUPPORTED_SCHEMES):
        spec = SCHEME_REGISTRY.get(scheme)
        if spec is None:
            items.append(
                {
                    "scheme": scheme,
                    "supported": True,
                    "documented": False,
                    "description": f"Supported scheme `{scheme}` without detailed schema yet.",
                    "template": f"{scheme}://{{target}}",
                }
            )
            continue
        if documented_only and not spec.documented:
            continue
        items.append(
            {
                "scheme": spec.scheme,
                "supported": True,
                "documented": spec.documented,
                "description": spec.description,
                "template": spec.template,
                "actions": list(spec.actions),
            }
        )
    return items


def _query_names(spec: SchemeSpec) -> set[str]:
    names: set[str] = set()
    for option in spec.query:
        names.add(option.name)
        names.update(option.aliases)
    return names


def _parse_instance(scheme: str, uri: str) -> dict[str, Any]:
    if scheme == "log":
        from uri3.resolvers.log_resolver import parse_log_uri

        ref = parse_log_uri(uri)
        return ref.to_dict()
    if scheme == "env":
        from uri3.resolvers.env_resolver import resolve_env

        return resolve_env(uri)
    if scheme == "python":
        from uri3.resolvers.python_resolver import resolve_python

        return resolve_python(uri)
    if scheme == "llm":
        from uri3.resolvers.llm_resolver import resolve_llm

        return resolve_llm(uri)
    if scheme == "pypi":
        from uri3.resolvers.pypi_resolver import resolve_pypi

        return resolve_pypi(uri)
    if scheme in {"http", "https"}:
        from uri3.resolvers.protocol_resolver import resolve_http_like

        return resolve_http_like(uri)
    if scheme == "a2a":
        from uri3.resolvers.protocol_resolver import resolve_a2a

        return resolve_a2a(uri)
    if scheme == "mcp":
        from uri3.resolvers.protocol_resolver import resolve_mcp

        return resolve_mcp(uri)
    if scheme == "docker":
        from uri3.resolvers.docker_resolver import resolve_docker

        return resolve_docker(uri)
    if scheme in {
        "resource",
        "artifact",
        "domain",
        "agent",
        "local",
        "input",
        "command",
        "event",
        "ssh",
        "git",
    }:
        from uri3.resolvers.ssh_resolver import resolve_ssh

        if scheme == "ssh":
            return resolve_ssh(uri)
        from uri3.resolvers.protocol_resolver import resolve_resource

        return resolve_resource(uri)
    raise ValueError(f"No parser available for scheme: {scheme}")


def analyze_uri(uri: str) -> dict[str, Any]:
    scheme = normalize_scheme(uri)
    schema = get_scheme_schema(scheme)
    spec = SCHEME_REGISTRY.get(scheme)
    parsed = urlparse(uri)
    query_keys = set(parsed.query.split("&")) if parsed.query else set()
    query_keys = {key.split("=", 1)[0] for key in query_keys if key}

    result: dict[str, Any] = {
        "uri": uri,
        "scheme": scheme,
        "schema": schema,
        "components": {
            "netloc": parsed.netloc,
            "path": parsed.path,
            "query": parsed.query,
        },
    }

    try:
        result["parsed"] = _parse_instance(scheme, uri)
        result["valid"] = True
        result["errors"] = []
    except ValueError as exc:
        result["parsed"] = None
        result["valid"] = False
        result["errors"] = [str(exc)]

    if spec and spec.query:
        known = _query_names(spec)
        canonical = {option.name for option in spec.query}
        used = sorted(key for key in query_keys if key in known)
        unknown = sorted(key for key in query_keys if key not in known)
        available = sorted(name for name in canonical if name not in used)
        result["query"] = {
            "used": used,
            "unknown": unknown,
            "available": available,
            "options": [option.to_dict() for option in spec.query],
        }
    else:
        result["query"] = {
            "used": sorted(query_keys),
            "unknown": [],
            "available": [],
            "options": [],
        }

    return result


def describe_uri(value: str) -> dict[str, Any]:
    if is_concrete_uri(value):
        return analyze_uri(value)
    return get_scheme_schema(value)

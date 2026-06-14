from __future__ import annotations

from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import yaml

from uri3.resolvers.router import resolve


URI_SCHEMES = {
    "env",
    "llm",
    "log",
    "python",
    "pypi",
    "http",
    "https",
    "a2a",
    "mcp",
    "resource",
    "artifact",
    "domain",
    "agent",
    "local",
    "input",
    "command",
    "event",
    "ssh",
    "docker",
    "git",
    "secret",
}


def is_uri(value: Any) -> bool:
    if not isinstance(value, str):
        return False
    if "://" not in value:
        return False
    scheme = urlparse(value).scheme
    return bool(scheme) and scheme in URI_SCHEMES


def load_uri_yaml(path: str | Path) -> dict[str, Any]:
    data = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"URI YAML must be a mapping: {path}")
    return data


def resolve_uri_values(
    value: Any,
    *,
    resolve_secrets: bool = False,
    _key: str | None = None,
) -> Any:
    if isinstance(value, dict):
        return {
            key: resolve_uri_values(item, resolve_secrets=resolve_secrets, _key=key)
            for key, item in value.items()
        }
    if isinstance(value, list):
        return [resolve_uri_values(item, resolve_secrets=resolve_secrets) for item in value]
    if value is None:
        return None
    if not is_uri(value):
        return value
    if not resolve_secrets and urlparse(value).scheme in {"env", "secret"}:
        return value
    try:
        result = resolve(value)
        target = result.target if hasattr(result, "target") else result
        if isinstance(target, dict) and "value" in target:
            return target.get("value")
        return target
    except ValueError:
        return value

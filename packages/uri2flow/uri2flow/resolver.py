from __future__ import annotations

import fnmatch
import re
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import yaml
from uri3.config.uri_yaml import unwrap_uri_yaml_document

_CONFIG_NAME = "config/flow_defaults.uri.yaml"


def _find_repo_root(start: Path | None = None) -> Path:
    current = (start or Path(__file__)).resolve()
    if current.is_file():
        current = current.parent
    for path in (current, *current.parents):
        if (path / "contracts").is_dir() and (path / "schemas").is_dir():
            return path
        if (path / _CONFIG_NAME).exists():
            return path
    return Path.cwd()


@dataclass(frozen=True)
class OperationDefaults:
    operation: str
    kind: str
    requires_approval: bool = False


def _pattern_to_regex(pattern: str) -> re.Pattern[str]:
    parts = []
    for chunk in re.split(r"(\{[^}]+\})", pattern):
        if chunk.startswith("{") and chunk.endswith("}"):
            parts.append("[^/]+")
        else:
            parts.append(re.escape(chunk))
    return re.compile("^" + "".join(parts) + "$")


def _match_pattern(pattern: str, uri: str) -> bool:
    if "{" in pattern:
        return _pattern_to_regex(pattern).match(uri) is not None
    return fnmatch.fnmatch(uri, pattern)


@lru_cache(maxsize=1)
def _load_flow_defaults_config() -> dict[str, Any]:
    path = _find_repo_root() / _CONFIG_NAME
    if not path.exists():
        return {"defaults": {}, "patterns": [], "fallback": {}}
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(data, dict):
        return {"defaults": {}, "patterns": [], "fallback": {}}
    return unwrap_uri_yaml_document(data)


def _defaults_from_entry(entry: dict[str, Any]) -> OperationDefaults:
    return OperationDefaults(
        operation=str(entry.get("operation") or "resolve"),
        kind=str(entry.get("kind") or "query"),
        requires_approval=bool(entry.get("requires_approval", False)),
    )


def _defaults_from_scheme(scheme: str) -> OperationDefaults | None:
    entry = (_load_flow_defaults_config().get("defaults") or {}).get(scheme)
    if not isinstance(entry, dict):
        return None
    return _defaults_from_entry(entry)


def _defaults_from_patterns(uri: str) -> OperationDefaults | None:
    for item in _load_flow_defaults_config().get("patterns") or []:
        if not isinstance(item, dict):
            continue
        pattern = str(item.get("match") or "")
        if pattern and _match_pattern(pattern, uri):
            return _defaults_from_entry(item)
    return None


def _fallback_defaults() -> OperationDefaults:
    entry = _load_flow_defaults_config().get("fallback") or {}
    if isinstance(entry, dict) and entry:
        return _defaults_from_entry(entry)
    return OperationDefaults("resolve", "query", False)


def default_operation_for_uri(uri: str) -> OperationDefaults:
    """Resolve default operation/kind from config/flow_defaults.uri.yaml."""
    matched = _defaults_from_patterns(uri)
    if matched is not None:
        return matched

    scheme = urlparse(uri).scheme
    scheme_defaults = _defaults_from_scheme(scheme)
    if scheme_defaults is not None:
        return scheme_defaults

    return _fallback_defaults()


def clear_defaults_cache() -> None:
    _load_flow_defaults_config.cache_clear()

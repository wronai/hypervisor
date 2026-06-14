from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

from .models import CapabilityManifest


@dataclass
class MatchResult:
    manifest: CapabilityManifest
    params: dict[str, str]


def template_to_regex(template: str) -> re.Pattern[str]:
    escaped = re.escape(template)
    pattern = re.sub(r"\\\{([a-zA-Z_][a-zA-Z0-9_]*)\\\}", r"(?P<\1>[^/]+)", escaped)
    return re.compile("^" + pattern + "$")


def match_uri(uri: str, registry: list[CapabilityManifest]) -> MatchResult | None:
    for manifest in registry:
        regex = template_to_regex(manifest.capability.uri_template)
        match = regex.match(uri)
        if match:
            return MatchResult(manifest=manifest, params=match.groupdict())
    return None


def require_match(uri: str, registry: list[CapabilityManifest]) -> MatchResult:
    result = match_uri(uri, registry)
    if result is None:
        raise LookupError(f"No capability matches URI: {uri}")
    return result

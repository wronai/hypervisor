from __future__ import annotations

OPERATION_ALIASES: dict[tuple[str, str], str] = {
    ("browser", "read"): "extract_dom",
    ("browser", "extract"): "extract_dom",
    ("dom", "read"): "extract_dom",
    ("dom", "extract"): "extract_dom",
    ("dom", "extract_dom"): "extract_dom",
    ("browser", "capture"): "screenshot",
    ("browser", "screenshot"): "screenshot",
    ("screen", "capture"): "observe",
    ("screen", "screenshot"): "observe",
    ("input", "call"): "type",
    ("input", "type"): "type",
}

SCHEME_ALIASES: dict[str, str] = {
    "dom": "browser",
}


def registry_scheme(scheme: str) -> str:
    return SCHEME_ALIASES.get(scheme, scheme)


def registry_operation(scheme: str, operation: str) -> str:
    return OPERATION_ALIASES.get((scheme, operation), operation)

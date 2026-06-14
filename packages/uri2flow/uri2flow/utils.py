from __future__ import annotations

import re
from urllib.parse import urlparse


def slugify(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return value.strip("-") or "flow"


def scheme_of(uri: str) -> str:
    return urlparse(uri).scheme


def path_parts(uri: str) -> list[str]:
    parsed = urlparse(uri)
    parts = []
    if parsed.netloc:
        parts.append(parsed.netloc)
    parts.extend([p for p in parsed.path.split("/") if p])
    return parts


def node_id_from_uri(uri: str, used: set[str] | None = None) -> str:
    used = used if used is not None else set()
    parts = path_parts(uri)
    scheme = scheme_of(uri)
    base = "-".join([scheme] + parts[-3:]) if parts else scheme
    base = slugify(base.replace(":", "-"))
    candidate = base or "step"
    idx = 2
    while candidate in used:
        candidate = f"{base}-{idx}"
        idx += 1
    used.add(candidate)
    return candidate

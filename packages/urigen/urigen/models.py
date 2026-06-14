from __future__ import annotations

import re
from pathlib import Path

from uri3.config.repo_root import find_repo_root

from urigen.artifacts import PROFILE_INCLUDES

_SLUG_RE = re.compile(r"[^a-z0-9]+")


def slugify(value: str, *, fallback: str = "ecosystem") -> str:
    slug = _SLUG_RE.sub("-", value.lower()).strip("-")
    return slug or fallback


def normalize_profile(profile: str) -> str:
    normalized = profile.strip().lower() or "minimal"
    if normalized not in PROFILE_INCLUDES:
        allowed = ", ".join(sorted(PROFILE_INCLUDES))
        raise ValueError(f"unknown urigen profile {profile!r}; expected one of: {allowed}")
    return normalized


def repo_root(root: str | Path | None = None) -> Path:
    return Path(root).resolve() if root else find_repo_root()


def wants_voice(prompt: str, profile: str) -> bool:
    text = prompt.lower()
    return profile in {"voice", "full"} or any(
        token in text for token in ("voice", "stt", "tts", "glos", "głos")
    )


def wants_operator(prompt: str, profile: str) -> bool:
    text = prompt.lower()
    return profile in {"operator", "full"} or any(
        token in text for token in ("browser", "chrome", "screen", "operator")
    )

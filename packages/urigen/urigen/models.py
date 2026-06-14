from __future__ import annotations

import re
from pathlib import Path

from uri3.config.repo_root import find_repo_root

from urigen.artifacts import PROFILE_INCLUDES

_SLUG_RE = re.compile(r"[^a-z0-9]+")

PROFILE_ALIASES = {
    "dashboard": "dashboard-agent",
    "dashboard-agent": "dashboard-agent",
    "full-ecosystem": "full",
    "ecosystem": "full",
    "operator-agent": "operator",
    "voice-agent": "voice",
}

PROFILE_DESCRIPTIONS = {
    "minimal": "Weather demo agent + health/check capabilities.",
    "agent": "Agent-oriented package with deployment fragment.",
    "voice": "Minimal weather ecosystem plus STT/TTS/voice command capabilities.",
    "operator": "Agent package with operator/browser workflow intent.",
    "provider": "Provider-style package skeleton.",
    "full": "Broad ecosystem package with voice/operator/replay includes.",
    "dashboard-agent": "Hypervisor Web UI system agent with view/repair capabilities.",
}


def slugify(value: str, *, fallback: str = "ecosystem") -> str:
    slug = _SLUG_RE.sub("-", value.lower()).strip("-")
    return slug or fallback


def normalize_profile(profile: str) -> str:
    normalized = profile.strip().lower() or "minimal"
    normalized = PROFILE_ALIASES.get(normalized, normalized)
    if normalized not in PROFILE_INCLUDES:
        allowed = ", ".join(sorted(set(PROFILE_INCLUDES) | set(PROFILE_ALIASES)))
        raise ValueError(f"unknown urigen profile {profile!r}; expected one of: {allowed}")
    return normalized


def profile_catalog() -> dict[str, dict[str, object]]:
    aliases: dict[str, list[str]] = {name: [] for name in PROFILE_INCLUDES}
    for alias, target in PROFILE_ALIASES.items():
        if alias != target and target in aliases:
            aliases[target].append(alias)
    return {
        name: {
            "name": name,
            "aliases": sorted(aliases[name]),
            "include": PROFILE_INCLUDES[name],
            "description": PROFILE_DESCRIPTIONS.get(name, ""),
        }
        for name in sorted(PROFILE_INCLUDES)
    }


def repo_root(root: str | Path | None = None) -> Path:
    return Path(root).resolve() if root else find_repo_root()


def wants_voice(prompt: str, profile: str) -> bool:
    text = prompt.lower()
    return profile in {"voice", "full"} or any(
        token in text for token in ("voice", "stt", "tts", "glos", "głos")
    )


def wants_dashboard(prompt: str, profile: str) -> bool:
    text = prompt.lower()
    if profile == "dashboard-agent":
        return True
    return any(
        token in text
        for token in (
            "dashboard",
            "web ui",
            "webui",
            "przeglądark",
            "przegladark",
            "procesów hypervisor",
            "procesow hypervisor",
            "process viewer",
            "process-viewer",
            "hypervisor-dashboard",
            "timeline",
            "status agent",
            "pokazywania proces",
        )
    )


def wants_operator(prompt: str, profile: str) -> bool:
    text = prompt.lower()
    return profile in {"operator", "full"} or any(
        token in text for token in ("browser", "chrome", "screen", "operator")
    )

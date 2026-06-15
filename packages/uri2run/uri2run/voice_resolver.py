from __future__ import annotations

import os
from pathlib import Path
from typing import Any

VOICE_PYTHON_BACKENDS: dict[str, str] = {
    "stt://mock/transcribe": "python://uri2voice.stt:transcribe",
    "stt://local/whisper": "python://uri2voice.stt_whisper:transcribe_whisper",
    "tts://mock/speak": "python://uri2voice.tts:speak",
    "voice://command/from-text": "python://uri2voice.voice_command:plan_voice_command",
}

VOICE_SCHEMES = frozenset({"stt", "tts", "voice"})


def is_voice_uri(target: str) -> bool:
    scheme = target.split("://", 1)[0] if "://" in target else ""
    return scheme in VOICE_SCHEMES


def default_voice_registry() -> Path | None:
    env = os.environ.get("TOURI_REGISTRY", "").strip()
    if env:
        path = Path(env)
        return path if path.exists() else None
    try:
        from uri3.paths import find_repo_root

        candidate = find_repo_root() / "examples" / "21_touri_voice"
        return candidate if candidate.exists() else None
    except Exception:  # noqa: BLE001
        return None


def resolve_voice_backend(target: str) -> dict[str, Any] | None:
    """Map stt:// / tts:// / voice:// to python or touri backend."""
    if not is_voice_uri(target):
        return None

    python_target = VOICE_PYTHON_BACKENDS.get(target)
    if python_target:
        return {"type": "python", "target": python_target, "voice_uri": target}

    registry = default_voice_registry()
    if registry is not None:
        return {
            "type": "touri",
            "target": target,
            "registry": str(registry),
            "voice_uri": target,
        }

    return {
        "type": "voice_unresolved",
        "target": target,
        "voice_uri": target,
        "error": (
            f"unknown voice URI: {target}. "
            "Known mock URIs: stt://mock/transcribe, tts://mock/speak, voice://command/from-text. "
            "Or set TOURI_REGISTRY=examples/21_touri_voice and use touri call."
        ),
    }

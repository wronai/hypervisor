from __future__ import annotations

import json
import os
import shutil
import subprocess
import time
from typing import Any

from uri2voice.artifacts import voice_artifact_dir


def _play_text(text: str, *, voice: str = "mock") -> dict[str, Any]:
    if os.environ.get("URI2VOICE_PLAY", "1") in {"0", "false", "FALSE", "no"}:
        return {"played": False, "player": None, "reason": "URI2VOICE_PLAY=0"}

    players: list[tuple[str, list[str]]] = []
    if shutil.which("spd-say"):
        players.append(("spd-say", ["spd-say", text]))
    if shutil.which("espeak"):
        players.append(("espeak", ["espeak", "-v", "pl", text]))
    if shutil.which("espeak-ng"):
        players.append(("espeak-ng", ["espeak-ng", "-v", "pl", text]))
    if shutil.which("say"):
        players.append(("say", ["say", text]))
    if shutil.which("paplay"):
        wav = _write_mock_wav(text)
        if wav is not None:
            players.append(("paplay", ["paplay", str(wav)]))

    for name, cmd in players:
        try:
            subprocess.run(cmd, check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return {"played": True, "player": name}
        except OSError:
            continue
    return {
        "played": False,
        "player": None,
        "reason": "no local speech player found (install spd-say, espeak, or set URI2VOICE_PLAY=0)",
    }


def _write_mock_wav(text: str):
    """Generate a short beep WAV so paplay can be used without TTS engines."""
    try:
        import wave
        from pathlib import Path

        out_dir = voice_artifact_dir({})
        wav_path = out_dir / f"mock_beep_{int(time.time() * 1000)}.wav"
        duration_sec = min(2.0, max(0.4, len(text) / 40.0))
        sample_rate = 22050
        frames = int(sample_rate * duration_sec)
        frequency = 880.0
        import math

        with wave.open(str(wav_path), "w") as handle:
            handle.setnchannels(1)
            handle.setsampwidth(2)
            handle.setframerate(sample_rate)
            for index in range(frames):
                value = int(16000 * math.sin(2 * math.pi * frequency * index / sample_rate))
                handle.writeframesraw(value.to_bytes(2, byteorder="little", signed=True))
        return wav_path
    except Exception:  # noqa: BLE001
        return None


def speak(payload: dict[str, Any] | None = None, context: dict[str, Any] | None = None):
    payload = payload or {}
    text = str(payload.get("text") or "")

    out_dir = voice_artifact_dir(context)
    artifact = out_dir / f"tts_{int(time.time() * 1000)}.json"
    artifact.write_text(
        json.dumps(
            {
                "text": text,
                "voice": payload.get("voice", "mock"),
                "engine": "mock",
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    artifact_uri = f"artifact://voice/{artifact.name}"
    playback = _play_text(text, voice=str(payload.get("voice", "mock"))) if text else {"played": False}
    if payload.get("play") is False:
        playback = {"played": False, "player": None, "reason": "play=false in payload"}

    return {
        "ok": True,
        "result_type": "artifact",
        "data": {
            "text": text,
            "audio_uri": artifact_uri,
            "playback": playback,
        },
        "artifact_uri": artifact_uri,
        "meta": {
            "engine": "mock",
            "artifact_path": str(artifact),
            "playback": playback,
        },
    }

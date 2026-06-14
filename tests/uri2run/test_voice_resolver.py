"""Tests for uri2run voice URI resolver."""

from __future__ import annotations

from uri2run.voice_resolver import resolve_voice_backend


def test_resolve_stt_mock_to_python():
    backend = resolve_voice_backend("stt://mock/transcribe")
    assert backend is not None
    assert backend["type"] == "python"
    assert backend["target"] == "python://uri2voice.stt:transcribe"


def test_resolve_tts_mock_to_python():
    backend = resolve_voice_backend("tts://mock/speak")
    assert backend is not None
    assert backend["type"] == "python"


def test_unknown_voice_uri_returns_touri_or_unresolved():
    backend = resolve_voice_backend("stt://local/whisper")
    assert backend is not None
    assert backend["type"] in {"touri", "voice_unresolved"}

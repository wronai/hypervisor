from __future__ import annotations

import base64
import os
import tempfile
from pathlib import Path
from typing import Any


def _suffix_for_mime(mime_type: str | None) -> str:
    if mime_type and "wav" in mime_type:
        return ".wav"
    if mime_type and "mp4" in mime_type:
        return ".mp4"
    return ".webm"


def _openai_whisper_transcribe(
    audio_bytes: bytes,
    *,
    language: str | None,
    mime_type: str | None,
) -> dict[str, Any]:
    api_key = os.environ.get("OPENAI_API_KEY", "").strip()
    if not api_key:
        return {
            "ok": False,
            "errors": [
                {
                    "code": "WHISPER_NO_API_KEY",
                    "detail": "Set OPENAI_API_KEY for stt://local/whisper (OpenAI API).",
                }
            ],
        }

    import httpx

    suffix = _suffix_for_mime(mime_type)
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as handle:
        handle.write(audio_bytes)
        temp_path = Path(handle.name)

    try:
        model = os.environ.get("OPENAI_WHISPER_MODEL", "whisper-1")
        with httpx.Client(timeout=120.0) as client:
            with temp_path.open("rb") as audio_file:
                data: dict[str, Any] = {"model": model}
                if language:
                    data["language"] = language
                response = client.post(
                    "https://api.openai.com/v1/audio/transcriptions",
                    headers={"Authorization": f"Bearer {api_key}"},
                    data=data,
                    files={"file": (temp_path.name, audio_file, mime_type or "application/octet-stream")},
                )
        if response.status_code >= 400:
            return {
                "ok": False,
                "errors": [
                    {
                        "code": "WHISPER_API_ERROR",
                        "detail": response.text[:500],
                    }
                ],
            }
        payload = response.json()
        text = str(payload.get("text") or "").strip()
        if not text:
            return {
                "ok": False,
                "errors": [{"code": "WHISPER_EMPTY", "detail": "Whisper returned empty transcript."}],
            }
        return {
            "ok": True,
            "data": {"text": text, "language": language or payload.get("language") or "auto"},
            "meta": {"engine": "openai-whisper", "model": model},
        }
    finally:
        temp_path.unlink(missing_ok=True)


def _local_whisper_transcribe(audio_bytes: bytes, *, language: str | None) -> dict[str, Any]:
    try:
        import whisper  # type: ignore
    except ImportError:
        return {
            "ok": False,
            "errors": [
                {
                    "code": "WHISPER_NOT_INSTALLED",
                    "detail": "Install openai-whisper locally or use OPENAI_API_KEY cloud mode.",
                }
            ],
        }

    model_name = os.environ.get("WHISPER_LOCAL_MODEL", "base")
    model = whisper.load_model(model_name)
    with tempfile.NamedTemporaryFile(suffix=".webm", delete=False) as handle:
        handle.write(audio_bytes)
        temp_path = Path(handle.name)
    try:
        options: dict[str, Any] = {}
        if language:
            options["language"] = language
        result = model.transcribe(str(temp_path), **options)
        text = str(result.get("text") or "").strip()
        if not text:
            return {
                "ok": False,
                "errors": [{"code": "WHISPER_EMPTY", "detail": "Local whisper returned empty transcript."}],
            }
        return {
            "ok": True,
            "data": {"text": text, "language": language or result.get("language") or "auto"},
            "meta": {"engine": "local-whisper", "model": model_name},
        }
    finally:
        temp_path.unlink(missing_ok=True)


def _decode_audio_base64(audio_b64: str) -> bytes | None:
    try:
        return base64.b64decode(audio_b64, validate=True)
    except (ValueError, TypeError):
        return None


def _load_audio_from_uri(audio_uri: str) -> bytes | None:
    if not isinstance(audio_uri, str) or not audio_uri.startswith("file://"):
        return None
    path = Path(audio_uri.removeprefix("file://"))
    if not path.is_file():
        return None
    return path.read_bytes()


def _load_audio_bytes(payload: dict[str, Any]) -> tuple[bytes | None, dict[str, Any] | None]:
    audio_b64 = payload.get("audio_base64")
    if isinstance(audio_b64, str) and audio_b64.strip():
        audio_bytes = _decode_audio_base64(audio_b64)
        if audio_bytes is None:
            return None, {
                "ok": False,
                "result_type": "transcript",
                "errors": [{"code": "INVALID_AUDIO", "detail": "audio_base64 is not valid base64."}],
            }
        return audio_bytes, None

    audio_uri = payload.get("audio_uri")
    if isinstance(audio_uri, str):
        audio_bytes = _load_audio_from_uri(audio_uri)
        if audio_bytes is not None:
            return audio_bytes, None

    text = payload.get("text")
    if text:
        language = payload.get("language")
        return None, {
            "ok": True,
            "result_type": "transcript",
            "data": {"text": str(text).strip(), "language": language or "pl"},
            "meta": {"engine": "whisper-fallback-text"},
        }

    return None, {
        "ok": False,
        "result_type": "transcript",
        "errors": [
            {
                "code": "WHISPER_NO_AUDIO",
                "detail": "Provide audio_base64, audio_uri file://..., or text for fallback.",
            }
        ],
    }


def _pick_whisper_engine(mode: str) -> str:
    if mode == "local":
        return "local"
    if mode == "openai":
        return "openai"
    return "openai" if os.environ.get("OPENAI_API_KEY", "").strip() else "local"


def transcribe_whisper(payload: dict[str, Any] | None = None, context: dict[str, Any] | None = None):
    del context
    payload = payload or {}
    language = payload.get("language")
    audio_bytes, early = _load_audio_bytes(payload)
    if early is not None:
        return early

    mime_type = payload.get("mime_type")
    mode = str(payload.get("engine") or os.environ.get("WHISPER_ENGINE", "auto")).lower()
    engine = _pick_whisper_engine(mode)
    if engine == "local":
        result = _local_whisper_transcribe(audio_bytes, language=language)
    else:
        result = _openai_whisper_transcribe(audio_bytes, language=language, mime_type=mime_type)

    if not result.get("ok"):
        return {
            "ok": False,
            "result_type": "transcript",
            "errors": result.get("errors") or [{"code": "WHISPER_FAILED", "detail": "transcription failed"}],
        }

    return {
        "ok": True,
        "result_type": "transcript",
        "data": result["data"],
        "meta": result.get("meta") or {},
    }

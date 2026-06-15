from __future__ import annotations

from typing import Any
from urllib.parse import parse_qs, quote, urlencode, urlparse


def _query_value(query: dict[str, list[str]], *keys: str) -> str | None:
    for key in keys:
        values = query.get(key)
        if values:
            for value in reversed(values):
                if value != "":
                    return value
    return None


def _query_bool(query: dict[str, list[str]], *keys: str) -> bool | None:
    raw = _query_value(query, *keys)
    if raw is None:
        return None
    return raw.strip().lower() in {"1", "true", "yes", "on"}


def parse_chat_prompt_uri(uri: str) -> dict[str, Any]:
    """Parse ``chat://{app}/prompt?text=…&img=…&mime-type=…``."""
    parsed = urlparse(uri.strip())
    if parsed.scheme != "chat":
        raise ValueError(f"not a chat URI: {uri}")

    path_parts = [part for part in parsed.path.strip("/").split("/") if part]
    app = parsed.netloc.strip()
    if not app and path_parts:
        app = path_parts[0]
        path_parts = path_parts[1:]
    if not app:
        raise ValueError(f"chat URI requires app host, e.g. chat://tellmesh/prompt: {uri}")
    if not path_parts or path_parts[-1] != "prompt":
        raise ValueError(f"chat URI path must end with /prompt: {uri}")

    query = parse_qs(parsed.query, keep_blank_values=True)
    text = _query_value(query, "text")
    if text is None or not text.strip():
        raise ValueError("chat://…/prompt requires non-empty ?text=")

    mime_type = _query_value(query, "mime-type", "mime_type", "mime")
    img = _query_value(query, "img", "image")
    llm = _query_bool(query, "llm")
    dry_run = _query_bool(query, "dry_run", "dry-run")

    attachment: dict[str, Any] | None = None
    if img:
        attachment = {"img": img}
        if mime_type:
            attachment["mime_type"] = mime_type

    return {
        "app": app,
        "operation": "prompt",
        "text": text,
        "img": img,
        "mime_type": mime_type,
        "attachment": attachment,
        "llm": llm,
        "dry_run": dry_run,
    }


def build_chat_prompt_uri(
    app: str,
    text: str,
    *,
    img: str | None = None,
    mime_type: str | None = None,
    llm: bool | None = None,
    dry_run: bool | None = None,
) -> str:
    params: dict[str, str] = {"text": text}
    if img:
        params["img"] = img
    if mime_type:
        params["mime-type"] = mime_type
    if llm:
        params["llm"] = "true"
    if dry_run is False:
        params["dry_run"] = "false"
    query = urlencode(params, quote_via=quote)
    return f"chat://{app.strip()}/prompt?{query}"


def is_chat_prompt_uri(value: str) -> bool:
    parsed = urlparse(value.strip())
    return parsed.scheme == "chat"


def resolve_ask_input(
    prompt: str | None,
    uri: str | None,
) -> tuple[str, dict[str, Any] | None, bool, bool]:
    """Return ``(text, prompt_meta, llm, dry_run_default)`` for /api/ask."""
    from urish.nl_uri import is_nl_uri, parse_nl_uri

    if uri:
        if is_nl_uri(uri):
            parsed = parse_nl_uri(uri)
            return (
                parsed["text"],
                {"kind": "nl", **parsed},
                bool(parsed.get("llm") or False),
                parsed.get("dry_run") if parsed.get("dry_run") is not None else True,
            )
        parsed = parse_chat_prompt_uri(uri)
        return (
            parsed["text"],
            {"kind": "chat", **parsed},
            bool(parsed.get("llm") or False),
            parsed.get("dry_run") if parsed.get("dry_run") is not None else True,
        )
    if prompt and is_nl_uri(prompt):
        parsed = parse_nl_uri(prompt)
        return (
            parsed["text"],
            {"kind": "nl", **parsed},
            bool(parsed.get("llm") or False),
            parsed.get("dry_run") if parsed.get("dry_run") is not None else True,
        )
    if prompt and is_chat_prompt_uri(prompt):
        parsed = parse_chat_prompt_uri(prompt)
        return (
            parsed["text"],
            {"kind": "chat", **parsed},
            bool(parsed.get("llm") or False),
            parsed.get("dry_run") if parsed.get("dry_run") is not None else True,
        )
    if not prompt or not prompt.strip():
        raise ValueError("prompt or uri is required")
    return prompt.strip(), None, False, True


def execute_chat_prompt_uri(
    uri: str,
    *,
    dry_run: bool = True,
    use_llm: bool = False,
    payload: dict[str, Any] | None = None,
) -> dict[str, Any]:
    from urish.backends.ask import ask_prompt

    parsed = parse_chat_prompt_uri(uri)
    overrides = payload or {}
    effective_text = str(overrides.get("text") or parsed["text"])
    effective_dry_run = (
        bool(overrides["dry_run"])
        if "dry_run" in overrides
        else parsed.get("dry_run")
        if parsed.get("dry_run") is not None
        else dry_run
    )
    effective_llm = bool(overrides.get("llm") or use_llm or parsed.get("llm") or False)
    envelope = ask_prompt(effective_text, dry_run=effective_dry_run, use_llm=effective_llm)
    data = envelope.setdefault("data", {})
    if isinstance(data, dict):
        data["chat"] = {
            "app": parsed["app"],
            "operation": parsed["operation"],
            "img": parsed.get("img"),
            "mime_type": parsed.get("mime_type"),
            "attachment": parsed.get("attachment"),
        }
        data["chat_uri"] = uri
    return envelope

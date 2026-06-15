from __future__ import annotations

from typing import Any
from urllib.parse import parse_qs, quote, unquote, urlencode, urlparse

from urish.chat_uri import _query_bool, _query_value


def parse_nl_uri(uri: str) -> dict[str, Any]:
    """Parse ``nl://ask?text=…`` or ``nl://ask/{prompt}`` (see chat UI contract)."""
    parsed = urlparse(uri.strip())
    if parsed.scheme != "nl":
        raise ValueError(f"not an nl URI: {uri}")

    query = parse_qs(parsed.query, keep_blank_values=True)
    text = _query_value(query, "text")
    target = parsed.netloc.strip()
    path = unquote(parsed.path.lstrip("/"))

    if text is None:
        if target == "ask" and path:
            text = path
        elif target and path.startswith("ask/"):
            text = path.split("ask/", 1)[1]
        elif target and path == "ask":
            pass
        elif path.startswith("ask/"):
            text = path.split("ask/", 1)[1]

    if text is None or not str(text).strip():
        raise ValueError("nl:// URI requires ?text= or nl://ask/{prompt}")

    app = "ask"
    if target and target != "ask":
        app = target
    elif target == "ask":
        app = "ask"

    return {
        "app": app,
        "target": "ask",
        "operation": "plan",
        "text": str(text),
        "llm": _query_bool(query, "llm"),
        "dry_run": _query_bool(query, "dry_run", "dry-run"),
    }


def build_nl_uri(text: str, *, app: str = "ask") -> str:
    params = {"text": text}
    if app == "ask":
        return f"nl://ask?{urlencode(params, quote_via=quote)}"
    return f"nl://{app}/ask?{urlencode(params, quote_via=quote)}"


def is_nl_uri(value: str) -> bool:
    return urlparse(value.strip()).scheme == "nl"


def execute_nl_uri(
    uri: str,
    *,
    dry_run: bool = True,
    use_llm: bool = False,
    payload: dict[str, Any] | None = None,
) -> dict[str, Any]:
    from urish.backends.ask import ask_prompt

    parsed = parse_nl_uri(uri)
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
        data["nl"] = {
            "app": parsed["app"],
            "target": parsed["target"],
            "operation": parsed["operation"],
        }
        data["nl_uri"] = uri
    return envelope

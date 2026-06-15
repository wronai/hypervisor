"""Tests for chat:// prompt URIs."""

from __future__ import annotations

from urllib.parse import quote

import pytest

from urish.chat_uri import (
    build_chat_prompt_uri,
    execute_chat_prompt_uri,
    is_chat_prompt_uri,
    parse_chat_prompt_uri,
    resolve_ask_input,
)
from urish.backends.call import _is_system_uri, call_uri


def test_parse_chat_prompt_uri_text_and_attachment():
    text = "pokaż proces agenta weather-map-agent.local\nzdiagnozuj agenta invoices-agent.local"
    uri = (
        "chat://tellmesh/prompt?"
        f"text={quote(text)}&img=data:image/png;base64,abc&mime-type=image/png"
    )
    parsed = parse_chat_prompt_uri(uri)
    assert parsed["app"] == "tellmesh"
    assert parsed["operation"] == "prompt"
    assert parsed["text"] == text
    assert parsed["img"] == "data:image/png;base64,abc"
    assert parsed["mime_type"] == "image/png"
    assert parsed["attachment"]["mime_type"] == "image/png"


def test_build_chat_prompt_uri_roundtrip():
    text = "hello world"
    uri = build_chat_prompt_uri("tellmesh", text, img="file:///tmp/x.png", mime_type="image/png")
    parsed = parse_chat_prompt_uri(uri)
    assert parsed["text"] == text
    assert parsed["img"] == "file:///tmp/x.png"
    assert parsed["mime_type"] == "image/png"


def test_resolve_ask_input_from_uri_field():
    text, meta, llm, dry_run = resolve_ask_input(None, "chat://tellmesh/prompt?text=hello")
    assert text == "hello"
    assert meta is not None
    assert meta["app"] == "tellmesh"
    assert llm is False
    assert dry_run is True


def test_resolve_ask_input_from_prompt_chat_uri():
    text, meta, _, _ = resolve_ask_input("chat://hypervisor/prompt?text=status", None)
    assert text == "status"
    assert meta["app"] == "hypervisor"


def test_parse_chat_prompt_uri_requires_text():
    with pytest.raises(ValueError, match="requires non-empty"):
        parse_chat_prompt_uri("chat://tellmesh/prompt")


def test_execute_chat_prompt_uri_batch_plan():
    text = (
        "pokaż proces agenta weather-map-agent.local\n"
        "zdiagnozuj agenta invoices-agent.local"
    )
    uri = build_chat_prompt_uri("tellmesh", text)
    envelope = execute_chat_prompt_uri(uri, dry_run=True)
    data = envelope["data"]
    assert envelope["result_type"] == "ask"
    assert data["batch"] is True
    assert len(data["actions"]) == 2
    assert data["chat_uri"] == uri
    assert data["chat"]["app"] == "tellmesh"


def test_call_uri_routes_chat_prompt_to_system_handler(monkeypatch):
    monkeypatch.setattr(
        "urish.chat_uri.execute_chat_prompt_uri",
        lambda uri, **kwargs: {
            "ok": True,
            "result_type": "ask",
            "data": {"prompt": "x", "planned_uris": [], "next_steps": []},
        },
    )
    assert _is_system_uri("chat://tellmesh/prompt?text=hello")
    result = call_uri("chat://tellmesh/prompt?text=hello", {})
    assert result["result_type"] == "ask"


def test_parse_chat_prompt_uri_prefers_last_mime_type():
    uri = "chat://tellmesh/prompt?text=hi&mime-type=text/plain&mime-type=image/png&img=abc"
    parsed = parse_chat_prompt_uri(uri)
    assert parsed["mime_type"] == "image/png"

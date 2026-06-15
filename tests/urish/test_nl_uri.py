"""Tests for nl:// natural-language routing URIs."""

from __future__ import annotations

from urllib.parse import quote

import pytest

from urish.backends.call import _is_system_uri, call_uri
from urish.chat_uri import resolve_ask_input
from urish.nl_uri import build_nl_uri, execute_nl_uri, is_nl_uri, parse_nl_uri


def test_build_and_parse_nl_uri_query_form():
    text = "pokaż proces agenta weather-map-agent.local\nzdiagnozuj agenta invoices-agent.local"
    uri = build_nl_uri(text)
    assert uri.startswith("nl://ask?text=")
    parsed = parse_nl_uri(uri)
    assert parsed["text"] == text
    assert parsed["app"] == "ask"
    assert parsed["operation"] == "plan"


def test_parse_nl_uri_path_form():
    uri = "nl://ask/" + quote("zdiagnozuj agenta invoices-agent.local", safe="")
    parsed = parse_nl_uri(uri)
    assert parsed["text"] == "zdiagnozuj agenta invoices-agent.local"


def test_resolve_ask_input_prefers_nl_uri():
    text = "pokaż health agenta user-agent.local"
    uri = build_nl_uri(text)
    resolved_text, meta, llm, dry_run = resolve_ask_input(None, uri)
    assert resolved_text == text
    assert meta is not None
    assert meta["kind"] == "nl"
    assert llm is False
    assert dry_run is True


def test_execute_nl_uri_batch_plan():
    text = (
        "pokaż proces agenta weather-map-agent.local\n"
        "zdiagnozuj agenta invoices-agent.local"
    )
    envelope = execute_nl_uri(build_nl_uri(text), dry_run=True)
    data = envelope["data"]
    assert envelope["result_type"] == "ask"
    assert data["batch"] is True
    assert len(data["actions"]) == 2
    assert data["nl_uri"].startswith("nl://ask?")


def test_call_uri_routes_nl_to_system_handler(monkeypatch):
    monkeypatch.setattr(
        "urish.nl_uri.execute_nl_uri",
        lambda uri, **kwargs: {
            "ok": True,
            "result_type": "ask",
            "data": {"prompt": "x", "planned_uris": [], "next_steps": []},
        },
    )
    uri = build_nl_uri("hello")
    assert _is_system_uri(uri)
    assert is_nl_uri(uri)
    result = call_uri(uri, {})
    assert result["result_type"] == "ask"


def test_parse_nl_uri_requires_text():
    with pytest.raises(ValueError, match="requires"):
        parse_nl_uri("nl://ask")

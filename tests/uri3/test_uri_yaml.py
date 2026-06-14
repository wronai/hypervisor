"""Tests for *.uri.yaml loading."""

from __future__ import annotations

from uri3.config.uri_yaml import is_uri, load_uri_yaml, resolve_uri_values


def test_is_uri():
    assert is_uri("env://OPENROUTER_API_KEY")
    assert is_uri("llm://openrouter/qwen/qwen3-coder-next")
    assert not is_uri("plain-text")
    assert not is_uri("http-not-a-uri")


def test_load_llm_uri_yaml():
    data = load_uri_yaml("config/llm.uri.yaml")
    assert data["version"] == 1
    assert "domain_planner" in data["profiles"]
    assert is_uri(data["profiles"]["default"]["model"])
    assert is_uri(data["profiles"]["default"]["api_key"])


def test_resolve_uri_values_keeps_secrets_by_default():
    data = load_uri_yaml("config/llm.uri.yaml")
    resolved = resolve_uri_values(data, resolve_secrets=False)
    assert resolved["profiles"]["default"]["api_key"] == "env://OPENROUTER_API_KEY"

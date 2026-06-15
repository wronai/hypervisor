from __future__ import annotations

import pytest

from hypervisor_dashboard_agent.presentation import (
    resolve_html_presentation,
    resolve_markdown_presentation,
    source_view_uri,
)


def test_source_view_uri_from_html_shorthand():
    assert (
        source_view_uri("html://process/agent/weather-map-agent.local/latest")
        == "view://process/agent/weather-map-agent.local/latest"
    )


def test_source_view_uri_from_html_explicit_view_prefix():
    assert (
        source_view_uri("html://view/process/agent/weather-map-agent.local/latest")
        == "view://process/agent/weather-map-agent.local/latest"
    )


def test_resolve_html_presentation(monkeypatch: pytest.MonkeyPatch):
    fake_view = {
        "result_type": "view",
        "view_uri": "view://process/agent/demo.local/latest",
        "content_type": "text/html",
        "title": "Demo",
        "data": {"agent_id": "demo.local"},
        "html": "<html><body>ok</body></html>",
    }

    class _Envelope:
        view_uri = fake_view["view_uri"]
        title = fake_view["title"]
        data = fake_view["data"]
        html = fake_view["html"]
        content_type = fake_view["content_type"]

        def to_dict(self):
            return dict(fake_view)

    monkeypatch.setattr(
        "hypervisor_dashboard_agent.presentation.resolve_view_uri",
        lambda *_a, **_k: _Envelope(),
    )
    payload = resolve_html_presentation("html://process/agent/demo.local/latest")
    assert payload["ok"] is True
    assert payload["result_type"] == "html"
    assert payload["html"] == "<html><body>ok</body></html>"
    assert payload["source_uri"] == "view://process/agent/demo.local/latest"


def test_resolve_markdown_presentation(monkeypatch: pytest.MonkeyPatch):
    fake_view = {
        "result_type": "view",
        "view_uri": "view://process/agent/demo.local/latest",
        "content_type": "text/html",
        "title": "Demo",
        "data": {"agent_id": "demo.local", "service_status": "healthy"},
        "html": "<html>ok</html>",
    }

    class _Envelope:
        view_uri = fake_view["view_uri"]
        title = fake_view["title"]
        data = fake_view["data"]
        html = fake_view["html"]
        content_type = fake_view["content_type"]

        def to_dict(self):
            return dict(fake_view)

    monkeypatch.setattr(
        "hypervisor_dashboard_agent.presentation.resolve_view_uri",
        lambda *_a, **_k: _Envelope(),
    )
    payload = resolve_markdown_presentation("markdown://process/agent/demo.local/latest")
    assert payload["ok"] is True
    assert payload["result_type"] == "markdown"
    assert "Demo" in payload["presentation_markdown"]
    assert payload["source_uri"] == "view://process/agent/demo.local/latest"

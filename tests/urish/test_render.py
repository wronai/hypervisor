"""Tests for urish text rendering fallbacks."""

from __future__ import annotations

from urish.render import _render_view_fallback, render_result


def test_render_view_fallback_helper():
    text = _render_view_fallback(
        {
            "result_type": "view",
            "view_uri": "view://process/agent/demo.local/latest",
            "title": "Demo Agent",
            "data": {
                "agent_id": "demo.local",
                "service_status": "healthy",
                "process_status": "running",
                "health_status": "ok",
                "effective_port": 8791,
            },
        }
    )
    assert text is not None
    assert "Demo Agent" in text
    assert "healthy" in text
    assert "8791" in text


def test_render_view_summary_in_text_mode():
    result = {
        "ok": True,
        "workflow_status": "completed",
        "service_result_status": "succeeded",
        "result_type": "view",
        "data": {
            "result_type": "view",
            "view_uri": "view://process/agent/demo.local/latest",
            "title": "Demo Agent",
            "data": {
                "agent_id": "demo.local",
                "service_status": "healthy",
                "process_status": "running",
                "health_status": "ok",
                "effective_port": 8791,
            },
        },
    }
    text = render_result(result, output="text")
    assert "Demo Agent" in text
    assert "healthy" in text


def test_render_browser_page_markdown_from_uri_envelope():
    result = {
        "ok": True,
        "data": {
            "ok": True,
            "url": "http://localhost:8788/www/",
            "adapter": "playwright",
            "title": "TellMesh",
            "status_code": 200,
            "text": "Hello page",
        },
    }
    text = render_result(result, output="markdown")
    assert "# TellMesh" in text
    assert "Hello page" in text

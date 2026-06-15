"""Tests for urish call URI routing."""

from __future__ import annotations

from urish.backends.call import _is_dashboard_view_uri, _is_system_uri, call_uri


def test_dashboard_view_uris_are_system():
    assert _is_dashboard_view_uri("view://process/agent/weather-map-agent.local/latest")
    assert _is_system_uri("view://process/agent/weather-map-agent.local/latest")


def test_weather_like_view_uris_are_not_system():
    assert not _is_dashboard_view_uri("view://forecast/Gdansk/7/html")
    assert not _is_system_uri("view://forecast/Gdansk/7/html")


def test_misrouted_view_forecast_does_not_raise(monkeypatch):
    monkeypatch.setattr(
        "urish.backends.explain.explain_target",
        lambda target: {"matched_registry": None, "checks": []},
    )
    result = call_uri("view://forecast/Gdansk/7/html", {})
    assert result["ok"] is False
    assert result["result_type"] == "resolution"
    assert "weather://forecast/Gdansk/7/html" in str(result.get("error", ""))

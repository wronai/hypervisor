"""Tests for uri2flow defaults loaded from config/flow_defaults.uri.yaml."""

from uri2flow.resolver import clear_defaults_cache, default_operation_for_uri


def setup_function() -> None:
    clear_defaults_cache()


def test_pattern_match_hypervisor_run():
    defaults = default_operation_for_uri("hypervisor://local/weather-agent/run")
    assert defaults.operation == "run"
    assert defaults.kind == "command"
    assert defaults.requires_approval is True


def test_pattern_match_hypervisor_restart():
    defaults = default_operation_for_uri("hypervisor://local/weather-agent/restart")
    assert defaults.operation == "restart"
    assert defaults.requires_approval is True


def test_pattern_match_browser_open():
    defaults = default_operation_for_uri("browser://chrome/page/open")
    assert defaults.operation == "open"
    assert defaults.kind == "command"


def test_pattern_match_dom_extract():
    defaults = default_operation_for_uri("dom://chrome/active/body")
    assert defaults.operation == "extract_dom"
    assert defaults.kind == "query"


def test_pattern_match_screen_observe():
    defaults = default_operation_for_uri("screen://chrome/active")
    assert defaults.operation == "observe"
    assert defaults.kind == "query"


def test_pattern_match_input_type():
    defaults = default_operation_for_uri("input://keyboard/main")
    assert defaults.operation == "type"
    assert defaults.kind == "command"
    assert defaults.requires_approval is True


def test_scheme_default_for_http():
    defaults = default_operation_for_uri("http://localhost:8101/health")
    assert defaults.operation == "read"
    assert defaults.kind == "query"


def test_fallback_for_unknown_scheme():
    defaults = default_operation_for_uri("custom://resource/action")
    assert defaults.operation == "resolve"
    assert defaults.kind == "query"

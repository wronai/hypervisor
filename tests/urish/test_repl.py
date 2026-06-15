"""Tests for urish interactive REPL."""

from __future__ import annotations

from unittest.mock import patch

from urish.cli import execute_cli_argv, main
from urish.repl import ReplState, parse_repl_line, run_repl


def test_parse_repl_line_bare_uri_real_mode_by_default():
    state = ReplState()
    argv = parse_repl_line("view://process/agent/weather-map-agent.local/latest", state)
    assert argv == [
        "call",
        "view://process/agent/weather-map-agent.local/latest",
        "--output",
        "text",
    ]


def test_parse_repl_line_bare_uri_dry_run_mode():
    state = ReplState(dry_run=True)
    argv = parse_repl_line("view://process/agent/weather-map-agent.local/latest", state)
    assert argv == [
        "call",
        "view://process/agent/weather-map-agent.local/latest",
        "--dry-run",
        "--output",
        "text",
    ]


def test_parse_repl_line_repair_apply_adds_approve_in_real_mode():
    state = ReplState(dry_run=False)
    argv = parse_repl_line("repair://agent/weather-map-agent.local/apply", state)
    assert argv == [
        "call",
        "repair://agent/weather-map-agent.local/apply",
        "--approve",
        "--output",
        "text",
    ]


def test_parse_repl_line_dry_run_uri_skips_approve_in_real_mode():
    state = ReplState(dry_run=False)
    argv = parse_repl_line("workflow://portal/zus-form/dry-run", state)
    assert "--approve" not in argv
    assert "--dry-run" not in argv


def test_parse_repl_line_natural_language_uses_ask_without_dry_run_by_default():
    state = ReplState()
    argv = parse_repl_line("zdiagnozuj agenta invoices-agent.local", state)
    assert argv == ["ask", "zdiagnozuj agenta invoices-agent.local"]


def test_parse_repl_line_natural_language_ask_dry_run_when_enabled():
    state = ReplState(dry_run=True)
    argv = parse_repl_line("zdiagnozuj agenta invoices-agent.local", state)
    assert argv == ["ask", "zdiagnozuj agenta invoices-agent.local", "--dry-run"]


def test_parse_repl_line_explicit_command_passthrough():
    state = ReplState(dry_run=True)
    argv = parse_repl_line("doctor --json", state)
    assert argv == ["doctor", "--json"]


def test_parse_repl_line_meta_help_returns_none(capsys):
    state = ReplState()
    assert parse_repl_line(".help", state) is None
    out = capsys.readouterr().out
    assert "TellMesh URI shell" in out
    assert "real" in out


def test_parse_repl_line_shell_output_is_not_routed_to_ask(capsys):
    state = ReplState()
    assert parse_repl_line("FAIL blocked/failed policy -msOK completed/succeeded data 13ms", state) is None
    out = capsys.readouterr().out
    assert "output terminala" in out


def test_parse_repl_line_bare_uri_adds_approve_for_browser_mutation():
    state = ReplState(dry_run=False)
    argv = parse_repl_line("browser://chrome/page/open", state)
    assert "--approve" in argv


def test_main_empty_argv_starts_repl():
    with patch("urish.cli.run_repl", return_value=0) as repl:
        code = main([])
    assert code == 0
    repl.assert_called_once()


def test_run_repl_executes_uri_line():
    calls: list[list[str]] = []

    def fake_execute(argv: list[str]) -> int:
        calls.append(argv)
        return 0

    with patch("builtins.input", side_effect=["health://agent/user-agent.local", "exit"]):
        code = run_repl(execute=fake_execute)

    assert code == 0
    assert calls
    assert calls[0][0] == "call"
    assert "health://agent/user-agent.local" in calls[0]
    assert "--dry-run" not in calls[0]


def test_execute_cli_argv_view_uri(monkeypatch):
    with patch("urish.backends.call.call_uri") as mocked:
        mocked.return_value = {
            "ok": True,
            "workflow_status": "completed",
            "execution_status": "completed",
            "service_result_status": "succeeded",
            "result_type": "view",
            "data": {
                "result_type": "view",
                "view_uri": "view://process/agent/user-agent.local/latest",
                "title": "User Agent",
                "data": {
                    "agent_id": "user-agent.local",
                    "service_status": "healthy",
                    "process_status": "running",
                    "health_status": "ok",
                    "effective_port": 8102,
                },
            },
            "meta": {},
        }
        code = execute_cli_argv(
            ["call", "view://process/agent/user-agent.local/latest", "--output", "text"]
        )
    assert code == 0
    mocked.assert_called_once()

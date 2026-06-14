"""Tests for urish unified URI shell."""

from __future__ import annotations

import json
from io import StringIO
from unittest.mock import patch

from urish.cli import main
from urish.payload import load_payload
from urish.policy import PolicyOptions, classify_uri, evaluate_policy
from urish.render import render_result
from urish.select import select_from_envelope
from urish.shortcuts import load_shortcuts, resolve_target


def test_load_payload_from_json():
    assert load_payload('{"text":"test"}') == {"text": "test"}


def test_load_payload_from_file(tmp_path):
    path = tmp_path / "payload.json"
    path.write_text('{"args":["hello"]}', encoding="utf-8")
    assert load_payload(payload_file=str(path)) == {"args": ["hello"]}


def test_load_payload_stdin_envelope():
    raw = json.dumps({"ok": True, "data": {"text": "hello"}})
    with patch("sys.stdin", StringIO(raw)):
        assert load_payload(stdin=True, stdin_mode="envelope") == {"text": "hello"}


def test_render_text_envelope():
    text = render_result(
        {
            "ok": True,
            "workflow_status": "completed",
            "service_result_status": "succeeded",
            "result_type": "shell",
            "data": {"stdout": "hello\n"},
            "meta": {"duration_ms": 1},
        },
        output="text",
    )
    assert "OK" in text
    assert "hello" in text


def test_shortcuts_load():
    shortcuts = load_shortcuts()
    assert "wh" in shortcuts or shortcuts == {} or "hwa" in shortcuts


def test_cli_call_python_mock():
    with patch("urish.backends.call.call_uri") as mocked:
        mocked.return_value = {
            "ok": True,
            "workflow_status": "completed",
            "execution_status": "completed",
            "service_result_status": "succeeded",
            "result_type": "transcript",
            "data": {"text": "test"},
            "meta": {"runtime": "uri2run", "transport": "python"},
        }
        code = main(
            [
                "call",
                "python://uri2voice.stt:transcribe",
                "--payload",
                '{"text":"test"}',
                "--json",
            ]
        )
        assert code == 0
        mocked.assert_called_once()


def test_cli_default_uri_invokes_call():
    with patch("urish.backends.call.call_uri") as mocked:
        mocked.return_value = {
            "ok": True,
            "workflow_status": "completed",
            "execution_status": "completed",
            "service_result_status": "succeeded",
            "result_type": "transcript",
            "data": {},
            "meta": {},
        }
        code = main(["python://uri2voice.stt:transcribe", "--json"])
        assert code == 0
        mocked.assert_called_once()


def test_cli_plan_passes_plain_defaults_to_call_backend():
    with patch("urish.backends.call.call_uri") as mocked:
        mocked.return_value = {
            "ok": True,
            "workflow_status": "completed",
            "execution_status": "completed",
            "service_result_status": "succeeded",
            "result_type": "plan",
            "data": {},
            "meta": {},
        }
        code = main(["plan", "python://uri2voice.stt:transcribe", "--json"])
        assert code == 0
        _, kwargs = mocked.call_args
        assert kwargs["backend_type"] == ""
        assert kwargs["timeout"] == 30.0
        assert kwargs["dry_run"] is True


def test_cli_call_accepts_payload_at_file(tmp_path):
    payload_path = tmp_path / "payload.json"
    payload_path.write_text('{"text":"from-file"}', encoding="utf-8")
    with patch("urish.backends.call.call_uri") as mocked:
        mocked.return_value = {
            "ok": True,
            "workflow_status": "completed",
            "execution_status": "completed",
            "service_result_status": "succeeded",
            "result_type": "transcript",
            "data": {"text": "from-file"},
            "meta": {},
        }
        code = main(
            [
                "call",
                "python://uri2voice.stt:transcribe",
                "--payload",
                f"@{payload_path}",
                "--json",
            ]
        )
        assert code == 0
        args, _ = mocked.call_args
        assert args[1] == {"text": "from-file"}


def test_resolve_target_uri_passthrough():
    assert (
        resolve_target("weather://forecast/Gdansk/14/html") == "weather://forecast/Gdansk/14/html"
    )


def test_policy_blocks_mutation_without_approval():
    opts = PolicyOptions.from_flags(policy="prod")
    allowed, reason, force_dry = evaluate_policy("shell://echo", options=opts)
    assert not allowed
    assert reason
    assert not force_dry


def test_policy_allows_read():
    opts = PolicyOptions.from_flags(readonly=True, policy="safe")
    allowed, reason, _ = evaluate_policy("health://agent/demo", options=opts)
    assert allowed
    assert reason is None


def test_policy_force_dry_run():
    opts = PolicyOptions.from_flags(dry_run=True, policy="dev")
    allowed, _, force_dry = evaluate_policy("shell://echo", options=opts)
    assert allowed
    assert force_dry


def test_classify_repair_uri():
    assert classify_uri("repair://agent/demo/apply") == "repair"


def test_select_from_envelope():
    assert select_from_envelope({"data": {"text": "hello"}}, "data.text") == "hello"


def test_cli_ask_command():
    with patch("urish.backends.ask.ask_prompt") as mocked:
        mocked.return_value = {
            "ok": True,
            "data": {
                "detected_kind": "ecosystem",
                "uris": ["ecosystem://weather-demo"],
                "next_steps": ["uri ecosystem plan test"],
            },
        }
        code = main(["ask", "stworz agenta pogodowego"])
        assert code == 0
        mocked.assert_called_once()


def test_cli_select_command():
    with (
        patch("sys.stdin", StringIO(json.dumps({"data": {"text": "hello"}}))),
        patch("typer.echo") as echo,
    ):
        code = main(["select", "data.text"])
        assert code == 0
        echo.assert_called_once_with("hello")


def test_cli_policy_blocked_exit_code():
    code = main(["call", "repair://agent/demo/apply", "--json"])
    assert code == 4


def test_cli_ticket_list():
    with patch("urish.backends.ticket.list_tickets") as mocked:
        mocked.return_value = {"ok": True, "data": {"tickets": [], "count": 0}}
        code = main(["ticket", "list", "--json"])
        assert code == 0


def test_cli_repair_diagnose():
    with patch("urish.backends.repair.repair_diagnose") as mocked:
        mocked.return_value = {"ok": True, "data": {"issues": []}}
        code = main(["repair", "diagnose", "weather-map-agent.local", "--json"])
        assert code == 0
        mocked.assert_called_once()


def test_cli_watch_limited():
    with patch("urish.backends.watch.watch_uri") as mocked:
        mocked.return_value = {"ok": True, "data": {"count": 1}}
        code = main(["watch", "health://agent/demo", "--count", "1"])
        assert code == 0
        mocked.assert_called_once()


def test_cli_ecosystem_generate_command(tmp_path):
    proposal = tmp_path / "proposal.yaml"
    proposal.write_text("version: 1\nproposal:\n  id: demo\n", encoding="utf-8")
    out = tmp_path / "ecosystem"
    with patch("urigen.generator.generate_ecosystem") as mocked:
        mocked.return_value = {
            "ok": True,
            "ecosystem": "demo",
            "directory": str(out),
            "ecosystem_file": str(out / "ecosystem.yaml"),
            "files": ["ecosystem.yaml"],
        }
        code = main(["ecosystem", "generate", str(proposal), "--out", str(out), "--json"])
        assert code == 0
        mocked.assert_called_once_with(str(proposal), out=str(out))


def test_cli_dashboard_create_plan_only():
    with patch("urish.backends.dashboard.create_dashboard") as mocked:
        mocked.return_value = {
            "ok": True,
            "status": "planned",
            "ecosystem_id": "hypervisor-dashboard",
            "steps": [{"step": "plan", "ok": True}],
        }
        code = main(["dashboard", "create", "hypervisor-dashboard", "--plan-only", "--json"])
        assert code == 0
        mocked.assert_called_once()
        _, kwargs = mocked.call_args
        assert kwargs["plan_only"] is True
        assert kwargs["approve"] is False


def test_cli_agent_create_dashboard_alias():
    with patch("urish.backends.dashboard.create_dashboard") as mocked:
        mocked.return_value = {
            "ok": True,
            "status": "planned",
            "ecosystem_id": "hypervisor-dashboard",
            "steps": [{"step": "plan", "ok": True}],
        }
        code = main(["agent", "create-dashboard", "hypervisor-dashboard", "--dry-run", "--json"])
        assert code == 0
        mocked.assert_called_once()
        _, kwargs = mocked.call_args
        assert kwargs["dry_run"] is True
        assert kwargs["approve"] is False

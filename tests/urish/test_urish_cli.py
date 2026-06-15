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
from urish.shortcuts import load_shortcut_specs, load_shortcuts, resolve_target


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


def test_render_text_view_summary():
    text = render_result(
        {
            "ok": True,
            "workflow_status": "completed",
            "service_result_status": "succeeded",
            "result_type": "view",
            "data": {
                "ok": True,
                "result_type": "view",
                "title": "Weather Map Agent",
                "data": {
                    "agent_id": "weather-map-agent.local",
                    "service_status": "stopped",
                    "process_status": "stale",
                    "health_status": "ok",
                    "incidents": [{"code": "RUNTIME_STATE_STALE", "detail": "dead pid"}],
                    "recommended_action": "restart",
                },
            },
            "meta": {"runtime": "urish"},
        },
        output="text",
    )
    assert "Weather Map Agent" in text
    assert "RUNTIME_STATE_STALE" in text
    assert "Restart agent" in text
    assert "OK completed/succeeded view" not in text


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


def test_shortcut_specs_preserve_payload():
    specs = load_shortcut_specs()
    if not specs:
        return
    assert specs["dashboard-ui"]["uri"] == "browser://chrome/page/open"
    assert specs["dashboard-ui"]["payload"] == {"url": "http://localhost:8788/ui"}


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


def test_cli_call_shortcut_uses_default_payload():
    with patch("urish.backends.call.call_uri") as mocked:
        mocked.return_value = {
            "ok": True,
            "workflow_status": "completed",
            "execution_status": "completed",
            "service_result_status": "succeeded",
            "result_type": "browser",
            "data": {},
            "meta": {},
        }
        code = main(["call", "dashboard-ui", "--approve", "--json"])
        assert code == 0
        args, _ = mocked.call_args
        assert args[0] == "browser://chrome/page/open"
        assert args[1] == {"url": "http://localhost:8788/ui"}


def test_cli_call_shortcut_explicit_payload_wins():
    with patch("urish.backends.call.call_uri") as mocked:
        mocked.return_value = {
            "ok": True,
            "workflow_status": "completed",
            "execution_status": "completed",
            "service_result_status": "succeeded",
            "result_type": "browser",
            "data": {},
            "meta": {},
        }
        code = main(
            [
                "call",
                "dashboard-ui",
                "--payload",
                '{"url":"http://localhost:9999/ui"}',
                "--approve",
                "--json",
            ]
        )
        assert code == 0
        args, _ = mocked.call_args
        assert args[1] == {"url": "http://localhost:9999/ui"}


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


def test_classify_repair_diagnose_uri_as_read():
    assert classify_uri("repair://agent/demo/diagnose") == "read"


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
    code = main(["call", "repair://agent/demo/apply", "--json", "--no-approve"])
    assert code == 4


def test_cli_dev_real_mode_allows_browser_without_explicit_approve():
    with patch("urish.backends.call.call_uri") as mocked:
        mocked.return_value = {"ok": True, "result_type": "data", "data": {"text": "ok"}}
        code = main(
            [
                "call",
                "browser://chrome/page/open",
                "--payload",
                '{"url":"http://localhost:8788/www/"}',
                "--json",
            ]
        )
    assert code == 0
    mocked.assert_called_once()
    policy_opts = mocked.call_args.kwargs["policy_options"]
    assert policy_opts.resolves_approve() is True


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


def test_cli_proof_summarizes_one_uri(capsys):
    with patch("urish.backends.proof.call_uri") as mocked:
        mocked.return_value = {
            "ok": True,
            "workflow_status": "completed",
            "execution_status": "completed",
            "service_result_status": "succeeded",
            "result_type": "view",
            "data": {
                "ok": True,
                "result_type": "view",
                "view_uri": "view://process/agent/demo.local/latest",
                "content_type": "text/html",
                "data": {
                    "service_status": "healthy",
                    "process_status": "running",
                    "health_status": "ok",
                    "actions": [
                        {"kind": "repair", "uri": "repair://agent/demo.local/apply"},
                        {"kind": "mutation", "uri": "ticket://bug/from-incident/demo.local"},
                    ],
                },
            },
            "meta": {"runtime": "urish", "transport": "hypervisor:system_uri"},
        }
        code = main(["proof", "view://process/agent/demo.local/latest", "--json"])
        assert code == 0
        payload = json.loads(capsys.readouterr().out)
        assert payload["result_type"] == "proof"
        checks = {item["name"]: item for item in payload["data"]["checks"]}
        assert checks["chat"]["ok"] is True
        assert checks["web_api"]["ok"] is True
        assert checks["dashboard_view"]["ok"] is True
        assert checks["repair_action"]["status"] == "available"
        assert checks["ticket_action"]["status"] == "available"


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


def test_cli_ecosystem_profiles_command():
    code = main(["ecosystem", "profiles", "--json"])
    assert code == 0


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


def test_cli_agent_run_passes_detach_once():
    with patch("urish.backends.agent.agent_action") as mocked:
        mocked.return_value = {"ok": True, "service_result_status": "succeeded"}
        code = main(
            [
                "agent",
                "run",
                "weather-map-agent.local",
                "--approve",
                "--detach",
                "--wait-healthy",
                "--json",
            ]
        )
        assert code == 0
        mocked.assert_called_once_with(
            "run",
            "weather-map-agent.local",
            detach=True,
            wait_healthy=True,
            supervise_repair="auto",
        )


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


def test_cli_www_create_from_nl_prompt():
    with patch("urish.backends.dashboard.create_dashboard") as mocked:
        mocked.return_value = {
            "ok": True,
            "status": "planned",
            "ecosystem_id": "hypervisor-dashboard",
            "steps": [{"step": "plan", "ok": True}],
        }
        code = main(
            [
                "www",
                "create",
                "stwórz prosty chat markdown połączony z API systemu",
                "--plan-only",
                "--json",
            ]
        )
        assert code == 0
        mocked.assert_called_once()
        args, kwargs = mocked.call_args
        assert args[0] == "hypervisor-dashboard"
        assert kwargs["prompt"] == "stwórz prosty chat markdown połączony z API systemu"
        assert kwargs["plan_only"] is True


def test_cli_agent_describe_does_not_crash_on_typer_signature():
    code = main(["agent", "describe", "weather-map-agent.local"])
    assert code == 0


def test_cli_agent_describe_writes_output(tmp_path):
    out = tmp_path / "weather-map-agent.local.md"
    code = main(["agent", "describe", "weather-map-agent.local", "-o", str(out), "--json"])
    assert code == 0
    assert out.is_file()
    assert "weather-map-agent" in out.read_text(encoding="utf-8")

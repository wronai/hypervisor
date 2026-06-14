from __future__ import annotations

import json
import os
import sys
from typing import Any

import typer

from urish.commands.runtime import RuntimeCommandDeps, register_runtime_commands
from urish.context import CONTEXT_ENV, list_contexts, load_context
from urish.exit_codes import exit_code_for_result
from urish.policy import PolicyOptions
from urish.render import render_result
from urish.shortcuts import load_shortcuts

app = typer.Typer(
    help="urish — unified URI shell (URI + payload + context + policy → envelope)",
    no_args_is_help=True,
    invoke_without_command=True,
)

agent_app = typer.Typer(help="Agent lifecycle shortcuts (maps to hypervisor:// / repair://)")
ecosystem_app = typer.Typer(help="Ecosystem generation (urigen backend)")
dashboard_app = typer.Typer(help="Dashboard system-agent workflow shortcuts")
context_app = typer.Typer(help="Execution context")
ticket_app = typer.Typer(help="Ticket artifacts and planfile integration")
repair_app = typer.Typer(help="Self-healing repair supervisor")
evolve_app = typer.Typer(help="Evolution proposals from tickets and incidents")
proposal_app = typer.Typer(help="Verify and apply evolution proposals")


def _policy_options(
    *,
    dry_run: bool,
    approve: bool,
    no_approve: bool,
    readonly: bool,
    sandbox: bool,
    policy: str,
) -> PolicyOptions:
    ctx = load_context()
    default_policy = (ctx.get("spec") or {}).get("default_policy", "dev")
    selected = policy or default_policy
    return PolicyOptions.from_flags(
        dry_run=dry_run,
        approve=approve,
        no_approve=no_approve,
        readonly=readonly,
        sandbox=sandbox,
        policy=selected,
    )


def _context_policy() -> str | None:
    ctx = load_context()
    return (ctx.get("spec") or {}).get("default_policy")


def _emit(result: dict[str, Any], *, output: str, quiet: bool, json_out: bool) -> None:
    fmt = "json" if json_out else output
    typer.echo(render_result(result, output=fmt, quiet=quiet))


def _finish(result: dict[str, Any], *, policy_blocked: bool = False) -> None:
    blocked = policy_blocked or bool(result.get("policy_blocked"))
    code = exit_code_for_result(result, policy_blocked=blocked)
    if code:
        raise SystemExit(code)


def _print_evolve_summary(result: dict[str, Any], *, json_out: bool) -> None:
    if json_out or not result.get("ok"):
        return
    data = result.get("data")
    if not isinstance(data, dict):
        return
    if data.get("proposal_path"):
        typer.echo(f"Generated proposal: {data['proposal_path']}")
    intent = data.get("detected_intent") or {}
    if intent.get("subtype"):
        typer.echo(f"Detected: {intent.get('kind')} / {intent.get('subtype')}")
    if data.get("next_steps"):
        typer.echo("Next:")
        for step in data["next_steps"]:
            typer.echo(f"  {step}")


register_runtime_commands(
    app,
    RuntimeCommandDeps(
        policy_options=_policy_options,
        context_policy=_context_policy,
        emit=_emit,
        finish=_finish,
    ),
)


@app.callback(invoke_without_command=True)
def root(ctx: typer.Context) -> None:
    """Default help when invoked without URI or subcommand."""
    if ctx.invoked_subcommand is None:
        typer.echo(ctx.get_help())
        raise typer.Exit(0)


@app.command("ask")
def ask_cmd(
    prompt: str = typer.Argument(..., help="Natural language prompt"),
    dry_run: bool = typer.Option(True, "--dry-run/--execute"),
    llm: bool = typer.Option(False, "--llm"),
    json_out: bool = typer.Option(False, "--json"),
    out: str = typer.Option("", "--out", help="Write generated artifact to file"),
) -> None:
    """Natural language → URI proposal/flow (does not execute directly)."""
    from urish.backends.ask import ask_prompt

    result = ask_prompt(prompt, dry_run=dry_run, use_llm=llm)
    if out:
        from pathlib import Path

        import yaml

        Path(out).parent.mkdir(parents=True, exist_ok=True)
        Path(out).write_text(
            yaml.safe_dump(result["data"]["generated"], sort_keys=False, allow_unicode=True),
            encoding="utf-8",
        )
    if json_out:
        typer.echo(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        data = result["data"]
        subtype = data.get("detected_subtype")
        kind = data.get("detected_kind")
        if subtype:
            typer.echo(f"Detected: {subtype} {kind}")
        else:
            typer.echo(f"Detected: {kind}")
        if data.get("ecosystem_id"):
            typer.echo(f"Name: {data['ecosystem_id']}")
        if data.get("profile"):
            typer.echo(f"Profile: {data['profile']}")
        if data.get("agent_id"):
            typer.echo(f"Agent: agent://{data['agent_id']}")
        if data.get("generated", {}).get("proposal_path"):
            typer.echo(f"Generated proposal: {data['generated']['proposal_path']}")
        from urish.ecosystem_workflow import build_planned_uris_display

        planned = build_planned_uris_display(data.get("planned_uris") or data["uris"])
        typer.echo("Planned:")
        for uri in planned:
            typer.echo(f"  {uri}")
        typer.echo("Next:")
        for step in data["next_steps"]:
            typer.echo(f"  {step}")
    _finish(result)


@app.command("nl")
def nl_cmd(
    prompt: str = typer.Argument(...),
    dry_run: bool = typer.Option(True, "--dry-run/--execute"),
    llm: bool = typer.Option(False, "--llm"),
    json_out: bool = typer.Option(False, "--json"),
    stdin: bool = typer.Option(False, "--stdin"),
) -> None:
    """Alias for ask with workflow bias."""
    if stdin:
        text = sys.stdin.read().strip()
        prompt = f"{prompt} {text}".strip() if prompt else text
    ask_cmd(prompt, dry_run=dry_run, llm=llm, json_out=json_out, out="")


@app.command("select")
def select_cmd(
    path: str = typer.Argument(..., help="Dot path, e.g. data.text"),
    json_out: bool = typer.Option(False, "--json"),
) -> None:
    """Extract value from stdin envelope for piping."""
    from urish.select import select_from_envelope

    envelope = json.loads(sys.stdin.read() or "{}")
    value = select_from_envelope(envelope, path)
    if json_out or isinstance(value, (dict, list)):
        typer.echo(json.dumps(value, ensure_ascii=False))
    else:
        typer.echo(str(value))


@app.command("shell")
def shell_cmd() -> None:
    """Interactive REPL for uri commands."""
    from urish.repl import run_repl

    raise typer.Exit(run_repl(execute=main))


@app.command("doctor")
def doctor_cmd(
    strict: bool = typer.Option(False, "--strict", help="Fail on artifact lifecycle/schema drift"),
    json_out: bool = typer.Option(False, "--json"),
) -> None:
    """Check uri2run transports, uri3 doctor, and optional artifact gates."""
    from urish.backends.doctor import doctor_all

    result = doctor_all(strict=strict)
    _emit(result, output="json" if json_out else "yaml", quiet=False, json_out=json_out)
    _finish(result)


@app.command("shortcuts")
def shortcuts_cmd(json_out: bool = typer.Option(False, "--json")) -> None:
    """List configured URI shortcuts."""
    payload = {"ok": True, "shortcuts": load_shortcuts(), "result_type": "shortcuts"}
    _emit(payload, output="json" if json_out else "yaml", quiet=False, json_out=json_out)


@agent_app.command("status")
def agent_status_cmd(selector: str, json_out: bool = typer.Option(False, "--json")) -> None:
    from urish.backends.agent import agent_action

    result = agent_action("status", selector)
    _emit(result, output="json" if json_out else "yaml", quiet=False, json_out=json_out)
    _finish(result)


@agent_app.command("health")
def agent_health_cmd(selector: str, json_out: bool = typer.Option(False, "--json")) -> None:
    from urish.backends.agent import agent_action

    result = agent_action("health", selector)
    _emit(result, output="json" if json_out else "yaml", quiet=False, json_out=json_out)
    _finish(result)


@agent_app.command("create-dashboard")
def agent_create_dashboard_cmd(
    name: str = typer.Argument("hypervisor-dashboard"),
    prompt: str = typer.Option("", "--prompt"),
    plan_only: bool = typer.Option(False, "--plan-only"),
    dry_run: bool = typer.Option(False, "--dry-run"),
    sandbox: bool = typer.Option(False, "--sandbox"),
    approve: bool = typer.Option(False, "--approve"),
    open_ui: bool = typer.Option(False, "--open"),
    json_out: bool = typer.Option(False, "--json"),
) -> None:
    """Alias for dashboard create — ecosystem plan→generate→verify→apply→run."""
    from urish.backends.dashboard import create_dashboard

    result = create_dashboard(
        name,
        prompt=prompt or None,
        plan_only=plan_only,
        dry_run=dry_run,
        sandbox=sandbox,
        approve=approve,
        open_browser=open_ui,
    )
    _emit(result, output="json" if json_out else "yaml", quiet=False, json_out=json_out)
    _finish(result)


@agent_app.command("run")
def agent_run_cmd(
    selector: str,
    detach: bool = typer.Option(True, "--detach/--no-detach"),
    wait_healthy: bool = typer.Option(False, "--wait-healthy"),
    approve: bool = typer.Option(False, "--approve"),
    dry_run: bool = typer.Option(False, "--dry-run"),
    json_out: bool = typer.Option(False, "--json"),
) -> None:
    from urish.backends.agent import agent_action
    from urish.policy import evaluate_policy

    policy_opts = _policy_options(
        dry_run=dry_run,
        approve=approve,
        no_approve=False,
        readonly=False,
        sandbox=False,
        policy="",
    )
    uri = f"hypervisor://local/{selector}/run"
    allowed, reason, force_dry_run = evaluate_policy(
        uri,
        options=policy_opts,
        context_policy=_context_policy(),
    )
    if not allowed:
        _emit(
            {"ok": False, "policy_blocked": True, "error": reason},
            output="json",
            quiet=False,
            json_out=True,
        )
        _finish({"ok": False, "policy_blocked": True}, policy_blocked=True)
    if force_dry_run:
        result = {
            "ok": True,
            "result_type": "plan",
            "data": {"action": "run", "selector": selector},
        }
        _emit(result, output="json" if json_out else "text", quiet=False, json_out=json_out)
        _finish(result)
    result = agent_action(
        "run",
        selector,
        detach=detach,
        wait_healthy=wait_healthy,
        supervise_repair="auto" if wait_healthy else "auto",
    )
    _emit(result, output="json" if json_out else "yaml", quiet=False, json_out=json_out)
    _finish(result)


@agent_app.command("repair")
def agent_repair_cmd(
    selector: str,
    dry_run: bool = typer.Option(False, "--dry-run"),
    approve: bool = typer.Option(False, "--approve"),
    json_out: bool = typer.Option(False, "--json"),
) -> None:
    from urish.backends.agent import agent_action

    if dry_run:
        result = agent_action("diagnose", selector)
    else:
        result = agent_action("repair", selector, safe=not approve, approve=approve)
    _emit(result, output="json" if json_out else "yaml", quiet=False, json_out=json_out)
    _finish(result)


app.add_typer(agent_app, name="agent")


@ecosystem_app.command("plan")
def ecosystem_plan_cmd(
    prompt: str = typer.Argument(...),
    out: str = typer.Option("", "--out"),
    profile: str = typer.Option("minimal", "--profile"),
    ecosystem_id: str = typer.Option("", "--id"),
    json_out: bool = typer.Option(False, "--json"),
) -> None:
    from urigen.io import dump_yaml, write_yaml
    from urigen.proposal import plan_ecosystem

    from urish.intent import detect_intent

    intent = detect_intent(prompt)
    selected_profile = profile
    if profile == "minimal" and intent.get("profile"):
        selected_profile = str(intent["profile"])
    eco_id = ecosystem_id or intent.get("ecosystem_id")
    payload = plan_ecosystem(prompt, profile=selected_profile, ecosystem_id=eco_id)
    if out:
        write_yaml(out, payload)
    typer.echo(json.dumps(payload, indent=2) if json_out else dump_yaml(payload))


@ecosystem_app.command("generate")
def ecosystem_generate_cmd(
    proposal: str = typer.Argument(...),
    out: str = typer.Option(..., "--out"),
    json_out: bool = typer.Option(False, "--json"),
) -> None:
    from urigen.generator import generate_ecosystem
    from urigen.io import dump_yaml

    payload = generate_ecosystem(proposal, out=out)
    typer.echo(json.dumps(payload, indent=2) if json_out else dump_yaml(payload))
    _finish(payload)


@ecosystem_app.command("verify")
def ecosystem_verify_cmd(path: str, json_out: bool = typer.Option(False, "--json")) -> None:
    from urigen.io import dump_yaml
    from urigen.verify import verify_ecosystem

    payload = verify_ecosystem(path)
    typer.echo(json.dumps(payload, indent=2) if json_out else dump_yaml(payload))
    _finish(payload)


@ecosystem_app.command("apply")
def ecosystem_apply_cmd(
    path: str,
    approve: bool = typer.Option(False, "--approve"),
    plan_only: bool = typer.Option(False, "--plan"),
    sandbox: bool = typer.Option(False, "--sandbox"),
    json_out: bool = typer.Option(False, "--json"),
) -> None:
    from urigen.apply import apply_ecosystem
    from urigen.io import dump_yaml

    if not approve and not plan_only:
        result = {
            "ok": False,
            "policy_blocked": True,
            "error": "ecosystem apply requires --approve or --plan",
        }
        typer.echo(json.dumps(result, indent=2) if json_out else dump_yaml(result))
        _finish(result, policy_blocked=True)
    payload = apply_ecosystem(path, approve=approve, plan_only=plan_only)
    if sandbox:
        payload.setdefault("meta", {})["sandbox"] = True
    typer.echo(json.dumps(payload, indent=2) if json_out else dump_yaml(payload))
    _finish(payload)


app.add_typer(ecosystem_app, name="ecosystem")


@dashboard_app.command("create")
def dashboard_create_cmd(
    name: str = typer.Argument("hypervisor-dashboard"),
    prompt: str = typer.Option("", "--prompt"),
    plan_only: bool = typer.Option(False, "--plan-only"),
    dry_run: bool = typer.Option(False, "--dry-run"),
    sandbox: bool = typer.Option(False, "--sandbox"),
    approve: bool = typer.Option(False, "--approve"),
    open_ui: bool = typer.Option(False, "--open"),
    json_out: bool = typer.Option(False, "--json"),
) -> None:
    from urish.backends.dashboard import create_dashboard

    result = create_dashboard(
        name,
        prompt=prompt or None,
        plan_only=plan_only,
        dry_run=dry_run,
        sandbox=sandbox,
        approve=approve,
        open_browser=open_ui,
    )
    _emit(result, output="json" if json_out else "yaml", quiet=False, json_out=json_out)
    _finish(result)


@dashboard_app.command("open")
def dashboard_open_cmd(
    url: str = typer.Option("http://localhost:8788/ui", "--url"),
    approve: bool = typer.Option(False, "--approve"),
    dry_run: bool = typer.Option(False, "--dry-run"),
    json_out: bool = typer.Option(False, "--json"),
) -> None:
    from urish.backends.call import call_uri
    from urish.policy import PolicyOptions

    result = call_uri(
        "browser://chrome/page/open",
        payload={"url": url},
        dry_run=dry_run,
        policy_options=PolicyOptions.from_flags(approve=approve, dry_run=dry_run),
    )
    _emit(result, output="json" if json_out else "yaml", quiet=False, json_out=json_out)
    _finish(result)


app.add_typer(dashboard_app, name="dashboard")


@context_app.command("list")
def context_list_cmd() -> None:
    for item in list_contexts():
        typer.echo(item)


@context_app.command("show")
def context_show_cmd(context_id: str = typer.Argument("")) -> None:
    import yaml

    typer.echo(yaml.safe_dump(load_context(context_id or None), sort_keys=False))


@context_app.command("use")
def context_use_cmd(context_id: str) -> None:
    os.environ[CONTEXT_ENV] = context_id
    typer.echo(f"context: {context_id}")


app.add_typer(context_app, name="context")


@ticket_app.command("list")
def ticket_list_cmd(json_out: bool = typer.Option(False, "--json")) -> None:
    from urish.backends.ticket import list_tickets

    result = list_tickets()
    _emit(result, output="json" if json_out else "yaml", quiet=False, json_out=json_out)


@ticket_app.command("show")
def ticket_show_cmd(target: str, json_out: bool = typer.Option(False, "--json")) -> None:
    from urish.backends.ticket import show_ticket

    try:
        result = show_ticket(target)
    except FileNotFoundError as exc:
        result = {"ok": False, "not_found": True, "error": str(exc)}
    if not json_out and result.get("ok") and isinstance(result.get("data"), dict):
        data = result["data"]
        intent = data.get("detected_intent") or {}
        if intent.get("subtype"):
            typer.echo(f"Detected: {intent.get('kind')} / {intent.get('subtype')}")
        if data.get("next_steps"):
            typer.echo("Next:")
            for step in data["next_steps"]:
                typer.echo(f"  {step}")
    _emit(result, output="json" if json_out else "yaml", quiet=not json_out, json_out=json_out)
    _finish(result)


@ticket_app.command("import")
def ticket_import_cmd(
    strategy: str = typer.Argument(...),
    sprint: str = typer.Option("", "--sprint"),
    json_out: bool = typer.Option(False, "--json"),
) -> None:
    from urish.backends.ticket import import_tickets

    result = import_tickets(strategy, sprint=sprint)
    _emit(result, output="json" if json_out else "yaml", quiet=False, json_out=json_out)
    _finish(result)


@ticket_app.command("plan")
def ticket_plan_cmd(target: str, json_out: bool = typer.Option(False, "--json")) -> None:
    from urish.backends.ticket import plan_ticket

    try:
        result = plan_ticket(target)
    except FileNotFoundError as exc:
        result = {"ok": False, "not_found": True, "error": str(exc)}
    if not json_out and result.get("ok") and isinstance(result.get("data"), dict):
        data = result["data"]
        if data.get("proposal_path"):
            typer.echo(f"Generated proposal: {data['proposal_path']}")
        intent = data.get("detected_intent") or {}
        if intent.get("subtype"):
            typer.echo(f"Detected: {intent.get('kind')} / {intent.get('subtype')}")
        if data.get("next_steps"):
            typer.echo("Next:")
            for step in data["next_steps"]:
                typer.echo(f"  {step}")
    _emit(result, output="json" if json_out else "yaml", quiet=not json_out, json_out=json_out)
    _finish(result)


app.add_typer(ticket_app, name="ticket")


@repair_app.command("diagnose")
def repair_diagnose_cmd(
    selector: str = typer.Argument(...),
    timeout: float = typer.Option(2.0, "--timeout"),
    log_limit: int = typer.Option(20, "--log-limit"),
    json_out: bool = typer.Option(False, "--json"),
) -> None:
    from urish.backends.repair import repair_diagnose

    result = repair_diagnose(selector, timeout=timeout, log_limit=log_limit)
    _emit(result, output="json" if json_out else "yaml", quiet=False, json_out=json_out)
    _finish(result)


@repair_app.command("apply")
def repair_apply_cmd(
    selector: str = typer.Argument(...),
    dry_run: bool = typer.Option(False, "--dry-run"),
    approve: bool = typer.Option(False, "--approve"),
    safe: bool = typer.Option(True, "--safe/--unsafe"),
    playbook: str = typer.Option("", "--playbook"),
    json_out: bool = typer.Option(False, "--json"),
) -> None:
    from urish.backends.repair import repair_apply, repair_diagnose

    if dry_run:
        result = repair_diagnose(selector)
    else:
        result = repair_apply(selector, safe=safe, approve=approve, playbook=playbook or None)
    _emit(result, output="json" if json_out else "yaml", quiet=False, json_out=json_out)
    _finish(result)


@repair_app.command("learn")
def repair_learn_cmd(
    incident_path: str = typer.Argument(...),
    sandbox: bool = typer.Option(True, "--sandbox/--no-sandbox"),
    json_out: bool = typer.Option(False, "--json"),
) -> None:
    from urish.backends.repair import repair_learn

    result = repair_learn(incident_path, sandbox=sandbox)
    _emit(result, output="json" if json_out else "yaml", quiet=False, json_out=json_out)
    _finish(result)


app.add_typer(repair_app, name="repair")


@evolve_app.command("from-ticket")
def evolve_from_ticket_cmd(target: str, json_out: bool = typer.Option(False, "--json")) -> None:
    from urish.backends.evolve import evolve_from_ticket

    try:
        result = evolve_from_ticket(target)
    except FileNotFoundError as exc:
        result = {"ok": False, "not_found": True, "error": str(exc)}
    _print_evolve_summary(result, json_out=json_out)
    _emit(result, output="json" if json_out else "yaml", quiet=not json_out, json_out=json_out)
    _finish(result)


@evolve_app.command("from-incident")
def evolve_from_incident_cmd(
    incident_path: str,
    json_out: bool = typer.Option(False, "--json"),
) -> None:
    from urish.backends.evolve import evolve_from_incident

    result = evolve_from_incident(incident_path)
    _print_evolve_summary(result, json_out=json_out)
    _emit(result, output="json" if json_out else "yaml", quiet=not json_out, json_out=json_out)
    _finish(result)


app.add_typer(evolve_app, name="evolve")


@proposal_app.command("verify")
def proposal_verify_cmd(path: str, json_out: bool = typer.Option(False, "--json")) -> None:
    from urish.backends.evolve import proposal_verify

    result = proposal_verify(path)
    _emit(result, output="json" if json_out else "yaml", quiet=False, json_out=json_out)
    _finish(result)


@proposal_app.command("apply")
def proposal_apply_cmd(
    path: str,
    approve: bool = typer.Option(False, "--approve"),
    sandbox: bool = typer.Option(False, "--sandbox"),
    json_out: bool = typer.Option(False, "--json"),
) -> None:
    from urish.backends.evolve import proposal_apply

    result = proposal_apply(path, approve=approve, sandbox=sandbox)
    _emit(result, output="json" if json_out else "yaml", quiet=False, json_out=json_out)
    _finish(result, policy_blocked=bool(result.get("policy_blocked")))


app.add_typer(proposal_app, name="proposal")


_KNOWN_COMMANDS = frozenset(
    {
        "call",
        "explain",
        "plan",
        "run",
        "logs",
        "watch",
        "stream",
        "ask",
        "nl",
        "select",
        "shell",
        "doctor",
        "shortcuts",
        "agent",
        "dashboard",
        "ecosystem",
        "context",
        "ticket",
        "repair",
        "evolve",
        "proposal",
        "help",
        "--help",
        "-h",
    }
)


def _normalize_argv(argv: list[str]) -> list[str]:
    if not argv:
        return argv
    first = argv[0]
    if first in _KNOWN_COMMANDS or first.startswith("-"):
        return argv
    if "://" in first:
        return ["call", *argv]
    try:
        if first in load_shortcuts():
            return ["call", *argv]
    except Exception:  # noqa: BLE001
        pass
    return argv


def main(argv: list[str] | None = None) -> int:
    try:
        normalized = _normalize_argv(list(argv or sys.argv[1:]))
        app(prog_name="uri", args=normalized, standalone_mode=False)
        return 0
    except SystemExit as exc:
        code = exc.code
        if code is None:
            return 0
        if isinstance(code, str):
            return 1
        return int(code)
    except typer.Exit as exc:
        code = getattr(exc, "exit_code", None) or getattr(exc, "code", 0)
        return int(code or 0)


if __name__ == "__main__":
    raise SystemExit(main())

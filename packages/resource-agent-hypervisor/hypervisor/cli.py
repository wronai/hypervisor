import json
import sys
from collections.abc import Sequence

import typer

from hypervisor import Hypervisor, get_config, load_config
from hypervisor.cli_commands import (
    call_docker,
    deploy_agent,
    echo_json,
    read_agent_logs,
    run_local_agent,
    verify_agent,
)
from hypervisor.deployment_registry.runner import (
    agent_status,
    inspect_agent,
    restart_agent,
    stop_agent,
    supervise_agent,
)
from hypervisor.deployment_registry.status import registry_summary
from hypervisor.uri.client import Uri3Client

app = typer.Typer(help="Hypervisor CLI — deployment registry, agent lifecycle, uri3 adapter")
repair_app = typer.Typer(help="Evolutionary self-healing: diagnose, apply, learn from incidents")
app.add_typer(repair_app, name="repair")


@app.command()
def call(uri: str):
    """Execute a callable URI (docker://, python://, log://)."""
    echo_json(Uri3Client().call(uri))


@app.command()
def scan(uri: str):
    payload = [
        item.__dict__ if hasattr(item, "__dict__") else item for item in Uri3Client().scan(uri)
    ]
    typer.echo(json.dumps(payload, indent=2, ensure_ascii=False))


@app.command()
def resolve(uri: str):
    echo_json(Uri3Client().resolve(uri))


@app.command()
def status():
    """Show hypervisor runtime status."""
    echo_json(Hypervisor().status())


@app.command(name="config")
def config_cmd(path: bool = typer.Option(False, "--path", help="Print config path only")):
    """Show or inspect configuration."""
    if path:
        cfg = load_config()
        typer.echo(cfg.get("_config_path", "<embedded-defaults>"))
    else:
        echo_json(get_config())


@app.command("deployments")
def deployments_list():
    """List entries from deployment registry."""
    typer.echo(json.dumps(registry_summary(), indent=2, ensure_ascii=False))


@app.command("run-agent")
def run_agent_cmd(
    selector: str = typer.Argument(
        ..., help="Deployment id or agent ref, e.g. weather-map-agent.local"
    ),
    port: int | None = typer.Option(None, "--port", help="Override HTTP port"),
    host: str = typer.Option("0.0.0.0", "--host"),
    reload: bool = typer.Option(False, "--reload"),
    detach: bool = typer.Option(
        False, "--detach", help="Start in background and write runtime state"
    ),
    dry_run: bool = typer.Option(False, "--dry-run", help="Print uvicorn command without starting"),
    if_running: str = typer.Option(
        "auto",
        "--if-running",
        help="Existing process policy: auto, reuse, restart, fail",
    ),
    wait_healthy: bool = typer.Option(
        False,
        "--wait-healthy",
        help="After detach start, run bounded supervise/repair until HTTP health OK",
    ),
    supervise_repair: str = typer.Option(
        "auto",
        "--supervise-repair",
        help="Repair loop for --wait-healthy: auto, restart, reuse, sync_health",
    ),
):
    """Start a local agent or print an SSH remote start plan with --dry-run."""
    run_local_agent(
        selector,
        port=port,
        host=host,
        reload=reload,
        detach=detach,
        dry_run=dry_run,
        if_running=None if if_running == "auto" else if_running,
        wait_healthy=wait_healthy,
        supervise_repair=supervise_repair,
    )


@app.command("stop-agent")
def stop_agent_cmd(selector: str = typer.Argument(..., help="Deployment id or agent ref")):
    """Stop a detached local agent using runtime state."""
    echo_json(stop_agent(selector))


@app.command("restart-agent")
def restart_agent_cmd(
    selector: str = typer.Argument(..., help="Deployment id or agent ref"),
    port: int | None = typer.Option(None, "--port"),
    host: str = typer.Option("0.0.0.0", "--host"),
    reload: bool = typer.Option(False, "--reload"),
    detach: bool = typer.Option(
        True, "--detach/--foreground", help="Restart in background by default"
    ),
):
    """Restart a local agent (stop then start)."""
    echo_json(restart_agent(selector, port=port, host=host, reload=reload, detach=detach))


@app.command("agent-status")
def agent_status_cmd(
    selector: str = typer.Argument(..., help="Deployment id or agent ref"),
    no_health: bool = typer.Option(False, "--no-health", help="Skip HTTP health probe"),
):
    """Show deployment status and optional health check."""
    echo_json(agent_status(selector, check_health=not no_health))


@app.command("inspect-agent")
def inspect_agent_cmd(
    selector: str = typer.Argument(..., help="Deployment id or agent ref"),
    timeout: float = typer.Option(2.0, "--timeout", help="HTTP probe timeout"),
    log_limit: int = typer.Option(20, "--log-limit", help="Recent ERROR log entries to include"),
):
    """Inspect process, health, card and recent error logs."""
    echo_json(inspect_agent(selector, timeout=timeout, log_limit=log_limit))


@app.command("supervise")
def supervise_cmd(
    selector: str = typer.Argument(..., help="Deployment id or agent ref"),
    repair: str = typer.Option(
        "none",
        "--repair",
        help="Repair strategy: none, auto, restart, reuse, sync_health",
    ),
    max_attempts: int = typer.Option(3, "--max-attempts", help="Bounded repair attempts"),
    timeout: float = typer.Option(2.0, "--timeout", help="HTTP probe timeout"),
    log_limit: int = typer.Option(20, "--log-limit", help="Recent ERROR log entries to include"),
    learn: bool = typer.Option(
        False,
        "--learn",
        help="On unresolved failure create schema-valid incident + evolution proposal",
    ),
):
    """Run bounded health supervision and optional restart repair."""
    if learn:
        from hypervisor.repair.supervisor import supervise_with_repair

        payload = supervise_with_repair(
            selector,
            repair=repair if repair != "none" else "auto",
            learn=True,
            timeout=timeout,
            log_limit=log_limit,
            max_attempts=max_attempts,
        )
    else:
        payload = supervise_agent(
            selector,
            repair=repair,
            timeout=timeout,
            log_limit=log_limit,
            max_attempts=max_attempts,
        )
    echo_json(payload)
    if not payload.get("ok"):
        raise typer.Exit(1)


@repair_app.command("diagnose")
def repair_diagnose_cmd(
    selector: str = typer.Argument(..., help="Deployment id or agent ref"),
    timeout: float = typer.Option(2.0, "--timeout"),
    log_limit: int = typer.Option(20, "--log-limit"),
):
    """Classify agent failure from runtime, health and logs."""
    from hypervisor.repair.supervisor import diagnose_agent

    echo_json(diagnose_agent(selector, timeout=timeout, log_limit=log_limit))


@repair_app.command("apply")
def repair_apply_cmd(
    selector: str = typer.Argument(..., help="Deployment id or agent ref"),
    safe: bool = typer.Option(True, "--safe/--unsafe", help="Only level-1 playbooks"),
    approve: bool = typer.Option(False, "--approve", help="Allow mutating playbooks"),
    playbook: str | None = typer.Option(None, "--playbook", help="Force a specific playbook"),
):
    """Apply known repair playbooks after diagnosis."""
    from hypervisor.repair.supervisor import repair_apply

    payload = repair_apply(
        selector,
        safe=safe,
        approved=approve,
        playbook=playbook,
    )
    echo_json(payload)
    if not payload.get("ok"):
        raise typer.Exit(1)


@repair_app.command("learn")
def repair_learn_cmd(
    incident_path: str = typer.Argument(..., help="Path to incident.yaml"),
    sandbox: bool = typer.Option(True, "--sandbox/--no-sandbox"),
):
    """Build evolution proposal from incident and optionally sandbox-test repairs."""
    from hypervisor.repair.supervisor import learn_from_incident

    payload = learn_from_incident(incident_path, run_sandbox=sandbox)
    echo_json(payload)
    if not payload.get("ok"):
        raise typer.Exit(1)


@app.command("logs")
def logs_cmd(
    selector: str = typer.Argument(..., help="Deployment id or agent ref"),
    limit: int = typer.Option(50, "--limit"),
):
    """Read agent-related logs via log:// URI."""
    read_agent_logs(selector, limit=limit)


@app.command("deploy-agent")
def deploy_agent_cmd(
    selector: str = typer.Argument(..., help="Deployment id (ssh:// or docker:// target)"),
    apply: bool = typer.Option(False, "--apply", help="Apply deploy (rsync or docker compose up)"),
):
    """Print or apply a deploy plan for SSH or Docker targets."""
    deploy_agent(selector, apply=apply)


@app.command("verify-agent")
def verify_agent_cmd(
    selector: str = typer.Argument(..., help="Deployment id or agent ref"),
    no_health: bool = typer.Option(False, "--no-health", help="Skip HTTP health scan"),
):
    """Verify SSH/Docker deployment and optional HTTP health."""
    verify_agent(selector, check_health=not no_health)


@app.command("docker")
def docker_cmd(
    uri: str = typer.Argument(
        ..., help="docker:// URI with action query, e.g. docker://stack/ssh-testenv?action=up"
    ),
    dry_run: bool = typer.Option(False, "--dry-run", help="Return command plan only"),
):
    """Control Docker stacks/containers through uri3."""
    call_docker(uri, dry_run=dry_run)


@app.command("replay-failure")
def replay_failure_cmd(
    source: str = typer.Argument(..., help="Workflow id or path to JSONL event log"),
    create_test: str = typer.Option(
        "", "--create-test", help="Write pytest regression file to this path"
    ),
    json_out: bool = typer.Option(False, "--json", help="Output JSON summary"),
):
    """Summarize failed workflow logs or generate a regression pytest file."""
    from uri2verify.replay import create_regression_test, replay_workflow_events

    if create_test:
        payload = create_regression_test(source, out=create_test)
    else:
        payload = replay_workflow_events(source)
        if json_out:
            payload = {key: value for key, value in payload.items() if key != "timeline"}
    echo_json(payload)


def main(argv: Sequence[str] | None = None) -> int:
    """Entry point that accepts optional argv (for tests and scripts)."""
    args = list(argv) if argv is not None else None
    try:
        app(args=args)
        return 0
    except SystemExit as e:
        return e.code if isinstance(e.code, int) else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

import json
import sys
from typing import Sequence

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
from hypervisor.deployment_registry.runner import agent_status, restart_agent, stop_agent
from hypervisor.deployment_registry.status import registry_summary
from hypervisor.uri.client import Uri3Client

app = typer.Typer(help="Hypervisor CLI — deployment registry, agent lifecycle, uri3 adapter")


@app.command()
def call(uri: str):
    """Execute a callable URI (docker://, python://, log://)."""
    echo_json(Uri3Client().call(uri))


@app.command()
def scan(uri: str):
    payload = [item.__dict__ if hasattr(item, "__dict__") else item for item in Uri3Client().scan(uri)]
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
    selector: str = typer.Argument(..., help="Deployment id or agent ref, e.g. weather-map-agent.local"),
    port: int | None = typer.Option(None, "--port", help="Override HTTP port"),
    host: str = typer.Option("0.0.0.0", "--host"),
    reload: bool = typer.Option(False, "--reload"),
    detach: bool = typer.Option(False, "--detach", help="Start in background and write runtime state"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Print uvicorn command without starting"),
):
    """Start a local agent or print an SSH remote start plan with --dry-run."""
    run_local_agent(selector, port=port, host=host, reload=reload, detach=detach, dry_run=dry_run)


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
    detach: bool = typer.Option(True, "--detach/--foreground", help="Restart in background by default"),
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
    uri: str = typer.Argument(..., help="docker:// URI with action query, e.g. docker://stack/ssh-testenv?action=up"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Return command plan only"),
):
    """Control Docker stacks/containers through uri3."""
    call_docker(uri, dry_run=dry_run)


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

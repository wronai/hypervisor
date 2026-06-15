from __future__ import annotations

import json

import typer

from urish.commands.deps import RuntimeCommandDeps


def register_ecosystem_commands(app: typer.Typer, deps: RuntimeCommandDeps) -> None:
    ecosystem_app = typer.Typer(help="Ecosystem generation (urigen backend)")

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
        deps.finish(payload)

    @ecosystem_app.command("verify")
    def ecosystem_verify_cmd(
        path: str,
        json_out: bool = typer.Option(False, "--json"),
    ) -> None:
        from urigen.io import dump_yaml
        from urigen.verify import verify_ecosystem

        payload = verify_ecosystem(path)
        typer.echo(json.dumps(payload, indent=2) if json_out else dump_yaml(payload))
        deps.finish(payload)

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
            deps.finish(result, policy_blocked=True)
        payload = apply_ecosystem(path, approve=approve, plan_only=plan_only)
        if sandbox:
            payload.setdefault("meta", {})["sandbox"] = True
        typer.echo(json.dumps(payload, indent=2) if json_out else dump_yaml(payload))
        deps.finish(payload)

    @ecosystem_app.command("profiles")
    def ecosystem_profiles_cmd(json_out: bool = typer.Option(False, "--json")) -> None:
        from urigen.io import dump_yaml
        from urigen.models import profile_catalog

        payload = {
            "ok": True,
            "profiles": list(profile_catalog().values()),
            "result_type": "ecosystem_profiles",
        }
        typer.echo(json.dumps(payload, indent=2) if json_out else dump_yaml(payload))

    app.add_typer(ecosystem_app, name="ecosystem")

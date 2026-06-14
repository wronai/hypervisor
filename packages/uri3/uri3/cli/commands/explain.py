from __future__ import annotations

import json

import typer

from uri3.resolvers.explain import explain_uri


def register(app: typer.Typer) -> None:
    @app.command()
    def explain(
        uri: str,
        registry: str = typer.Option("", "--registry", help="touri capability registry directory"),
        json_out: bool = typer.Option(False, "--json", help="Output JSON"),
    ) -> None:
        """Show which registry resolves a URI and how it would be executed."""
        payload = explain_uri(uri, registry_root=registry or None)
        typer.echo(json.dumps(payload, indent=2, ensure_ascii=False) if json_out else _render(payload))


def _render(payload: dict) -> str:
    lines = [
        f"uri: {payload.get('uri')}",
        f"matched_registry: {payload.get('matched_registry') or payload.get('resolution', 'unknown')}",
    ]
    if payload.get("capability"):
        lines.append(f"capability: {payload['capability']}")
    if payload.get("backend"):
        backend = payload["backend"]
        lines.append(f"backend: {backend.get('type')} -> {backend.get('target') or backend.get('command') or backend.get('url') or '-'}")
    if payload.get("policy"):
        lines.append(f"policy: {json.dumps(payload['policy'], ensure_ascii=False)}")
    if payload.get("data_quality"):
        lines.append(f"data_quality: {json.dumps(payload['data_quality'], ensure_ascii=False)}")
    if payload.get("fallbacks"):
        lines.append(f"fallbacks: {json.dumps(payload['fallbacks'], ensure_ascii=False)}")
    if payload.get("verification"):
        verification = payload["verification"]
        lines.append(f"verification: data_quality={verification.get('data_quality_enabled')} fallbacks={verification.get('fallback_count', 0)}")
        if verification.get("data_quality"):
            lines.append(f"  failure_code: {verification['data_quality'].get('failure_code')}")
        if verification.get("fallbacks"):
            for item in verification["fallbacks"]:
                lines.append(f"  - when={item.get('when')} backend={item.get('backend_type')}")
    if payload.get("runtime_transport"):
        lines.append(f"runtime_transport: {payload['runtime_transport']}")
    if payload.get("operations"):
        lines.append(f"uri2ops operations: {', '.join(payload['operations'])}")
    if payload.get("checks"):
        lines.append("checks:")
        for check in payload["checks"]:
            lines.append(f"  - {check['registry']}: matched={check.get('matched')}")
    return "\n".join(lines)

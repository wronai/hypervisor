from __future__ import annotations

from pathlib import Path
from typing import Any

from uri3.graph import (
    build_execution_plan,
    load_workflow_graph,
    run_workflow,
    validate_workflow_graph,
)
from uri3.results import ServiceResult, service_result

from uri2run.result import error_result
from uri2run.transports.paths import execution_options, execution_root


def run_workflow_from_graph_dict(
    graph: dict[str, Any],
    *,
    source_key: str,
    source_path: Path,
    payload: dict[str, Any],
    context: dict[str, Any],
    backend_extra: dict[str, Any] | None = None,
    transport: str,
    invalid_code: str,
) -> ServiceResult:
    """Shared dry-run and execute path for uri_flow and uri_graph transports."""
    extra = backend_extra or {}
    options = execution_options(payload, extra)

    errors = validate_workflow_graph(graph)
    if errors:
        return error_result(invalid_code, "; ".join(errors[:5]))

    workflow = load_workflow_graph(graph)
    root = execution_root(context)

    if options["dry_run"]:
        simulation = run_workflow(
            workflow,
            approve=False,
            dry_run=True,
            browser_mode=options["browser"],
            root=root,
        ).to_dict()
        data = {
            source_key: str(source_path),
            "plan": build_execution_plan(workflow),
            "simulation": simulation,
        }
        ok = bool((simulation.get("workflow_result") or {}).get("ok", True))
        return service_result(ok=ok, result_type="plan", data=data, meta={"transport": transport})

    result = run_workflow(
        workflow,
        approve=options["approve"],
        dry_run=False,
        browser_mode=options["browser"],
        root=root,
    )
    body = result.to_dict()
    ok = bool((body.get("workflow_result") or {}).get("ok", False))
    return service_result(ok=ok, result_type="workflow", data=body, meta={"transport": transport})

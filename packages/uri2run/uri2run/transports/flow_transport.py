from __future__ import annotations

from typing import Any

from uri2flow import expand_flow
from uri2run.result import error_result
from uri2run.transports.paths import execution_options, resolve_path
from uri3.graph import build_execution_plan, dry_run_workflow, load_workflow_graph, run_workflow
from uri3.graph import validate_workflow_graph
from uri3.results import ServiceResult, service_result


def run_uri_flow(
    flow_path: str,
    payload: dict[str, Any],
    context: dict[str, Any],
    *,
    backend_extra: dict[str, Any] | None = None,
) -> ServiceResult:
    extra = backend_extra or {}
    path = resolve_path(flow_path, context)
    if not path.is_file():
        return error_result("FLOW_NOT_FOUND", f"Flow file not found: {path}")

    options = execution_options(payload, extra)
    try:
        graph = expand_flow(path)
    except Exception as exc:
        return error_result("FLOW_EXPAND_FAILED", str(exc))

    errors = validate_workflow_graph(graph)
    if errors:
        return error_result("FLOW_INVALID", "; ".join(errors[:5]))

    workflow = load_workflow_graph(graph)
    root = path.parent if path.parent.is_dir() else resolve_path(".", context).parent

    if options["dry_run"]:
        simulation = dry_run_workflow(workflow)
        data = {
            "flow": str(path),
            "plan": build_execution_plan(workflow),
            "simulation": simulation,
        }
        ok = bool((simulation.get("workflow_result") or {}).get("ok", True))
        return service_result(ok=ok, result_type="plan", data=data, meta={"transport": "uri_flow"})

    result = run_workflow(
        workflow,
        approve=options["approve"],
        dry_run=False,
        browser_mode=options["browser"],
        root=root,
    )
    body = result.to_dict()
    ok = bool((body.get("workflow_result") or {}).get("ok", False))
    return service_result(ok=ok, result_type="workflow", data=body, meta={"transport": "uri_flow"})

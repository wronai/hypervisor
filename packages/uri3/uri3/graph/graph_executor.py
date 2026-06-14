from __future__ import annotations

from typing import Any

from uri3.graph.adapters.uri2ops_adapter import cleanup_operator_adapters
from uri3.graph.adapters.registry import adapter_for_uri
from uri3.graph.conditions import evaluate_condition
from uri3.graph.dependency_graph import topological_sort
from uri3.graph.event_log import append_workflow_event
from uri3.graph.execution_models import (
    ExecutionContext,
    GraphExecutionPlan,
    GraphExecutionResult,
    StepExecutionResult,
    new_execution_context,
    utc_now_iso,
)
from uri3.graph.graph_serializer import workflow_manifest
from uri3.graph.graph_validator import load_workflow_graph, validate_workflow_graph
from uri3.graph.models import GraphNode, WorkflowGraph
from uri3.graph.operation_registry import effective_kind, validate_node_operation
from uri3.graph.policy import can_execute_step


def build_execution_plan(graph: WorkflowGraph | dict[str, Any]) -> dict[str, Any]:
    workflow = graph if isinstance(graph, WorkflowGraph) else load_workflow_graph(graph)
    order = topological_sort(workflow)
    steps = []
    for node_id in order:
        node = workflow.nodes[node_id]
        steps.append(
            {
                "id": node.id,
                "uri": node.uri,
                "operation": node.operation,
                "kind": effective_kind(node),
                "depends_on": list(node.depends_on),
                "condition": node.condition,
                "requires_approval": effective_kind(node) == "command",
            }
        )
    plan = GraphExecutionPlan(graph_id=workflow.id, kind=workflow.kind, order=order, steps=steps)
    return {
        **plan.to_dict(),
        "manifest": workflow_manifest(workflow),
    }


def dry_run_workflow(source: WorkflowGraph | dict[str, Any]) -> dict[str, Any]:
    return run_workflow(source, dry_run=True).to_dict()


def _dependencies_ok(node: GraphNode, completed: dict[str, StepExecutionResult]) -> tuple[bool, str | None]:
    for dependency in node.depends_on:
        prior = completed.get(dependency)
        if prior is None:
            return False, f"missing dependency {dependency!r}"
        if prior.status == "skipped":
            return False, f"dependency {dependency!r} was skipped"
        if not prior.ok and prior.status != "blocked":
            return False, f"dependency {dependency!r} failed"
    return True, None


def _execute_step(node: GraphNode, context: ExecutionContext) -> dict[str, Any]:
    adapter = adapter_for_uri(node.uri)
    if adapter is None:
        return {
            "ok": True,
            "mock": True,
            "message": f"no adapter registered for {node.uri}; treated as no-op mock",
        }
    return adapter.execute(node, context)


def run_workflow(
    source: WorkflowGraph | dict[str, Any],
    *,
    approve: bool = False,
    dry_run: bool = False,
    root=None,
    browser_mode: str = "auto",
) -> GraphExecutionResult:
    errors = validate_workflow_graph(source)
    if errors:
        raise ValueError("Workflow graph validation failed: " + "; ".join(errors[:5]))

    workflow = source if isinstance(source, WorkflowGraph) else load_workflow_graph(source)
    for node in workflow.nodes.values():
        op_error = validate_node_operation(node)
        if op_error:
            raise ValueError(op_error)

    context = new_execution_context(
        workflow.id,
        root=root,
        approve_commands=approve,
        dry_run=dry_run,
        browser_mode=browser_mode,
    )
    started_at = utc_now_iso()
    append_workflow_event(
        workflow.id,
        {"type": "WorkflowStarted", "workflow_id": workflow.id, "run_id": context.run_id, "mode": "dry_run" if dry_run else "execute"},
        root=context.root,
    )

    order = topological_sort(workflow)
    completed: dict[str, StepExecutionResult] = {}
    step_results: list[StepExecutionResult] = []
    pending_approval: list[str] = []
    workflow_ok = True
    mode = "dry_run" if dry_run else "execute"

    try:
        for node_id in order:
            node = workflow.nodes[node_id]
            kind = effective_kind(node)

            if not evaluate_condition(node.condition, context):
                skipped = StepExecutionResult(
                    id=node.id,
                    uri=node.uri,
                    operation=node.operation,
                    kind=kind,
                    status="skipped",
                    ok=True,
                    result={"reason": "condition_not_met"},
                )
                step_results.append(skipped)
                completed[node.id] = skipped
                context.step_outputs[node.id] = skipped.result
                continue

            deps_ok, dep_error = _dependencies_ok(node, completed)
            if not deps_ok:
                failed = StepExecutionResult(
                    id=node.id,
                    uri=node.uri,
                    operation=node.operation,
                    kind=kind,
                    status="failed",
                    ok=False,
                    error=dep_error,
                )
                step_results.append(failed)
                completed[node.id] = failed
                workflow_ok = False
                append_workflow_event(
                    workflow.id,
                    {"type": "StepFailed", "workflow_id": workflow.id, "step_id": node.id, "error": dep_error},
                    root=context.root,
                )
                break

            allowed, policy_error = can_execute_step(node, approve_commands=approve, dry_run=dry_run)
            if not allowed:
                blocked = StepExecutionResult(
                    id=node.id,
                    uri=node.uri,
                    operation=node.operation,
                    kind=kind,
                    status="blocked",
                    ok=False,
                    error=policy_error,
                )
                step_results.append(blocked)
                completed[node.id] = blocked
                pending_approval.append(node.id)
                workflow_ok = False
                append_workflow_event(
                    workflow.id,
                    {"type": "StepBlocked", "workflow_id": workflow.id, "step_id": node.id, "reason": policy_error},
                    root=context.root,
                )
                break

            append_workflow_event(
                workflow.id,
                {"type": "StepStarted", "workflow_id": workflow.id, "step_id": node.id, "uri": node.uri, "operation": node.operation},
                root=context.root,
            )

            if dry_run:
                result_payload = {
                    "ok": True,
                    "dry_run": True,
                    "uri": node.uri,
                    "operation": node.operation,
                }
            else:
                result_payload = _execute_step(node, context)

            ok = bool(result_payload.get("ok", True))
            step_artifact_uri = result_payload.get("artifact_uri")
            step = StepExecutionResult(
                id=node.id,
                uri=node.uri,
                operation=node.operation,
                kind=kind,
                status="completed" if ok else "failed",
                ok=ok,
                result=result_payload,
                artifact_uri=step_artifact_uri,
                error=None if ok else str(result_payload.get("error") or "step failed"),
            )
            step_results.append(step)
            completed[node.id] = step
            context.step_outputs[node.id] = {**result_payload, "ok": ok}

            append_workflow_event(
                workflow.id,
                {
                    "type": "StepCompleted" if ok else "StepFailed",
                    "workflow_id": workflow.id,
                    "step_id": node.id,
                    "ok": ok,
                    **({"artifact_uri": step_artifact_uri} if step_artifact_uri else {}),
                },
                root=context.root,
            )
            if not ok:
                workflow_ok = False
                break
    finally:
        cleanup_operator_adapters(context)

    completed_at = utc_now_iso()
    append_workflow_event(
        workflow.id,
        {"type": "WorkflowCompleted", "workflow_id": workflow.id, "ok": workflow_ok, "mode": mode},
        root=context.root,
    )

    message = None
    if pending_approval:
        message = "Workflow stopped: command node(s) require --approve"
    elif dry_run:
        message = "Dry-run completed without side effects"

    return GraphExecutionResult(
        id=workflow.id,
        ok=workflow_ok and not pending_approval,
        started_at=started_at,
        completed_at=completed_at,
        mode=mode,
        steps=step_results,
        pending_approval=pending_approval,
        message=message,
    )

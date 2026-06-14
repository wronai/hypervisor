from __future__ import annotations

from pathlib import Path
from typing import Any


def run_target(
    target: str,
    *,
    approve: bool = False,
    dry_run: bool = False,
    adapter: str = "mock",
    payload: dict[str, Any] | None = None,
) -> dict[str, Any]:
    _ = payload
    path = Path(target)
    if path.suffix == ".yaml" and path.exists():
        if "task" in path.read_text(encoding="utf-8")[:500]:
            from uri2ops.operator.runner import run_task
            from uri2ops.operator.task import load_task

            task = load_task(path)
            result = run_task(task, dry_run=dry_run, approve=approve, adapter=adapter)
            return result.to_dict()
        if ".uri.flow." in path.name or "flow:" in path.read_text(encoding="utf-8")[:200]:
            from uri2flow.expander import expand_flow
            from uri3.graph import run_workflow

            graph = expand_flow(path)
            payload = run_workflow(graph, dry_run=dry_run, browser_mode=adapter).to_dict()
            return payload
    if target.startswith("workflow://") or target.startswith("flow://"):
        from touri.executor import call_uri

        return call_uri(target).to_dict()
    return {
        "ok": False,
        "validation_failed": True,
        "error": f"unsupported run target: {target}",
        "result_type": "run",
    }

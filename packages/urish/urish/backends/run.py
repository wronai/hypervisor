from __future__ import annotations

from pathlib import Path
from typing import Any

from uri3.paths import find_repo_root


def _repo_root() -> Path:
    return find_repo_root(strict=False)


def _touri_registry_root() -> str:
    from uri3.resolvers.explain import default_touri_registry

    return str(default_touri_registry(_repo_root()))


def _run_workflow_uri(
    target: str,
    *,
    approve: bool = False,
    dry_run: bool = False,
    adapter: str = "mock",
    payload: dict[str, Any] | None = None,
    artifact_root: Path | None = None,
) -> dict[str, Any]:
    from touri.executor import call_uri

    repo = _repo_root()
    body = dict(payload or {})
    body.setdefault("dry_run", dry_run)
    body.setdefault("approve", approve)
    body.setdefault("browser", adapter)
    context = {
        "root": str(repo),
        "artifact_root": str(artifact_root or repo),
        "dry_run": dry_run,
        "approve": approve,
        "browser": adapter,
    }
    try:
        result = call_uri(target, _touri_registry_root(), payload=body, context=context)
        return result.to_dict()
    except LookupError as exc:
        from urish.backends.explain import explain_target

        return {
            "ok": False,
            "validation_failed": True,
            "error": str(exc),
            "explain": explain_target(target, registry=_touri_registry_root()),
            "result_type": "run",
        }


def run_target(
    target: str,
    *,
    approve: bool = False,
    dry_run: bool = False,
    adapter: str = "mock",
    payload: dict[str, Any] | None = None,
    artifact_root: Path | None = None,
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
    if target.startswith("workflow://") or target.startswith("flow://") or target.startswith("cron://"):
        return _run_workflow_uri(
            target,
            approve=approve,
            dry_run=dry_run,
            adapter=adapter,
            payload=payload,
            artifact_root=artifact_root,
        )
    return {
        "ok": False,
        "validation_failed": True,
        "error": f"unsupported run target: {target}",
        "result_type": "run",
    }

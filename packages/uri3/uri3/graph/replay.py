from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from uri3.graph.event_log import workflow_event_path


def _resolve_event_path(source: str | Path, root: Path) -> Path:
    path = Path(source)
    if path.exists():
        return path
    candidate = workflow_event_path(str(source), root)
    if candidate.exists():
        return candidate
    raise FileNotFoundError(f"workflow event log not found for {source!r}")


def load_workflow_events(source: str | Path, *, root: Path | None = None) -> list[dict[str, Any]]:
    from uri3.config.repo_root import find_repo_root

    repo_root = root or find_repo_root()
    path = _resolve_event_path(source, repo_root)
    events: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            events.append(json.loads(line))
    return events


def replay_workflow_events(source: str | Path, *, root: Path | None = None) -> dict[str, Any]:
    from uri3.config.repo_root import find_repo_root

    repo_root = root or find_repo_root()
    path = _resolve_event_path(source, repo_root)
    events = load_workflow_events(path, root=repo_root)
    workflow_id = next((event.get("workflow_id") for event in events if event.get("workflow_id")), path.stem)
    failed_steps = [event for event in events if event.get("type") == "StepFailed"]
    blocked_steps = [event for event in events if event.get("type") == "StepBlocked"]
    completed = next((event for event in reversed(events) if event.get("type") == "WorkflowCompleted"), None)
    return {
        "workflow_id": workflow_id,
        "event_log": str(path),
        "event_count": len(events),
        "failed_steps": failed_steps,
        "blocked_steps": blocked_steps,
        "workflow_completed": completed,
        "timeline": events,
    }

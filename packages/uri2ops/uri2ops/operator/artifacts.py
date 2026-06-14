from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

from uri2ops.operator.artifact_resolver import resolve_artifact_path


def artifact_root(root: str | Path | None = None) -> Path:
    base = Path(root) if root else Path.cwd()
    path = base / "output" / "artifacts" / "operator"
    path.mkdir(parents=True, exist_ok=True)
    return path


def write_artifact(name: str, payload: dict[str, Any], root: str | Path | None = None) -> str:
    safe = name.replace(":", "_").replace("/", "_")
    file_name = f"{int(time.time() * 1000)}_{safe}.json"
    path = artifact_root(root) / file_name
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    return f"artifact://operator/{file_name}"


def write_step_artifact(
    task_id: str,
    run_id: str,
    step_id: str,
    suffix: str,
    content: bytes | str,
    *,
    root: str | Path | None = None,
) -> tuple[Path, str]:
    base = Path(root) if root else Path.cwd()
    path = base / "output" / "artifacts" / "operator" / "workflows" / task_id / run_id / step_id / suffix
    path.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(content, str):
        path.write_text(content, encoding="utf-8")
    else:
        path.write_bytes(content)
    uri = f"artifact://operator/workflows/{task_id}/{run_id}/{step_id}/{suffix}"
    return path, uri


def resolve_artifact(uri: str, *, root: str | Path | None = None) -> Path:
    return resolve_artifact_path(uri, root=Path(root) if root else None)

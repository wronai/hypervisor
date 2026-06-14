from __future__ import annotations

import json
import os
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from hypervisor.paths import find_repo_root


def runtime_root(root: Path | None = None) -> Path:
    repo = Path(root) if root is not None else find_repo_root()
    return repo / "output" / "runtime" / "agents"


def state_path(deployment_id: str, root: Path | None = None) -> Path:
    return runtime_root(root) / deployment_id / "state.json"


def load_runtime_state(deployment_id: str, root: Path | None = None) -> dict[str, Any] | None:
    path = state_path(deployment_id, root)
    if not path.exists():
        return None
    data = json.loads(path.read_text(encoding="utf-8"))
    return data if isinstance(data, dict) else None


def save_runtime_state(deployment_id: str, state: dict[str, Any], root: Path | None = None) -> Path:
    path = state_path(deployment_id, root)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path


def clear_runtime_state(deployment_id: str, root: Path | None = None) -> None:
    path = state_path(deployment_id, root)
    if path.exists():
        path.unlink()


def is_process_alive(pid: int | None) -> bool:
    if not pid or pid <= 0:
        return False
    try:
        os.kill(pid, 0)
    except OSError:
        return False
    return True


def runtime_status(deployment_id: str, root: Path | None = None) -> str:
    state = load_runtime_state(deployment_id, root)
    if not state:
        return "stopped"
    pid = state.get("pid")
    if state.get("status") == "running" and is_process_alive(pid):
        return "running"
    if state.get("status") == "running":
        return "stale"
    return str(state.get("status") or "stopped")


def now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import yaml

from uri3.paths import find_repo_root

CONTEXT_ENV = "URISH_CONTEXT"
DEFAULT_CONTEXT_ID = "local-dev"


def context_dir(root: Path | None = None) -> Path:
    repo = root or find_repo_root()
    return repo / "config" / "urish" / "contexts"


def load_context(context_id: str | None = None, *, root: Path | None = None) -> dict[str, Any]:
    repo = root or find_repo_root()
    selected = context_id or os.environ.get(CONTEXT_ENV) or DEFAULT_CONTEXT_ID
    path = context_dir(repo) / f"{selected}.yaml"
    if not path.exists():
        return {
            "metadata": {"id": selected},
            "spec": {"default_output": "text", "default_policy": "dev"},
        }
    payload = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    return payload if isinstance(payload, dict) else {}


def list_contexts(*, root: Path | None = None) -> list[str]:
    directory = context_dir(root)
    if not directory.exists():
        return [DEFAULT_CONTEXT_ID]
    return sorted(path.stem for path in directory.glob("*.yaml"))

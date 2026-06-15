from __future__ import annotations

from pathlib import Path
from typing import Any


def resolve_path(path: str, context: dict[str, Any]) -> Path:
    if isinstance(path, str) and path.startswith("file://"):
        # Support file:// URIs for local sources (graphs, flows, markpact, etc.)
        from urllib.parse import unquote
        p = path[7:]
        if p.startswith("/") and len(p) > 2 and p[2] == ":":
            p = p[1:]  # windows file:///c:...
        return Path(unquote(p))
    candidate = Path(path)
    if candidate.is_absolute():
        return candidate
    root = context.get("root")
    if root:
        return Path(root) / candidate
    from uri3.config.repo_root import find_repo_root

    return find_repo_root() / candidate


def execution_root(context: dict[str, Any]) -> Path:
    root = context.get("artifact_root") or context.get("root")
    if root:
        return Path(root)
    from uri3.config.repo_root import find_repo_root

    return find_repo_root()


def execution_options(payload: dict[str, Any], backend_extra: dict[str, Any]) -> dict[str, Any]:
    return {
        "dry_run": bool(payload.get("dry_run", backend_extra.get("dry_run", True))),
        "approve": bool(payload.get("approve", backend_extra.get("approve", False))),
        "browser": str(payload.get("browser", backend_extra.get("browser", "mock"))),
    }

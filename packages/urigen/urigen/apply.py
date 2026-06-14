from __future__ import annotations

from pathlib import Path
from typing import Any

from urigen.io import load_yaml


def apply_ecosystem(
    ecosystem_path: str | Path,
    *,
    approve: bool = False,
) -> dict[str, Any]:
    """Approval-gated apply placeholder.

    The MVP keeps apply idempotent and non-mutating. Future versions can merge
    contracts and registries here after verify succeeds.
    """
    ecosystem = load_yaml(ecosystem_path)
    ecosystem_id = (ecosystem.get("ecosystem") or {}).get("id")
    if not approve:
        return {
            "ok": False,
            "ecosystem": ecosystem_id,
            "status": "blocked",
            "reason": "apply requires --approve",
            "actions": [],
        }
    return {
        "ok": True,
        "ecosystem": ecosystem_id,
        "status": "skipped",
        "reason": "urigen MVP does not mutate repository registries yet",
        "actions": [
            {"action": "merge_contracts", "status": "skipped"},
            {"action": "copy_capabilities", "status": "skipped"},
            {"action": "update_deployments", "status": "skipped"},
            {"action": "ensure_running", "status": "skipped", "if_running": "reuse"},
        ],
    }

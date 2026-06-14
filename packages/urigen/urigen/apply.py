from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any

import yaml

from urigen.apply_planner import build_apply_plan
from urigen.io import load_yaml, write_json, write_yaml
from urigen.models import repo_root
from urigen.verify import verify_ecosystem


def _resolve_path(value: str, repo: Path) -> Path:
    path = Path(value)
    return path if path.is_absolute() else repo / value


def _merge_deployment_fragment(fragment_path: Path, target_path: Path, rollback_dir: Path) -> dict[str, Any]:
    fragment = load_yaml(fragment_path)
    backup = None
    if target_path.exists():
        rollback_dir.mkdir(parents=True, exist_ok=True)
        backup = rollback_dir / "agent_deployments.yaml.bak"
        shutil.copy2(target_path, backup)
        registry = load_yaml(target_path)
    else:
        registry = {"deployments": []}
    by_id = {item["id"]: item for item in registry.get("deployments") or [] if isinstance(item, dict)}
    for item in fragment.get("deployments") or []:
        if isinstance(item, dict) and item.get("id"):
            merged = dict(by_id.get(item["id"], {}))
            merged.update(item)
            by_id[str(item["id"])] = merged
    registry["deployments"] = sorted(by_id.values(), key=lambda row: str(row.get("id")))
    target_path.parent.mkdir(parents=True, exist_ok=True)
    target_path.write_text(yaml.safe_dump(registry, sort_keys=False, allow_unicode=True), encoding="utf-8")
    return {"merged": len(fragment.get("deployments") or []), "backup": str(backup) if backup else None}


def _copy_tree(source: Path, target: Path, rollback_dir: Path) -> dict[str, Any]:
    copied: list[str] = []
    if target.exists():
        rollback_dir.mkdir(parents=True, exist_ok=True)
        backup = rollback_dir / target.name
        if backup.exists():
            shutil.rmtree(backup)
        shutil.copytree(target, backup)
    target.mkdir(parents=True, exist_ok=True)
    for path in sorted(source.rglob("*")):
        if path.is_dir():
            continue
        rel = path.relative_to(source)
        dest = target / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, dest)
        copied.append(str(rel))
    return {"copied": copied}


def _copy_file(source: Path, target: Path, rollback_dir: Path) -> dict[str, Any]:
    if target.exists():
        rollback_dir.mkdir(parents=True, exist_ok=True)
        backup = rollback_dir / target.name
        shutil.copy2(target, backup)
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)
    return {"source": str(source), "target": str(target)}


def _execute_action(action: dict[str, Any], *, repo: Path, ecosystem_dir: Path, rollback_dir: Path) -> dict[str, Any]:
    operation = action.get("operation")
    source = _resolve_path(str(action.get("source")), repo)
    target = _resolve_path(str(action.get("target")), repo)

    if operation == "merge":
        if not source.is_file():
            return {"id": action["id"], "status": "skipped", "detail": "source missing"}
        detail = _copy_file(source, target, rollback_dir)
        return {"id": action["id"], "status": "completed", **detail}

    if operation == "copy_dir":
        if not source.is_dir():
            return {"id": action["id"], "status": "skipped", "detail": "source missing"}
        detail = _copy_tree(source, target, rollback_dir)
        return {"id": action["id"], "status": "completed", **detail}

    if operation == "merge_yaml_list":
        if not source.is_file():
            return {"id": action["id"], "status": "skipped", "detail": "source missing"}
        detail = _merge_deployment_fragment(source, target, rollback_dir)
        return {"id": action["id"], "status": "completed", **detail}

    if operation == "verify":
        verification = verify_ecosystem(
            ecosystem_dir / "ecosystem.yaml",
            root=repo if (repo / "docs" / "PACKAGE_BOUNDARIES.yaml").exists() else repo_root(None),
            write_report=False,
            skip_doctor=not (repo / "docs" / "PACKAGE_BOUNDARIES.yaml").exists(),
        )
        status = "completed" if verification.get("ok") else "failed"
        return {"id": action["id"], "status": status, "detail": verification}

    return {"id": action["id"], "status": "skipped", "detail": f"unknown operation {operation}"}


def apply_ecosystem(
    ecosystem_path: str | Path,
    *,
    approve: bool = False,
    plan_only: bool = False,
    root: str | Path | None = None,
) -> dict[str, Any]:
    repo = repo_root(root)
    ecosystem_file = Path(ecosystem_path).resolve()
    ecosystem_dir = ecosystem_file.parent
    ecosystem = load_yaml(ecosystem_file)
    eco_meta = ecosystem.get("metadata") or ecosystem.get("ecosystem") or {}
    eco_id = str(eco_meta.get("id") or "generated-ecosystem")

    plan = build_apply_plan(ecosystem_file, repo_root=repo)
    plan_path = write_yaml(ecosystem_dir / "apply_plan.yaml", plan)

    if plan_only or not approve:
        blocked = not approve and not plan_only
        return {
            "ok": not blocked,
            "ecosystem": eco_id,
            "status": "planned" if plan_only else "blocked",
            "reason": "apply requires --approve" if blocked else "apply plan generated",
            "plan_path": str(plan_path),
            "plan_uri": plan["uri"]["self"],
            "actions": plan["spec"]["actions"],
        }

    verify_root = repo if (repo / "docs" / "PACKAGE_BOUNDARIES.yaml").exists() else repo_root(None)
    skip_doctor = verify_root is not repo
    verification = verify_ecosystem(
        ecosystem_file,
        root=verify_root,
        write_report=False,
        skip_doctor=skip_doctor,
    )
    if not verification.get("ok"):
        return {
            "ok": False,
            "ecosystem": eco_id,
            "status": "blocked",
            "reason": "ecosystem verify failed before apply",
            "verification": verification,
            "plan_path": str(plan_path),
        }

    rollback_dir = ecosystem_dir / "rollback"
    action_results: list[dict[str, Any]] = []
    for action in plan["spec"]["actions"]:
        if action.get("requires_approval") and not approve:
            action_results.append({"id": action["id"], "status": "skipped", "detail": "approval required"})
            continue
        action_results.append(
            _execute_action(action, repo=repo, ecosystem_dir=ecosystem_dir, rollback_dir=rollback_dir)
        )

    failed = [item for item in action_results if item.get("status") == "failed"]
    ok = not failed
    lifecycle = dict((ecosystem.get("status") or {}).get("lifecycle") or {})
    lifecycle.update({"verified": True, "applied": ok, "active": ok})
    ecosystem["status"] = {"lifecycle": lifecycle, "apply_status": "applied" if ok else "failed"}
    write_yaml(ecosystem_file, ecosystem)

    result = {
        "$schema": "schemas/apply_result.schema.json",
        "apiVersion": "uri3.io/v1",
        "kind": "ApplyResult",
        "uri": {
            "self": f"apply://ecosystem/{eco_id}/result",
            "ecosystem": f"ecosystem://{eco_id}",
            "plan": plan["uri"]["self"],
        },
        "status": {
            "ok": ok,
            "execution_status": "completed",
            "service_result_status": "succeeded" if ok else "failed",
            "apply_status": "applied" if ok else "failed",
        },
        "actions": action_results,
        "rollback": {"available": rollback_dir.exists(), "path": str(rollback_dir)},
    }
    result_path = write_json(ecosystem_dir / "apply_result.json", result)
    return {
        "ok": ok,
        "ecosystem": eco_id,
        "status": "applied" if ok else "failed",
        "plan_path": str(plan_path),
        "result_path": str(result_path),
        "actions": action_results,
        "result": result,
    }

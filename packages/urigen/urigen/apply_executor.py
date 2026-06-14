from __future__ import annotations

import hashlib
import json
import shutil
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

import yaml

from urigen.io import load_yaml, write_json
from urigen.models import repo_root
from urigen.verify import verify_ecosystem


@dataclass
class RollbackEntry:
    action_id: str
    operation: str
    target: str
    backup_path: str | None = None
    applied_backup_path: str | None = None
    created: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class RollbackManifest:
    ecosystem_id: str
    entries: list[RollbackEntry] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "ecosystem_id": self.ecosystem_id,
            "entries": [entry.to_dict() for entry in self.entries],
        }


def _resolve_path(value: str, repo: Path) -> Path:
    path = Path(value)
    return path if path.is_absolute() else repo / value


def _file_digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def preview_action_diff(action: dict[str, Any], *, repo: Path) -> dict[str, Any]:
    operation = action.get("operation")
    source = _resolve_path(str(action.get("source", "")), repo)
    target = _resolve_path(str(action.get("target", "")), repo)
    preview: dict[str, Any] = {
        "id": action.get("id"),
        "operation": operation,
        "source": str(source),
        "target": str(target),
    }
    if operation in {"merge", "copy_file"}:
        if not source.is_file():
            preview["change"] = "skip"
            preview["reason"] = "source missing"
        elif not target.exists():
            preview["change"] = "create"
        elif _file_digest(source) == _file_digest(target):
            preview["change"] = "unchanged"
        else:
            preview["change"] = "update"
    elif operation == "copy_dir":
        if not source.is_dir():
            preview["change"] = "skip"
            preview["reason"] = "source missing"
        elif not target.exists():
            preview["change"] = "create"
        else:
            preview["change"] = "merge"
            preview["files"] = len(list(source.rglob("*")))
    elif operation == "merge_yaml_list":
        if not source.is_file():
            preview["change"] = "skip"
        else:
            fragment = load_yaml(source)
            preview["change"] = "merge"
            preview["items"] = len(fragment.get("deployments") or [])
    elif operation == "verify":
        preview["change"] = "verify"
    else:
        preview["change"] = "unknown"
    return preview


def build_plan_diff(plan: dict[str, Any], *, repo: Path) -> list[dict[str, Any]]:
    return [preview_action_diff(action, repo=repo) for action in plan.get("spec", {}).get("actions") or []]


def _copy_file(
    action_id: str,
    source: Path,
    target: Path,
    rollback_dir: Path,
) -> tuple[dict[str, Any], RollbackEntry | None]:
    if not source.is_file():
        return {"id": action_id, "status": "skipped", "detail": "source missing"}, None
    if target.exists() and _file_digest(source) == _file_digest(target):
        return {"id": action_id, "status": "unchanged", "detail": {"target": str(target)}}, None

    entry = RollbackEntry(
        action_id=action_id,
        operation="copy_file",
        target=str(target),
        created=not target.exists(),
    )
    if target.exists():
        rollback_dir.mkdir(parents=True, exist_ok=True)
        pre_backup = rollback_dir / f"{action_id}_{target.name}.pre"
        shutil.copy2(target, pre_backup)
        entry.backup_path = str(pre_backup)
        status = "updated"
    else:
        status = "created"

    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)
    rollback_dir.mkdir(parents=True, exist_ok=True)
    applied_backup = rollback_dir / f"{action_id}_{target.name}.applied"
    shutil.copy2(target, applied_backup)
    entry.applied_backup_path = str(applied_backup)
    return (
        {"id": action_id, "status": status, "detail": {"source": str(source), "target": str(target)}},
        entry,
    )


def _copy_tree(
    action_id: str,
    source: Path,
    target: Path,
    rollback_dir: Path,
) -> tuple[dict[str, Any], RollbackEntry | None]:
    if not source.is_dir():
        return {"id": action_id, "status": "skipped", "detail": "source missing"}, None

    entry = RollbackEntry(
        action_id=action_id,
        operation="copy_dir",
        target=str(target),
        created=not target.exists(),
    )
    if target.exists():
        rollback_dir.mkdir(parents=True, exist_ok=True)
        pre_backup = rollback_dir / f"{action_id}_{target.name}.pre"
        if pre_backup.exists():
            shutil.rmtree(pre_backup)
        shutil.copytree(target, pre_backup)
        entry.backup_path = str(pre_backup)
        status = "updated"
    else:
        status = "created"

    target.mkdir(parents=True, exist_ok=True)
    copied: list[str] = []
    for path in sorted(source.rglob("*")):
        if path.is_dir():
            continue
        rel = path.relative_to(source)
        dest = target / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, dest)
        copied.append(str(rel))
    rollback_dir.mkdir(parents=True, exist_ok=True)
    applied_backup = rollback_dir / f"{action_id}_{target.name}.applied"
    if applied_backup.exists():
        shutil.rmtree(applied_backup)
    shutil.copytree(target, applied_backup)
    entry.applied_backup_path = str(applied_backup)
    return (
        {"id": action_id, "status": status, "detail": {"copied": copied, "target": str(target)}},
        entry,
    )


def _merge_deployment_fragment(
    action_id: str,
    fragment_path: Path,
    target_path: Path,
    rollback_dir: Path,
) -> tuple[dict[str, Any], RollbackEntry | None]:
    if not fragment_path.is_file():
        return {"id": action_id, "status": "skipped", "detail": "source missing"}, None

    fragment = load_yaml(fragment_path)
    entry = RollbackEntry(
        action_id=action_id,
        operation="merge_yaml_list",
        target=str(target_path),
        created=not target_path.exists(),
    )
    if target_path.exists():
        rollback_dir.mkdir(parents=True, exist_ok=True)
        backup = rollback_dir / f"{action_id}_agent_deployments.yaml.bak"
        shutil.copy2(target_path, backup)
        entry.backup_path = str(backup)
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
    rollback_dir.mkdir(parents=True, exist_ok=True)
    post_backup = rollback_dir / f"{action_id}_agent_deployments.yaml.applied"
    shutil.copy2(target_path, post_backup)
    entry.applied_backup_path = str(post_backup)
    return (
        {
            "id": action_id,
            "status": "updated" if entry.backup_path else "created",
            "detail": {"merged": len(fragment.get("deployments") or []), "target": str(target_path)},
        },
        entry,
    )


def execute_action(
    action: dict[str, Any],
    *,
    repo: Path,
    ecosystem_dir: Path,
    rollback_dir: Path,
) -> tuple[dict[str, Any], RollbackEntry | None]:
    operation = action.get("operation")
    action_id = str(action.get("id") or "unknown")
    source = _resolve_path(str(action.get("source", "")), repo)
    target = _resolve_path(str(action.get("target", "")), repo)

    if operation in {"merge", "copy_file"}:
        return _copy_file(action_id, source, target, rollback_dir)
    if operation == "copy_dir":
        return _copy_tree(action_id, source, target, rollback_dir)
    if operation == "merge_yaml_list":
        return _merge_deployment_fragment(action_id, source, target, rollback_dir)
    if operation == "verify":
        verify_root = repo if (repo / "docs" / "PACKAGE_BOUNDARIES.yaml").exists() else repo_root(None)
        verification = verify_ecosystem(
            ecosystem_dir / "ecosystem.yaml",
            root=verify_root,
            write_report=False,
            skip_doctor=verify_root is not repo,
        )
        status = "completed" if verification.get("ok") else "failed"
        return {"id": action_id, "status": status, "detail": verification}, None
    return {"id": action_id, "status": "skipped", "detail": f"unknown operation {operation}"}, None


def rollback_manifest(manifest: RollbackManifest, *, repo: Path, manual: bool = False) -> dict[str, Any]:
    restored: list[str] = []
    deleted: list[str] = []
    errors: list[str] = []

    for entry in reversed(manifest.entries):
        target = Path(entry.target)
        try:
            if manual:
                backup_ref = entry.applied_backup_path or entry.backup_path
            elif entry.created:
                backup_ref = None
            else:
                backup_ref = entry.backup_path

            if backup_ref:
                backup = Path(backup_ref)
                if not backup.exists():
                    errors.append(f"missing backup for {entry.action_id}: {backup_ref}")
                    continue
                target.parent.mkdir(parents=True, exist_ok=True)
                if backup.is_dir():
                    if target.exists():
                        shutil.rmtree(target)
                    shutil.copytree(backup, target)
                else:
                    shutil.copy2(backup, target)
                restored.append(str(target))
            elif entry.created and target.exists():
                if target.is_dir():
                    shutil.rmtree(target)
                else:
                    target.unlink()
                deleted.append(str(target))
        except OSError as exc:
            errors.append(f"{entry.action_id}: {exc}")

    return {
        "ok": not errors,
        "restored": restored,
        "deleted": deleted,
        "errors": errors,
    }


def write_rollback_manifest(manifest: RollbackManifest, rollback_dir: Path) -> Path:
    rollback_dir.mkdir(parents=True, exist_ok=True)
    path = rollback_dir / "manifest.json"
    path.write_text(json.dumps(manifest.to_dict(), indent=2), encoding="utf-8")
    return path


def load_rollback_manifest(rollback_dir: Path) -> RollbackManifest:
    path = rollback_dir / "manifest.json"
    if not path.is_file():
        raise FileNotFoundError(f"rollback manifest not found: {path}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    entries = [RollbackEntry(**item) for item in payload.get("entries") or []]
    return RollbackManifest(ecosystem_id=str(payload.get("ecosystem_id") or ""), entries=entries)


def execute_apply_plan(
    plan: dict[str, Any],
    *,
    repo: Path,
    ecosystem_dir: Path,
    ecosystem_id: str,
    approve: bool = True,
) -> dict[str, Any]:
    rollback_dir = ecosystem_dir / "rollback"
    manifest = RollbackManifest(ecosystem_id=ecosystem_id)
    action_results: list[dict[str, Any]] = []
    failed = False
    rolled_back = False
    rollback_result: dict[str, Any] | None = None

    for action in plan.get("spec", {}).get("actions") or []:
        if action.get("requires_approval") and not approve:
            action_results.append({"id": action["id"], "status": "blocked", "detail": "approval required"})
            continue
        result, entry = execute_action(action, repo=repo, ecosystem_dir=ecosystem_dir, rollback_dir=rollback_dir)
        action_results.append(result)
        if entry is not None:
            manifest.entries.append(entry)
        if result.get("status") == "failed":
            failed = True
            rollback_result = rollback_manifest(manifest, repo=repo, manual=False)
            rolled_back = True
            write_rollback_manifest(manifest, rollback_dir)
            break

    if manifest.entries:
        write_rollback_manifest(manifest, rollback_dir)

    ok = not failed
    execution_status = "completed"
    if rolled_back:
        execution_status = "rolled_back"
    elif failed:
        execution_status = "failed"

    return {
        "ok": ok,
        "action_results": action_results,
        "execution_status": execution_status,
        "rollback": {
            "available": rollback_dir.exists(),
            "path": str(rollback_dir),
            "manifest": str(rollback_dir / "manifest.json") if (rollback_dir / "manifest.json").exists() else None,
            "rolled_back": rolled_back,
            "result": rollback_result,
        },
    }


def rollback_apply(
    ecosystem_dir: str | Path,
    *,
    repo: Path,
) -> dict[str, Any]:
    ecosystem_dir = Path(ecosystem_dir)
    rollback_dir = ecosystem_dir / "rollback"
    manifest = load_rollback_manifest(rollback_dir)
    result = rollback_manifest(manifest, repo=repo, manual=True)
    payload = {
        "ok": result.get("ok", False),
        "status": "rolled_back" if result.get("ok") else "rollback_failed",
        "rollback": result,
        "manifest": str(rollback_dir / "manifest.json"),
    }
    write_json(ecosystem_dir / "rollback_result.json", payload)
    return payload

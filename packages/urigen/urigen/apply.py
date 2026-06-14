from __future__ import annotations

from pathlib import Path
from typing import Any

from urigen.apply_executor import (
    build_plan_diff,
    execute_apply_plan,
    rollback_apply,
)
from urigen.apply_planner import build_apply_plan
from urigen.apply_validate import validate_apply_artifact
from urigen.io import load_yaml, write_json, write_yaml
from urigen.models import repo_root
from urigen.verify import verify_ecosystem


def _ecosystem_meta(ecosystem: dict[str, Any]) -> tuple[str, dict[str, Any]]:
    eco_meta = ecosystem.get("metadata") or ecosystem.get("ecosystem") or {}
    eco_id = str(eco_meta.get("id") or "generated-ecosystem")
    return eco_id, eco_meta


def _planned_response(
    *,
    eco_id: str,
    plan_path: Path,
    plan: dict[str, Any],
    diff: dict[str, Any],
    plan_errors: list[str] | None,
    plan_only: bool,
    approve: bool,
) -> dict[str, Any]:
    blocked = not approve and not plan_only
    return {
        "ok": not blocked,
        "ecosystem": eco_id,
        "status": "planned" if plan_only else "blocked",
        "reason": "apply requires --approve" if blocked else "apply plan generated",
        "plan_path": str(plan_path),
        "plan_uri": plan["uri"]["self"],
        "actions": plan["spec"]["actions"],
        "diff": diff,
        "schema_errors": plan_errors or None,
    }


def _verify_before_apply(ecosystem_file: Path, *, repo: Path) -> dict[str, Any]:
    verify_root = repo if (repo / "docs" / "PACKAGE_BOUNDARIES.yaml").exists() else repo_root(None)
    skip_doctor = verify_root is not repo
    return verify_ecosystem(
        ecosystem_file,
        root=verify_root,
        write_report=False,
        skip_doctor=skip_doctor,
    )


def _update_lifecycle(ecosystem: dict[str, Any], *, ok: bool, execution_status: str) -> str:
    lifecycle = dict((ecosystem.get("status") or {}).get("lifecycle") or {})
    if execution_status == "rolled_back":
        lifecycle.update({"verified": True, "applied": False, "active": False, "rolled_back": True})
        apply_status = "rolled_back"
    else:
        lifecycle.update({"verified": True, "applied": ok, "active": ok})
        apply_status = "applied" if ok else "failed"
    ecosystem["status"] = {"lifecycle": lifecycle, "apply_status": apply_status}
    return apply_status


def _build_apply_result(
    *,
    eco_id: str,
    plan: dict[str, Any],
    ok: bool,
    execution_status: str,
    apply_status: str,
    action_results: list[dict[str, Any]],
    execution: dict[str, Any],
    diff: dict[str, Any],
    repo: Path,
) -> dict[str, Any]:
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
            "execution_status": execution_status,
            "service_result_status": "succeeded" if ok else "failed",
            "apply_status": apply_status,
        },
        "actions": action_results,
        "rollback": execution["rollback"],
        "diff": diff,
    }
    result_errors = validate_apply_artifact(result, "apply_result.schema.json", repo=repo)
    if result_errors:
        result["schema_warnings"] = result_errors
    return result


def apply_ecosystem(
    ecosystem_path: str | Path,
    *,
    approve: bool = False,
    plan_only: bool = False,
    rollback: bool = False,
    root: str | Path | None = None,
) -> dict[str, Any]:
    repo = repo_root(root)
    ecosystem_file = Path(ecosystem_path).resolve()
    ecosystem_dir = ecosystem_file.parent
    ecosystem = load_yaml(ecosystem_file)
    eco_id, _ = _ecosystem_meta(ecosystem)

    if rollback:
        payload = rollback_apply(ecosystem_dir, repo=repo)
        payload["ecosystem"] = eco_id
        return payload

    plan = build_apply_plan(ecosystem_file, repo_root=repo)
    plan_errors = validate_apply_artifact(plan, "apply_plan.schema.json", repo=repo)
    plan_path = write_yaml(ecosystem_dir / "apply_plan.yaml", plan)
    diff = build_plan_diff(plan, repo=repo)

    if plan_only or not approve:
        return _planned_response(
            eco_id=eco_id,
            plan_path=plan_path,
            plan=plan,
            diff=diff,
            plan_errors=plan_errors,
            plan_only=plan_only,
            approve=approve,
        )

    verification = _verify_before_apply(ecosystem_file, repo=repo)
    if not verification.get("ok"):
        return {
            "ok": False,
            "ecosystem": eco_id,
            "status": "blocked",
            "reason": "ecosystem verify failed before apply",
            "verification": verification,
            "plan_path": str(plan_path),
            "diff": diff,
        }

    execution = execute_apply_plan(
        plan,
        repo=repo,
        ecosystem_dir=ecosystem_dir,
        ecosystem_id=eco_id,
        approve=approve,
    )
    action_results = execution["action_results"]
    ok = execution["ok"]
    execution_status = execution["execution_status"]
    apply_status = _update_lifecycle(ecosystem, ok=ok, execution_status=execution_status)
    write_yaml(ecosystem_file, ecosystem)

    result = _build_apply_result(
        eco_id=eco_id,
        plan=plan,
        ok=ok,
        execution_status=execution_status,
        apply_status=apply_status,
        action_results=action_results,
        execution=execution,
        diff=diff,
        repo=repo,
    )
    result_path = write_json(ecosystem_dir / "apply_result.json", result)
    return {
        "ok": ok,
        "ecosystem": eco_id,
        "status": apply_status,
        "plan_path": str(plan_path),
        "result_path": str(result_path),
        "actions": action_results,
        "diff": diff,
        "rollback": execution["rollback"],
        "result": result,
    }

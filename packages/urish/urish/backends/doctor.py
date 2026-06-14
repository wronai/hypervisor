from __future__ import annotations

from typing import Any

from uri3.doctor.runner import run_doctor
from uri3.paths import find_repo_root


def doctor_all(*, root=None, strict: bool = False) -> dict[str, Any]:
    repo = root or find_repo_root()
    checks: list[dict[str, Any]] = []
    try:
        from uri2run.doctor import doctor_transport_dependencies

        transport = doctor_transport_dependencies()
        checks.append({"id": "uri2run.transports", **transport})
    except Exception as exc:  # noqa: BLE001
        checks.append({"id": "uri2run.transports", "ok": False, "error": str(exc)})
    try:
        uri3 = run_doctor(root=repo)
        checks.append({"id": "uri3.doctor", **uri3})
    except Exception as exc:  # noqa: BLE001
        checks.append({"id": "uri3.doctor", "ok": False, "error": str(exc)})

    if strict:
        checks.extend(_artifact_gate_checks(repo, strict=strict))

    failed = [item for item in checks if not item.get("ok")]
    return {
        "ok": not failed,
        "strict": strict,
        "checks": checks,
        "failed": len(failed),
        "result_type": "doctor",
        "workflow_status": "completed" if not failed else "failed",
        "execution_status": "completed",
        "service_result_status": "succeeded" if not failed else "failed",
    }


def _artifact_gate_checks(repo, *, strict: bool) -> list[dict[str, Any]]:
    from hypervisor.artifacts.gate import check_artifacts, check_lifecycle_coverage, check_schemas

    checks: list[dict[str, Any]] = []
    try:
        schemas = check_schemas(repo)
        checks.append({"id": "artifacts.schemas", **schemas})
    except Exception as exc:  # noqa: BLE001
        checks.append({"id": "artifacts.schemas", "ok": False, "error": str(exc)})

    artifact_patterns = [
        "output/incidents/**/*.yaml",
        "output/tickets/**/*.yaml",
        "evolution/proposals/**/*.yaml",
        "output/repair-plans/**/*.yaml",
    ]
    try:
        artifacts = check_artifacts(repo, patterns=artifact_patterns)
        checks.append(
            {
                "id": "artifacts.incidents_tickets",
                "patterns": artifact_patterns,
                **artifacts,
            }
        )
    except Exception as exc:  # noqa: BLE001
        checks.append({"id": "artifacts.incidents_tickets", "ok": False, "error": str(exc)})

    try:
        lifecycle = check_lifecycle_coverage(repo, strict=strict)
        checks.append({"id": "artifacts.lifecycle", **lifecycle})
    except Exception as exc:  # noqa: BLE001
        checks.append({"id": "artifacts.lifecycle", "ok": False, "error": str(exc)})

    return checks

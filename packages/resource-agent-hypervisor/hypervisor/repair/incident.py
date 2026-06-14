from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import yaml

from hypervisor.paths import find_repo_root
from hypervisor.repair.models import IncidentArtifact, Symptom
from hypervisor.repair.validator import validate_incident_dict


def _now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _incident_id() -> str:
    stamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
    return f"inc_{stamp}"


def incident_uri(agent_id: str, incident_id: str) -> str:
    return f"incident://agent/{agent_id}/{incident_id}"


def incident_storage_path(repo_root: Path, agent_id: str, incident_id: str) -> Path:
    day = datetime.now(UTC).strftime("%Y-%m-%d")
    return repo_root / "output" / "incidents" / day / agent_id / f"{incident_id}.yaml"


def build_incident_from_inspection(
    inspection: dict[str, Any],
    *,
    classification: dict[str, Any] | None = None,
    created_by: str = "agent://repair-supervisor",
    source: str | None = None,
) -> IncidentArtifact:
    agent_id = str(inspection["id"])
    metadata_id = _incident_id()
    readiness = inspection.get("readiness") or {}
    process = inspection.get("process") or {}
    health = inspection.get("health") or {}
    logs = inspection.get("log_errors") or {}

    symptoms: list[Symptom] = []
    for item in inspection.get("incidents") or []:
        symptoms.append(
            Symptom(
                code=str(item.get("code") or "UNKNOWN"),
                message=str(item.get("detail") or item.get("code") or "incident"),
                severity="error",
            )
        )
    for item in inspection.get("warnings") or []:
        symptoms.append(
            Symptom(
                code=str(item.get("code") or "WARNING"),
                message=str(item.get("detail") or item.get("code") or "warning"),
                severity="warning",
            )
        )
    if not symptoms:
        symptoms.append(
            Symptom(
                code="SERVICE_UNHEALTHY",
                message="Agent inspection reported degraded service status.",
                severity="error",
            )
        )

    runtime_state = inspection.get("runtime_state") or {}
    return IncidentArtifact(
        metadata_id=metadata_id,
        agent_id=agent_id,
        created_at=_now_iso(),
        created_by=created_by,
        source=source or f"hypervisor://agent/{agent_id}/supervise",
        uri={
            "self": incident_uri(agent_id, metadata_id),
            "subject": str(inspection.get("agent_ref") or f"agent://{agent_id.split('.')[0]}"),
            "deployment": f"hypervisor://local/{agent_id}",
            "runtime_state": f"runtime://agent/{agent_id}/state",
            "health": f"health://agent/{agent_id}",
            "logs": str(inspection.get("log_uri") or f"log://hypervisor?grep={agent_id}"),
        },
        status={
            "lifecycle_status": str(
                inspection.get("runtime_status") or readiness.get("process") or "unknown"
            ),
            "health_status": "ok" if health.get("ok") else "failed",
            "workflow_status": "failed" if not inspection.get("ok") else "completed",
            "execution_status": "completed",
            "service_result_status": "failed" if not inspection.get("ok") else "succeeded",
        },
        symptoms=symptoms,
        evidence={
            "runtime": {
                "pid": process.get("pid"),
                "running": process.get("running"),
                "effective_port": readiness.get("effective_port"),
                "declared_health_uri": readiness.get("declared_health_uri"),
                "effective_health_uri": readiness.get("effective_health_uri"),
                "runtime_state_path": str(
                    find_repo_root() / "output" / "runtime" / "agents" / agent_id / "state.json"
                ),
                "command": runtime_state.get("command"),
                "stored_health_uri": runtime_state.get("health_uri"),
            },
            "health_check": {
                "uri": health.get("uri"),
                "ok": health.get("ok"),
                "status_code": health.get("status_code"),
                "error": health.get("error"),
            },
            "logs": {
                "uri": logs.get("uri") or inspection.get("log_uri"),
                "error_count": logs.get("error_count", 0),
                "entries": (logs.get("entries") or [])[:5],
            },
        },
        classification=classification or {},
    )


def write_incident(
    incident: IncidentArtifact,
    *,
    repo_root: Path | None = None,
) -> Path:
    repo = repo_root or find_repo_root()
    payload = incident.to_dict(repo_root=repo)
    errors = validate_incident_dict(payload, repo)
    if errors:
        raise ValueError(f"incident validation failed: {errors[:3]}")
    path = incident_storage_path(repo, incident.agent_id, incident.metadata_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(payload, sort_keys=False, allow_unicode=True), encoding="utf-8")
    return path


def load_incident(path: str | Path, *, repo_root: Path | None = None) -> dict[str, Any]:
    repo = repo_root or find_repo_root()
    payload = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must contain YAML mapping")
    errors = validate_incident_dict(payload, repo)
    if errors:
        raise ValueError(f"invalid incident artifact: {errors[:3]}")
    return payload

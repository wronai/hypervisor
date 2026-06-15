from __future__ import annotations

import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import yaml

from hypervisor_dashboard_agent.uri_client import inspect_agent, list_agent_deployments


# Prefer shared if available (from main hypervisor package); fallback for standalone.
try:
    from hypervisor.deployment_registry.runtime_state import now_iso as _now_iso
except Exception:  # noqa: BLE001
    from datetime import UTC, datetime
    def _now_iso() -> str:
        return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _parse_ts(value: str | None, *, fallback: float) -> str:
    if not value:
        return datetime.fromtimestamp(fallback, UTC).replace(microsecond=0).isoformat().replace(
            "+00:00", "Z"
        )
    text = str(value).strip()
    if text.endswith("Z"):
        return text
    if "+" in text or text.count("-") > 2:
        return text
    return text + "Z"


def _extract_agent_id(metadata: dict, path: Path) -> str:
    return str(metadata.get("agent_id") or path.parent.name)

def _extract_incident_id(metadata: dict, path: Path) -> str:
    return str(metadata.get("id") or path.stem)

def _extract_summary(symptoms: list) -> str:
    if isinstance(symptoms, list) and symptoms:
        first = symptoms[0]
        if isinstance(first, dict):
            return str(first.get("message") or first.get("code") or "")
    return ""

def _build_incident_event(path: Path, root: Path, payload: dict[str, Any]) -> dict[str, Any]:
    metadata = payload.get("metadata") or {}
    agent_id = _extract_agent_id(metadata, path)
    incident_id = _extract_incident_id(metadata, path)
    uri_block = payload.get("uri") or {}
    self_uri = uri_block.get("self") if isinstance(uri_block, dict) else None
    summary = _extract_summary(payload.get("symptoms") or [])
    created_at = str(metadata.get("created_at") or "")
    return {
        "id": f"incident:{agent_id}:{incident_id}",
        "type": "incident.created",
        "ts": _parse_ts(created_at, fallback=path.stat().st_mtime),
        "agent_id": agent_id,
        "uri": self_uri or f"incident://agent/{agent_id}/{incident_id}",
        "summary": summary or f"incident {incident_id}",
        "source": str(path.relative_to(root)),
    }


def _incident_events(root: Path, *, limit: int) -> list[dict[str, Any]]:
    incidents_dir = root / "output" / "incidents"
    if not incidents_dir.is_dir():
        return []
    paths = sorted(incidents_dir.rglob("*.yaml"), key=lambda p: p.stat().st_mtime, reverse=True)
    events: list[dict[str, Any]] = []
    for path in paths[:limit]:
        try:
            payload = yaml.safe_load(path.read_text(encoding="utf-8"))
        except (OSError, yaml.YAMLError):
            continue
        if not isinstance(payload, dict):
            continue
        events.append(_build_incident_event(path, root, payload))
    return events


def _monitor_events(root: Path, *, limit: int) -> list[dict[str, Any]]:
    monitoring_dir = root / "output" / "monitoring"
    if not monitoring_dir.is_dir():
        return []
    events: list[dict[str, Any]] = []
    paths = sorted(
        monitoring_dir.glob("*.json"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    for path in paths:
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if not isinstance(payload, dict):
            continue
        status = str(payload.get("status") or payload.get("alert") or "monitor.snapshot")
        checked_at = str(payload.get("checked_at") or payload.get("timestamp") or "")
        events.append(
            {
                "id": f"monitor:{path.stem}:{int(path.stat().st_mtime)}",
                "type": "monitor.snapshot",
                "ts": _parse_ts(checked_at, fallback=path.stat().st_mtime),
                "agent_id": None,
                "uri": payload.get("url") or f"resource://monitor/{path.stem}",
                "summary": status,
                "source": str(path.relative_to(root)),
            }
        )
        if len(events) >= limit:
            break
    return events


def _derive_service_status(inspection: dict[str, Any], health_ok: bool) -> str:
    service_status = str(inspection.get("service_status") or ("healthy" if health_ok else "degraded"))
    if health_ok and service_status in {"stopped", "degraded", "failed"}:
        service_status = "healthy"
    return service_status


def _health_summary(service_status: str, incidents: list[Any]) -> str:
    if incidents and isinstance(incidents, list):
        first = incidents[0]
        if isinstance(first, dict):
            code = first.get("code", "")
            if code:
                return f"{service_status}: {code}"
    return service_status


def _agent_health_event(root: Path, deployment: dict[str, Any]) -> dict[str, Any] | None:
    agent_id = str(deployment.get("id") or "")
    if not agent_id:
        return None
    try:
        inspection = inspect_agent(agent_id, root=root, timeout=0.75, log_limit=3)
    except Exception:  # noqa: BLE001 — best-effort sidebar feed
        return None
    health_ok = bool((inspection.get("health") or {}).get("ok"))
    ok = bool(inspection.get("ok") or health_ok)
    service_status = _derive_service_status(inspection, health_ok)
    summary = _health_summary(service_status, inspection.get("incidents") or [])
    return {
        "id": f"agent.health:{agent_id}:{service_status}",
        "type": "agent.health",
        "ts": _now_iso(),
        "agent_id": agent_id,
        "uri": deployment.get("health_uri") or f"health://agent/{agent_id}",
        "summary": summary.strip(),
        "ok": ok,
        "view_uri": deployment.get("view_uri"),
    }


def _agent_health_events(root: Path, *, limit: int) -> list[dict[str, Any]]:
    deployments = list_agent_deployments(root=root)[:limit]
    if not deployments:
        return []
    events: list[dict[str, Any]] = []
    max_workers = min(6, len(deployments))
    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        futures = [pool.submit(_agent_health_event, root, deployment) for deployment in deployments]
        for future in as_completed(futures):
            event = future.result()
            if event:
                events.append(event)
    return events


def _should_include_log_event(payload: dict[str, Any]) -> bool:
    level = str(payload.get("level") or "INFO").upper()
    kind = str(payload.get("kind") or "")
    return kind == "LogEvent" or level in {"ERROR", "WARNING", "CRITICAL"}


def _agent_id_from_log_subject(subject: str | None) -> str | None:
    if not isinstance(subject, str) or not subject.startswith("health://agent/"):
        return None
    return subject.removeprefix("health://agent/").split("/")[0] or None


def _log_event_from_payload(
    payload: dict[str, Any],
    *,
    path: Path,
    line_no: int,
    root: Path,
) -> dict[str, Any]:
    level = str(payload.get("level") or "INFO").upper()
    event_block = payload.get("event") if isinstance(payload.get("event"), dict) else {}
    code = str(event_block.get("code") or level)
    message = str(
        payload.get("message")
        or event_block.get("message")
        or payload.get("msg")
        or code
    )[:180]
    uri_block = payload.get("uri") if isinstance(payload.get("uri"), dict) else {}
    log_uri = uri_block.get("self") if isinstance(uri_block, dict) else None
    subject = uri_block.get("subject") if isinstance(uri_block, dict) else None
    ts = str(payload.get("timestamp") or payload.get("time") or "")
    return {
        "id": f"log:{path.stem}:{line_no}:{code}",
        "type": "log.event",
        "ts": _parse_ts(ts, fallback=path.stat().st_mtime),
        "agent_id": _agent_id_from_log_subject(subject),
        "uri": log_uri or f"log://file/{path.relative_to(root)}",
        "summary": f"{level}: {message}",
        "source": str(path.relative_to(root)),
        "level": level,
    }


def _recent_jsonl_lines(path: Path) -> list[tuple[int, str]]:
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return []
    start_line = max(1, len(lines) - 39)
    return list(enumerate(lines[-40:], start=start_line))


def _events_from_jsonl_path(path: Path, *, root: Path, limit: int) -> list[dict[str, Any]]:
    events: list[dict[str, Any]] = []
    for line_no, line in reversed(_recent_jsonl_lines(path)):
        stripped = line.strip()
        if not stripped:
            continue
        try:
            payload = json.loads(stripped)
        except json.JSONDecodeError:
            continue
        if not isinstance(payload, dict) or not _should_include_log_event(payload):
            continue
        events.append(_log_event_from_payload(payload, path=path, line_no=line_no, root=root))
        if len(events) >= limit:
            break
    return events


def _log_jsonl_events(root: Path, *, limit: int) -> list[dict[str, Any]]:
    logs_dir = root / "output" / "logs"
    if not logs_dir.is_dir():
        return []
    paths = sorted(
        logs_dir.rglob("*.jsonl"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    events: list[dict[str, Any]] = []
    for path in paths:
        events.extend(_events_from_jsonl_path(path, root=root, limit=limit - len(events)))
        if len(events) >= limit:
            return events
    return events


def collect_system_events(*, root: Path, limit: int = 30) -> list[dict[str, Any]]:
    """Merge incidents, monitor snapshots, log events, and live agent health."""
    per_source = max(2, min(4, limit))
    merged: dict[str, dict[str, Any]] = {}
    for event in (
        *_incident_events(root, limit=per_source),
        *_monitor_events(root, limit=per_source),
        *_log_jsonl_events(root, limit=per_source),
        *_agent_health_events(root, limit=per_source),
    ):
        merged[event["id"]] = event
    events = list(merged.values())
    events.sort(key=lambda item: item.get("ts") or "", reverse=True)
    return events[:limit]


def filter_events_since(events: list[dict[str, Any]], since: str | None) -> list[dict[str, Any]]:
    if not since:
        return events
    return [event for event in events if (event.get("ts") or "") > since]

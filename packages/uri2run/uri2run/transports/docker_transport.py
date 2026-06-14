from __future__ import annotations

from pathlib import Path
from typing import Any

from uri3.results import ServiceResult, service_result

from uri2run.result import error_result


def _docker_ok(data: dict[str, Any]) -> bool:
    if "ok" in data:
        return bool(data["ok"])
    if data.get("dry_run"):
        return True
    return "error" not in data


def run_docker(target: str, payload: dict[str, Any], context: dict[str, Any]) -> ServiceResult:
    from uri3.docker.controller import control_docker

    root = Path(str(context.get("root", ".")))
    try:
        data = control_docker(target, root=root, payload=payload or None)
    except (ValueError, RuntimeError, OSError) as exc:
        return error_result("DOCKER_TRANSPORT_FAILED", str(exc), result_type="docker")
    if not isinstance(data, dict):
        return service_result(
            ok=True,
            result_type="docker",
            data={"result": data},
            meta={"transport": "docker", "target": target},
        )
    return service_result(
        ok=_docker_ok(data),
        result_type="docker",
        data=data,
        meta={"transport": "docker", "target": target, "action": data.get("action")},
    )


def run_docker_transport(
    backend: dict[str, Any],
    payload: dict[str, Any],
    context: dict[str, Any],
) -> ServiceResult:
    target = backend.get("target") or backend.get("url")
    if not target:
        return error_result("BACKEND_INVALID", "docker backend missing target/url")
    return run_docker(str(target), payload, context)

from __future__ import annotations

from pathlib import Path
from typing import Any

from touri.validator import validate_manifest
from uri2flow.expander import expand_flow
from uri2flow.validator import validate_flow
from uri3.doctor.runner import run_doctor
from uri3.graph import validate_workflow_graph
from uri3.resolvers.explain import explain_uri

from urigen.io import load_yaml, write_json
from urigen.models import repo_root


def verify_ecosystem(
    ecosystem_path: str | Path,
    *,
    root: str | Path | None = None,
    write_report: bool = True,
    skip_doctor: bool = False,
) -> dict[str, Any]:
    """Verify an ecosystem without mutating repository registries or deployments."""
    path = Path(ecosystem_path)
    base = path.parent
    repo = repo_root(root)
    ecosystem = load_yaml(path)
    registry = base / "capabilities"
    checks = [
        _check_capabilities(ecosystem, base),
        _check_flows(ecosystem, base),
        _check_explain(ecosystem, registry, repo),
    ]
    if not skip_doctor:
        checks.append(_check_doctor(repo, registry))
    payload = {
        "ok": all(item["ok"] for item in checks),
        "ecosystem": (ecosystem.get("metadata") or ecosystem.get("ecosystem") or {}).get("id"),
        "checks": checks,
        "warnings": [warning for item in checks for warning in item.get("warnings", [])],
    }
    if write_report:
        report_path = write_json(base / "verify_report.json", payload)
        payload["report"] = str(report_path)
    return payload


def _check_result(check_id: str, ok: bool, **detail: Any) -> dict[str, Any]:
    return {"id": check_id, "ok": ok, **detail}


def _resolve(base: Path, value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else base / path


def _check_capabilities(ecosystem: dict[str, Any], base: Path) -> dict[str, Any]:
    results: list[dict[str, Any]] = []
    errors: list[str] = []
    for item in ecosystem.get("capabilities") or []:
        source = _resolve(base, str(item.get("source") or ""))
        if not source.is_file():
            errors.append(f"missing capability source: {source}")
            continue
        result = validate_manifest(source)
        results.append({"source": str(source), **result})
        if not result.get("ok"):
            errors.extend(str(err) for err in result.get("errors") or [])
    return _check_result("capabilities", ok=not errors, results=results, errors=errors)


def _check_flows(ecosystem: dict[str, Any], base: Path) -> dict[str, Any]:
    results: list[dict[str, Any]] = []
    errors: list[str] = []
    for item in ecosystem.get("flows") or []:
        source = _resolve(base, str(item.get("source") or ""))
        if not source.is_file():
            errors.append(f"missing flow source: {source}")
            continue
        try:
            warnings = validate_flow(source)
            graph = expand_flow(source)
            graph_errors = validate_workflow_graph(graph)
            results.append(
                {
                    "id": item.get("id"),
                    "source": str(source),
                    "warnings": warnings,
                    "graph_errors": graph_errors,
                }
            )
            errors.extend(str(error) for error in graph_errors)
        except Exception as exc:
            errors.append(f"{source}: {exc}")
    return _check_result("flows", ok=not errors, results=results, errors=errors)


def _check_explain(ecosystem: dict[str, Any], registry: Path, repo: Path) -> dict[str, Any]:
    results: list[dict[str, Any]] = []
    errors: list[str] = []
    required = {"matched_registry", "backend", "runtime_transport", "verification", "policy"}
    for item in ecosystem.get("capabilities") or []:
        sample_uri = str(item.get("sample_uri") or "")
        if not sample_uri:
            continue
        try:
            payload = explain_uri(sample_uri, registry_root=registry, root=repo)
            missing = sorted(required - set(payload))
            results.append(
                {
                    "uri": sample_uri,
                    "matched_registry": payload.get("matched_registry"),
                    "runtime_transport": payload.get("runtime_transport"),
                    "missing": missing,
                }
            )
            if payload.get("matched_registry") != "touri":
                errors.append(f"{sample_uri}: expected touri match")
            if missing:
                errors.append(f"{sample_uri}: missing explain fields {missing}")
        except Exception as exc:
            errors.append(f"{sample_uri}: {exc}")
    return _check_result("explain", ok=not errors, results=results, errors=errors)


def _check_doctor(repo: Path, registry: Path) -> dict[str, Any]:
    try:
        payload = run_doctor(root=repo, registry=registry)
    except Exception as exc:
        return _check_result("doctor", ok=False, errors=[str(exc)])
    return _check_result(
        "doctor",
        ok=bool(payload.get("ok")),
        registry=str(registry),
        checks=[item.get("id") for item in payload.get("checks") or []],
        warnings=payload.get("warnings") or [],
    )

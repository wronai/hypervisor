from __future__ import annotations

from pathlib import Path
from typing import Any

from uri2flow.validator import validate_flow
from uri3.resolvers.explain import explain_uri

from urigen.io import load_yaml
from urigen.models import repo_root


def explain_ecosystem(
    ecosystem_path: str | Path,
    *,
    root: str | Path | None = None,
) -> dict[str, Any]:
    path = Path(ecosystem_path)
    base = path.parent
    repo = repo_root(root)
    ecosystem = load_yaml(path)
    registry = base / "capabilities"
    return {
        "ecosystem": ecosystem.get("ecosystem") or {},
        "domains": _domains(ecosystem, base),
        "agents": _agents(ecosystem, base),
        "capabilities": _capabilities(ecosystem, registry, repo),
        "flows": _flows(ecosystem, base),
        "deployments": _deployments(ecosystem),
        "risks": _risks(ecosystem),
    }


def _exists(base: Path, value: str) -> bool:
    path = Path(value)
    return (path if path.is_absolute() else base / path).exists()


def _domains(ecosystem: dict[str, Any], base: Path) -> list[dict[str, Any]]:
    return [
        {
            "id": item.get("id"),
            "source_present": _exists(base, str(item.get("source") or "")),
            "uri_tree_present": _exists(base, str(item.get("uri_tree") or "")),
        }
        for item in ecosystem.get("domains") or []
    ]


def _agents(ecosystem: dict[str, Any], base: Path) -> list[dict[str, Any]]:
    return [
        {
            "id": item.get("id"),
            "contract_present": _exists(base, str(item.get("contract") or "")),
            "deployment_refs": [
                dep.get("id")
                for dep in ecosystem.get("deployments") or []
                if dep.get("agent_ref") == item.get("ref")
            ],
        }
        for item in ecosystem.get("agents") or []
    ]


def _capabilities(ecosystem: dict[str, Any], registry: Path, repo: Path) -> list[dict[str, Any]]:
    results = []
    for item in ecosystem.get("capabilities") or []:
        sample_uri = str(item.get("sample_uri") or "")
        payload: dict[str, Any] = {}
        if sample_uri:
            payload = explain_uri(sample_uri, registry_root=registry, root=repo)
        results.append(
            {
                "id": item.get("id"),
                "sample_uri": sample_uri,
                "matched_registry": payload.get("matched_registry"),
                "backend": payload.get("backend"),
                "runtime_transport": payload.get("runtime_transport"),
                "policy": payload.get("policy"),
                "verification": payload.get("verification"),
            }
        )
    return results


def _flows(ecosystem: dict[str, Any], base: Path) -> list[dict[str, Any]]:
    results = []
    for item in ecosystem.get("flows") or []:
        source = str(item.get("source") or "")
        path = Path(source)
        resolved = path if path.is_absolute() else base / path
        try:
            warnings = validate_flow(resolved)
            ok = True
        except Exception as exc:
            warnings = [str(exc)]
            ok = False
        results.append({"id": item.get("id"), "source": source, "ok": ok, "warnings": warnings})
    return results


def _deployments(ecosystem: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        {
            "id": item.get("id"),
            "agent_ref": item.get("agent_ref"),
            "health_uri": item.get("health_uri"),
            "if_running": item.get("if_running", "reuse"),
            "status": "planned",
        }
        for item in ecosystem.get("deployments") or []
    ]


def _risks(ecosystem: dict[str, Any]) -> list[str]:
    risks: list[str] = []
    for item in ecosystem.get("capabilities") or []:
        if "data_quality" not in item:
            risks.append(f"{item.get('id')}: no ecosystem-level data_quality policy")
    if not ecosystem.get("tests"):
        risks.append("no tests declared")
    return risks

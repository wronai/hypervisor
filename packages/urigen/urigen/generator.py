from __future__ import annotations

from pathlib import Path
from typing import Any

from urigen.artifacts import (
    AGENT_CONTRACTS,
    APP_SOURCES,
    CAPABILITY_SAMPLE_URIS,
    CAPABILITY_SOURCES,
    DOMAIN_FILES,
    FLOW_SOURCES,
    repo_path,
)
from urigen.envelope import stamp_ecosystem
from urigen.io import copy_file, load_yaml, relative_to, write_text, write_yaml
from urigen.models import repo_root
from urigen.writer import (
    dashboard_deployment_fragment,
    deployment_fragment,
    render_readme,
    test_plan,
    voice_flow,
)

DEFAULT_DATA_QUALITY_POLICY = {
    "failure_code": "GENERATED_ECOSYSTEM_DATA_QUALITY_FAILED",
    "recoverable": True,
    "validators": [],
}


def generate_ecosystem(
    proposal_path: str | Path,
    *,
    out: str | Path,
    root: str | Path | None = None,
) -> dict[str, Any]:
    """Generate an isolated ecosystem artifact directory from a proposal."""
    repo = repo_root(root)
    proposal = load_yaml(proposal_path)
    proposal_meta = proposal.get("proposal") or {}
    intent = proposal.get("intent") or {}
    ecosystem_id = str(proposal_meta.get("id") or "generated-ecosystem")
    out_dir = Path(out)
    out_dir.mkdir(parents=True, exist_ok=True)

    files: list[str] = []
    embedded: dict[str, str] = {}
    capabilities = _copy_capabilities(intent, repo, out_dir, files, embedded)
    flows = _write_flows(intent, repo, out_dir, files, embedded)
    domains = _copy_domains(intent, repo, out_dir, files)
    agents = _copy_agents(intent, repo, out_dir, files)
    deployments = _write_deployments(intent, out_dir, files)
    applications = _copy_applications(intent, repo, out_dir, files)

    ecosystem = stamp_ecosystem(
        {
            "version": 1,
            "ecosystem": {
                "id": ecosystem_id,
                "description": (
                    f"Generated URI ecosystem for: {proposal_meta.get('source_prompt', '')}"
                ),
                "source_prompt": proposal_meta.get("source_prompt", ""),
                "profile": proposal_meta.get("profile", "minimal"),
            },
            "domains": domains,
            "agents": agents,
            "applications": applications,
            "capabilities": capabilities,
            "flows": flows,
            "deployments": deployments,
            "tests": [
                {"id": "capability-plan", "type": "urigen.capability_contract"},
                {"id": "explain-sample-uris", "type": "uri3.explain"},
                {"id": "workflow-dry-run", "type": "uri3.validate-workflow"},
                {"id": "doctor", "type": "uri3.doctor"},
            ],
            "publishing": {
                "markpact_readme": "README.md",
            },
        },
        lifecycle={"generated": True},
    )

    ecosystem_path = write_yaml(out_dir / "ecosystem.yaml", ecosystem)
    files.append(relative_to(ecosystem_path, out_dir))
    readme_path = write_text(out_dir / "README.md", render_readme(ecosystem, embedded))
    files.append(relative_to(readme_path, out_dir))
    plan_path = write_yaml(out_dir / "tests" / "test_plan.yaml", test_plan(ecosystem_id))
    files.append(relative_to(plan_path, out_dir))
    explain_path = write_yaml(
        out_dir / "tests" / "test_explain_uris.yaml",
        {"uris": [item["sample_uri"] for item in capabilities if item.get("sample_uri")]},
    )
    files.append(relative_to(explain_path, out_dir))
    dry_run_path = write_yaml(
        out_dir / "tests" / "test_workflow_dry_run.yaml",
        {"flows": [item["source"] for item in flows]},
    )
    files.append(relative_to(dry_run_path, out_dir))
    (out_dir / "generated" / "agents").mkdir(parents=True, exist_ok=True)

    return {
        "ok": True,
        "ecosystem": ecosystem_id,
        "directory": str(out_dir),
        "ecosystem_file": str(ecosystem_path),
        "files": sorted(files),
    }


def _copy_capabilities(
    intent: dict[str, Any],
    repo: Path,
    out_dir: Path,
    files: list[str],
    embedded: dict[str, str],
) -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    for capability_id in intent.get("capabilities") or []:
        source_rel = CAPABILITY_SOURCES.get(str(capability_id))
        if not source_rel:
            continue
        source = repo_path(repo, source_rel)
        target = out_dir / "capabilities" / source.name
        copy_file(source, target)
        manifest = load_yaml(target)
        manifest.setdefault("data_quality", dict(DEFAULT_DATA_QUALITY_POLICY))
        write_yaml(target, manifest)
        rel = relative_to(target, out_dir)
        files.append(rel)
        embedded[rel] = target.read_text(encoding="utf-8")
        entries.append(
            {
                "id": str(capability_id),
                "source": rel,
                "sample_uri": CAPABILITY_SAMPLE_URIS.get(str(capability_id), ""),
                "data_quality": dict(DEFAULT_DATA_QUALITY_POLICY),
            }
        )
    return entries


def _write_flows(
    intent: dict[str, Any],
    repo: Path,
    out_dir: Path,
    files: list[str],
    embedded: dict[str, str],
) -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    for flow_id in intent.get("flows") or []:
        flow_name = str(flow_id)
        if flow_name == "voice-command-health":
            target = write_yaml(
                out_dir / "flows" / "voice_command_health.uri.flow.yaml", voice_flow()
            )
        else:
            source_rel = FLOW_SOURCES.get(flow_name)
            if not source_rel:
                continue
            source = repo_path(repo, source_rel)
            target = copy_file(source, out_dir / "flows" / source.name)
        rel = relative_to(target, out_dir)
        files.append(rel)
        embedded[rel] = target.read_text(encoding="utf-8")
        entries.append(
            {
                "id": flow_name,
                "source": rel,
                "graph": f"generated/{flow_name}.uri.graph.yaml",
            }
        )
    return entries


def _copy_domains(
    intent: dict[str, Any],
    repo: Path,
    out_dir: Path,
    files: list[str],
) -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    for domain_id in intent.get("domains") or []:
        copied: list[str] = []
        for source_rel in DOMAIN_FILES.get(str(domain_id), []):
            source = repo_path(repo, source_rel)
            target = out_dir / "domains" / str(domain_id) / source.name
            copy_file(source, target)
            rel = relative_to(target, out_dir)
            files.append(rel)
            copied.append(rel)
        entries.append(
            {
                "id": str(domain_id),
                "source": copied[0] if copied else "",
                "uri_tree": next((item for item in copied if item.endswith("uri_tree.yaml")), ""),
            }
        )
    return entries


def _copy_agents(
    intent: dict[str, Any],
    repo: Path,
    out_dir: Path,
    files: list[str],
) -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    for agent_id in intent.get("agents") or []:
        source_rel = AGENT_CONTRACTS.get(str(agent_id))
        if not source_rel:
            continue
        source = repo_path(repo, source_rel)
        target = copy_file(source, out_dir / "contracts" / "agents" / source.name)
        rel = relative_to(target, out_dir)
        files.append(rel)
        entries.append(
            {
                "id": str(agent_id),
                "ref": f"agent://{agent_id}",
                "contract": rel,
                "generated_dir": f"generated/agents/{str(agent_id).replace('-', '_')}",
            }
        )
    return entries


def _copy_applications(
    intent: dict[str, Any],
    repo: Path,
    out_dir: Path,
    files: list[str],
) -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    for agent_id in intent.get("agents") or []:
        source_rel = APP_SOURCES.get(str(agent_id))
        if not source_rel:
            continue
        source = repo_path(repo, source_rel)
        target = out_dir / "app"
        copied = _copy_application_tree(source, target, out_dir, files)
        entries.append(
            {
                "id": f"{agent_id}.app",
                "agent_ref": f"agent://{agent_id}",
                "runtime": "fastapi",
                "source": relative_to(target, out_dir),
                "entrypoint": "hypervisor_dashboard_agent.main:app",
                "files": copied,
            }
        )
    return entries


def _copy_application_tree(
    source: Path,
    target: Path,
    out_dir: Path,
    files: list[str],
) -> list[str]:
    copied: list[str] = []
    for item in sorted(source.rglob("*")):
        rel = item.relative_to(source)
        if item.is_dir() or _skip_app_artifact(rel, item):
            continue
        destination = copy_file(item, target / rel)
        relative = relative_to(destination, out_dir)
        files.append(relative)
        copied.append(relative)
    return copied


def _skip_app_artifact(rel: Path, item: Path) -> bool:
    return (
        item.suffix == ".pyc"
        or any(part == "__pycache__" for part in rel.parts)
        or any(part.endswith(".egg-info") for part in rel.parts)
    )


def _write_deployments(
    intent: dict[str, Any],
    out_dir: Path,
    files: list[str],
) -> list[dict[str, Any]]:
    agents = [str(item) for item in intent.get("agents") or []]
    if "hypervisor-dashboard" in agents:
        fragment = dashboard_deployment_fragment()
        deployment_entries = [
            {
                "id": "hypervisor-dashboard.local",
                "agent_ref": "agent://hypervisor-dashboard",
                "target_uri": "local://packages/hypervisor-dashboard-agent",
                "health_uri": "http://localhost:8788/health",
                "if_running": "reuse",
            }
        ]
    else:
        fragment = deployment_fragment()
        deployment_entries = [
            {
                "id": "weather-map-agent.local",
                "agent_ref": "agent://weather-map-agent",
                "target_uri": "local://agents/generated/weather_map_agent",
                "health_uri": "http://localhost:8101/health",
                "if_running": "reuse",
            }
        ]
    path = write_yaml(out_dir / "deployments" / "agent_deployments.fragment.yaml", fragment)
    files.append(relative_to(path, out_dir))
    source = relative_to(path, out_dir)
    return [{**entry, "source": source} for entry in deployment_entries]

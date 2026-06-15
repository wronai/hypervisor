from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

from hypervisor.contract_registry.loader import load_contract_registry
from hypervisor.deployment_registry.loader import load_deployment_registry
from hypervisor.deployment_registry.local_targets import (
    build_local_run_plan,
    local_target_to_module,
    local_target_to_relative_path,
)
from hypervisor.deployment_registry.selector import resolve_deployment
from hypervisor.paths import find_repo_root


@dataclass
class AgentDescribeReport:
    selector: str
    markdown: str
    data: dict[str, Any] = field(default_factory=dict)

    def write(self, path: Path) -> Path:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(self.markdown, encoding="utf-8")
        return path


def describe_agent(
    selector: str,
    *,
    root: str | Path | None = None,
) -> AgentDescribeReport:
    repo = find_repo_root() if root is None else Path(root)
    deployment = resolve_deployment(selector, root=repo, prefer_local=True)
    agent_name = deployment.agent_ref.removeprefix("agent://")
    contract_path = _find_contract_path(repo, agent_name, deployment)
    contract = _read_yaml(contract_path) if contract_path else {}
    is_operator = contract.get("kind") == "hypervisor.operator_agent"
    agent_meta = contract.get("metadata") if is_operator else (contract.get("agent") or {})
    if not agent_meta and not is_operator:
        agent_meta = contract.get("agent") or {}
    package_rel = _package_relative_path(deployment, repo)
    package_dir = repo / package_rel if package_rel else None
    agent_kind = _agent_kind(deployment, is_operator=is_operator)
    generated_meta = _read_yaml(package_dir / ".generated.yaml") if package_dir else {}
    domain_pack = _find_domain_pack(repo, contract_path, deployment, contract)
    markpact_blocks = _extract_markpact_blocks(package_dir / "README.md") if package_dir else []
    files = (
        _list_package_files(package_dir, agent_kind=agent_kind)
        if package_dir and package_dir.is_dir()
        else []
    )
    registry = load_contract_registry(repo)
    agent_caps = [cap for cap in registry.capabilities if cap.agent == agent_name]
    all_deployments = load_deployment_registry(repo).by_agent_ref(deployment.agent_ref)
    run_plan = _safe_run_plan(deployment, repo)
    data = {
        "selector": selector,
        "deployment_id": deployment.id,
        "agent_ref": deployment.agent_ref,
        "agent_name": agent_name,
        "contract_path": _rel(repo, contract_path),
        "contract_format": "operator_yaml" if is_operator else "yaml",
        "markpact_in_readme": bool(markpact_blocks),
        "package_path": _rel(repo, package_dir),
        "domain_pack": domain_pack,
        "files": files,
        "is_operator": is_operator,
        "agent_kind": agent_kind,
        "deployments": [item.id for item in all_deployments],
    }
    markdown = _render_markdown(
        repo=repo,
        selector=selector,
        deployment=deployment,
        agent_name=agent_name,
        agent_meta=agent_meta,
        contract_path=contract_path,
        contract=contract,
        is_operator=is_operator,
        generated_meta=generated_meta,
        domain_pack=domain_pack,
        markpact_blocks=markpact_blocks,
        files=files,
        agent_caps=agent_caps,
        all_deployments=all_deployments,
        run_plan=run_plan,
        registry=registry,
    )
    return AgentDescribeReport(selector=selector, markdown=markdown, data=data)


def _deployment_health_label(deployment_item: Any) -> str:
    declared = deployment_item.declared
    for candidate in (
        deployment_item.health_uri,
        declared.health_uri if declared else None,
    ):
        if isinstance(candidate, str) and candidate:
            return candidate
    if str(deployment_item.target_uri).startswith("local://"):
        from hypervisor.deployment_registry.status import infer_port

        port = infer_port(deployment_item)
        return f"http://localhost:{port}/health"
    return "—"


def _safe_run_plan(deployment: Any, repo: Path) -> dict[str, Any] | None:
    if not str(deployment.target_uri).startswith("local://"):
        return None
    try:
        return build_local_run_plan(deployment, repo=repo)
    except (FileNotFoundError, ValueError):
        return None


def _find_contract_path(repo: Path, agent_name: str, deployment: Any) -> Path | None:
    metadata = deployment.metadata or {}
    contract_rel = metadata.get("contract")
    if contract_rel:
        path = repo / contract_rel
        if path.is_file():
            return path
    slug = agent_name.replace("-", "_")
    candidate = repo / "contracts" / "agents" / f"{slug}.yaml"
    if candidate.is_file():
        return candidate
    domain_id = (deployment.metadata or {}).get("domain_id")
    if domain_id:
        fragment = repo / "domains" / domain_id.replace("-", "_") / "registry.fragment.yaml"
        if fragment.is_file():
            raw = _read_yaml(fragment)
            rel = raw.get("agent_contract")
            if rel:
                path = repo / rel
                if path.is_file():
                    return path
    for path in sorted((repo / "contracts" / "agents").glob("*.yaml")):
        raw = _read_yaml(path)
        if (raw.get("agent") or {}).get("name") == agent_name:
            return path
    return None


def _find_domain_pack(
    repo: Path,
    contract_path: Path | None,
    deployment: Any | None = None,
    contract: dict[str, Any] | None = None,
) -> dict[str, Any] | None:
    metadata = (deployment.metadata or {}) if deployment is not None else {}
    domain_rel = metadata.get("domain_pack")
    if not domain_rel and contract:
        contracts_block = contract.get("contracts") or {}
        domain_rel = contracts_block.get("domain_pack")
    if domain_rel:
        domain_path = repo / domain_rel
        if domain_path.is_file():
            domain_dir = domain_path.parent
            return {
                "id": domain_dir.name,
                "path": _rel(repo, domain_dir),
                "domain_yaml": _rel(repo, domain_path),
                "registry_fragment": _rel(repo, domain_dir / "registry.fragment.yaml"),
                "uri_tree": _rel(repo, domain_dir / "uri_tree.yaml"),
                "commands": _rel(repo, domain_dir / "commands.yaml"),
                "resources": _rel(repo, domain_dir / "resources.yaml"),
                "views": _rel(repo, domain_dir / "views.yaml"),
                "operator_registry": _rel(repo, domain_dir / "operator_registry.yaml"),
                "scenario_registry": _rel(repo, domain_dir / "scenario_registry.yaml"),
            }
    if contract_path is None:
        return None
    contract_rel = _rel(repo, contract_path)
    for fragment_path in sorted((repo / "domains").glob("*/registry.fragment.yaml")):
        raw = _read_yaml(fragment_path)
        if raw.get("agent_contract") == contract_rel:
            domain_dir = fragment_path.parent
            return {
                "id": domain_dir.name,
                "path": _rel(repo, domain_dir),
                "registry_fragment": _rel(repo, fragment_path),
                "uri_tree": _rel(repo, domain_dir / "uri_tree.yaml"),
                "commands": _rel(repo, domain_dir / "commands.yaml"),
                "resources": _rel(repo, domain_dir / "resources.yaml"),
                "views": _rel(repo, domain_dir / "views.yaml"),
            }
    return None


def _package_relative_path(deployment: Any, repo: Path) -> Path | None:
    if not str(deployment.target_uri).startswith("local://"):
        return None
    try:
        return local_target_to_relative_path(deployment.target_uri)
    except ValueError:
        return None


def _list_package_files(package_dir: Path, *, agent_kind: str) -> list[dict[str, str]]:
    skip = {"__pycache__", ".pytest_cache", ".mypy_cache", ".egg-info"}
    items: list[dict[str, str]] = []
    for path in sorted(package_dir.rglob("*")):
        if not path.is_file():
            continue
        if any(part in skip or part.endswith(".egg-info") for part in path.parts):
            continue
        rel = path.relative_to(package_dir).as_posix()
        role = _file_role(rel, agent_kind=agent_kind)
        items.append({"path": rel, "role": role})
    return items


def _agent_kind(deployment: Any, *, is_operator: bool) -> str:
    if is_operator:
        return "operator"
    if str(deployment.target_uri).startswith("local://agents/custom/"):
        return "custom"
    metadata = deployment.metadata or {}
    if metadata.get("source") == "system_agent" or str(deployment.target_uri).startswith("local://packages/"):
        return "system"
    return "generated"


def _capability_backing_note(*, agent_kind: str) -> str:
    if agent_kind == "system":
        return "served natively by the system agent"
    if agent_kind == "custom":
        return "served by the hand-written custom agent"
    if agent_kind == "operator":
        return "executed by uri2ops adapters"
    return "via Resource Runtime"


def _skill_invoke_example(cap: dict[str, Any], *, deployment: Any) -> str:
    name = cap.get("name", "skill")
    uri = str(cap.get("uri") or "")
    if cap.get("type") == "command":
        command = cap.get("command") or "Command"
        return f"POST /skills/{name} with {command} payload"
    if "{place}" in uri and "{days}" in uri:
        return f"GET /skills/{name}?place=Gdansk&days=7"
    if "{agent_id}" in uri:
        return f"GET /skills/{name}?agent_id={deployment.id}"
    if "{invoice_id}" in uri:
        return f"GET /skills/{name}?invoice_id=demo-1"
    if "{user_id}" in uri:
        return f"GET /skills/{name}?user_id=demo"
    if "{workflow_id}" in uri:
        return f"GET /skills/{name}?workflow_id=demo-workflow"
    if "{incident_id}" in uri:
        return f"GET /skills/{name}?incident_id=demo-incident"
    return f"GET /skills/{name}?uri={uri or '...'}"


def _file_role(rel: str, *, agent_kind: str) -> str:
    if agent_kind == "custom":
        custom_roles = {
            "main.py": "FastAPI entrypoint (uvicorn target)",
            "routes.py": "HTTP routes: health, card, skills",
            "agent_card.py": "Agent Card payload (hand-maintained from contract)",
            "analysis.py": "Business logic and agent-to-agent orchestration",
            "__init__.py": "Package marker",
        }
        if rel in custom_roles:
            return custom_roles[rel]
        if rel.endswith(".py"):
            return "Hand-written Python module"
        return "Hand-written package file"

    roles = {
        "main.py": "FastAPI entrypoint (uvicorn target)",
        "routes.py": "HTTP routes: health, card, skills, resource proxy",
        "agent_card.py": "Agent Card payload (generated from contract)",
        "README.md": "Human docs + Markpact provenance blocks",
        ".generated.yaml": "Generator metadata (source contract, hash)",
        "Dockerfile": "Container image for deployment",
        "tests/test_contract.py": "Contract conformance tests",
    }
    return roles.get(rel, "generated artifact")


def _extract_markpact_blocks(readme_path: Path) -> list[dict[str, str]]:
    if not readme_path.is_file():
        return []
    text = readme_path.read_text(encoding="utf-8")
    pattern = re.compile(r"```markpact(?::([^\n]+))?\n(.*?)```", re.S)
    blocks: list[dict[str, str]] = []
    for match in pattern.finditer(text):
        blocks.append({"label": (match.group(1) or "block").strip(), "body": match.group(2).strip()})
    return blocks


def _read_yaml(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    return raw if isinstance(raw, dict) else {}


def _rel(repo: Path, path: Path | None) -> str | None:
    if path is None:
        return None
    try:
        return path.relative_to(repo).as_posix()
    except ValueError:
        return str(path)


def _render_markdown(
    *,
    repo: Path,
    selector: str,
    deployment: Any,
    agent_name: str,
    agent_meta: dict[str, Any],
    contract_path: Path | None,
    contract: dict[str, Any],
    is_operator: bool = False,
    generated_meta: dict[str, Any],
    domain_pack: dict[str, Any] | None,
    markpact_blocks: list[dict[str, str]],
    files: list[dict[str, str]],
    agent_caps: list[Any],
    all_deployments: list[Any],
    run_plan: dict[str, Any] | None,
    registry: Any,
) -> str:
    agent_kind = _agent_kind(deployment, is_operator=is_operator)
    backing_note = _capability_backing_note(agent_kind=agent_kind)
    package_label = {
        "operator": "Operator runtime package",
        "system": "System agent package",
        "custom": "Custom agent package",
        "generated": "Generated package",
    }[agent_kind]
    lines: list[str] = [
        f"# Agent report: `{agent_name}`",
        "",
        f"Selector: `{selector}` · deployment: `{deployment.id}` · agent ref: `{deployment.agent_ref}`",
        "",
        "## Contract",
        "",
    ]
    if is_operator:
        lines.extend(
            [
                "Primary contract format is **operator YAML** under `agents/operators/*.yaml` "
                "(`kind: hypervisor.operator_agent`).",
                "",
            ]
        )
    else:
        if agent_kind == "custom":
            lines.extend(
                [
                    "Primary contract format is **YAML** under `contracts/agents/*.yaml` "
                    "(resource-agent-factory schema).",
                    "Custom packages under `agents/custom/*` are **hand-written** and are not "
                    "regenerated by `resource-agent-factory` (no Markpact README blocks).",
                    "",
                ]
            )
        else:
            lines.extend(
                [
                    "Primary contract format is **YAML** under `contracts/agents/*.yaml` "
                    "(resource-agent-factory schema).",
                    "Generated packages embed **Markpact** provenance blocks in `README.md` "
                    "(not the source contract file).",
                    "",
                ]
            )
    if contract_path:
        if is_operator:
            lines.extend(
                [
                    f"- **Contract file:** `{_rel(repo, contract_path)}`",
                    f"- **Kind:** `{contract.get('kind', '—')}`",
                    f"- **Title:** {agent_meta.get('title', '—')}",
                    f"- **Description:** {agent_meta.get('description', '—')}",
                    f"- **Runtime package:** `{agent_meta.get('runtime_package', '—')}`",
                ]
            )
            runtime = contract.get("runtime") or {}
            if runtime.get("health_uri"):
                lines.append(f"- **Health URI:** `{runtime['health_uri']}`")
        else:
            lines.extend(
                [
                    f"- **Contract file:** `{_rel(repo, contract_path)}`",
                    f"- **Version:** `{agent_meta.get('version', '—')}`",
                    f"- **Python package:** `{agent_meta.get('python_package', '—')}`",
                    f"- **Description:** {agent_meta.get('description', '—')}",
                ]
            )
            if agent_kind == "custom":
                lines.append(
                    "- **Implementation:** hand-written FastAPI routes "
                    "(capabilities served directly, no Resource Runtime proxy)"
                )
            else:
                lines.append(
                    f"- **Runtime env:** `{agent_meta.get('runtime_url_env', 'RESOURCE_RUNTIME_URL')}` "
                    f"→ `{agent_meta.get('runtime_url_default', 'http://localhost:8000')}`"
                )
            if agent_kind == "generated" and generated_meta.get("contract_hash"):
                lines.append(f"- **Contract hash:** `{generated_meta['contract_hash']}`")
            if agent_kind == "generated" and generated_meta.get("generator"):
                lines.append(f"- **Generator:** `{generated_meta['generator']}`")
    else:
        lines.append("- _No contract YAML found for this agent._")

    lines.extend(["", "## Capabilities (contract)", ""])
    if is_operator:
        op_caps = contract.get("capabilities") or []
        if op_caps:
            lines.append("| Scheme | Operations | Adapters |")
            lines.append("|--------|------------|----------|")
            for cap in op_caps:
                ops = ", ".join(cap.get("operations") or [])
                adapters = ", ".join(cap.get("adapters") or [])
                lines.append(f"| `{cap.get('scheme', '—')}` | {ops or '—'} | {adapters or '—'} |")
        else:
            lines.append("_No operator capabilities in contract._")
    else:
        caps = contract.get("capabilities") or []
        if caps:
            lines.append("| Name | Type | URI / command | Schema | Renderer |")
            lines.append("|------|------|---------------|--------|----------|")
            for cap in caps:
                uri_or_cmd = cap.get("uri") or cap.get("command") or "—"
                lines.append(
                    f"| `{cap.get('name', '—')}` | `{cap.get('type', '—')}` | `{uri_or_cmd}` | "
                    f"`{cap.get('output_schema') or cap.get('input_schema') or '—'}` | `{cap.get('renderer') or '—'}` |"
                )
        else:
            lines.append("_No capabilities in contract._")

    if domain_pack:
        lines.extend(
            [
                "",
                "## Domain pack",
                "",
                f"- **Domain id:** `{domain_pack['id']}`",
                f"- **Path:** `{domain_pack['path']}/`",
                f"- **URI tree:** `{domain_pack.get('uri_tree') or '—'}`",
                f"- **Commands:** `{domain_pack.get('commands') or '—'}`",
                f"- **Resources:** `{domain_pack.get('resources') or '—'}`",
                f"- **Views:** `{domain_pack.get('views') or '—'}`",
            ]
        )
        if domain_pack.get("operator_registry"):
            lines.append(f"- **Operator registry:** `{domain_pack['operator_registry']}`")
        if domain_pack.get("scenario_registry"):
            lines.append(f"- **Scenario registry:** `{domain_pack['scenario_registry']}`")
        commands_path = domain_pack.get("commands")
        if commands_path:
            commands = _read_yaml(repo / commands_path)
            for item in commands.get("commands") or []:
                if isinstance(item, dict):
                    lines.append(
                        f"- Command `{item.get('name')}` → handler `{item.get('handler_uri')}`"
                    )

    lines.extend(["", f"## {package_label}", ""])
    if str(deployment.target_uri).startswith("local://"):
        try:
            rel = local_target_to_relative_path(deployment.target_uri)
            lines.extend(
                [
                    f"- **Path:** `{rel.as_posix()}/`",
                    f"- **Uvicorn module:** `{local_target_to_module(deployment.target_uri)}`",
                ]
            )
        except ValueError:
            lines.append(f"- **Target:** `{deployment.target_uri}`")
    else:
        lines.append(f"- **Target:** `{deployment.target_uri}`")

    if files:
        lines.extend(["", "| File | Role |", "|------|------|"])
        for item in files:
            lines.append(f"| `{item['path']}` | {item['role']} |")

    lines.extend(["", "## Deployments (registry)", ""])
    if all_deployments:
        lines.append("| Deployment id | Target | Health | Status |")
        lines.append("|---------------|--------|--------|--------|")
        for item in all_deployments:
            lines.append(
                f"| `{item.id}` | `{item.target_uri}` | `{_deployment_health_label(item)}` | `{item.status}` |"
            )
    else:
        lines.append(f"- `{deployment.id}` only")

    lines.extend(["", "## How it is invoked", ""])
    lines.extend(
        [
            "### Lifecycle (hypervisor)",
            "",
            "```bash",
            f"hypervisor run-agent {deployment.id} --detach --wait-healthy",
            f"hypervisor inspect-agent {deployment.id}",
            f"hypervisor describe-agent {deployment.id} -o output/reports/{deployment.id}.md",
            f"hypervisor stop-agent {deployment.id}",
            "```",
            "",
            "### System URIs (dashboard / chat)",
            "",
            "```bash",
            f"uri call view://process/agent/{deployment.id}/latest",
            f"uri call html://process/agent/{deployment.id}/latest",
            f"uri call repair://agent/{deployment.id}/diagnose",
            f"uri call health://agent/{deployment.id}",
            "```",
            "",
        ]
    )

    resource_caps = contract.get("capabilities") or []

    if run_plan and not is_operator:
        http_label = {
            "system": "HTTP (system agent)",
            "custom": "HTTP (custom agent)",
            "generated": "HTTP (generated agent)",
        }[agent_kind]
        proxy_endpoints = agent_kind == "generated"
        lines.extend(
            [
                f"### {http_label}",
                "",
                "```bash",
                " ".join(run_plan.get("command") or []),
                "```",
                "",
                "| Endpoint | Purpose |",
                "|----------|---------|",
                f"| `GET {run_plan.get('health_uri')}` | health |",
                f"| `GET {run_plan.get('card_uri')}` | agent card |",
                "| `GET /capabilities` | capability list |",
            ]
        )
        if proxy_endpoints:
            lines.extend(
                [
                    "| `GET /resources/read?uri=...` | proxy to Resource Runtime |",
                    "| `POST /commands` | dispatch command to Resource Runtime |",
                ]
            )
        lines.extend(
            [
                "",
                "### Skills (agent surface)",
                "",
            ]
        )
        for cap in resource_caps:
            if not isinstance(cap, dict):
                continue
            name = cap.get("name")
            invoke = _skill_invoke_example(cap, deployment=deployment)
            detail = cap.get("uri") or cap.get("command") or "—"
            lines.append(f"- `{name}` → `{invoke}` (backs `{detail}`, {backing_note})")
    elif is_operator:
        runtime = contract.get("runtime") or {}
        lines.extend(
            [
                "### HTTP (operator runtime)",
                "",
                f"- **Command:** `{runtime.get('command', '—')}`",
                f"- **A2A tasks:** `{runtime.get('a2a_tasks_uri', '—')}`",
                f"- **MCP tools:** `{runtime.get('mcp_tools_uri', '—')}`",
                "",
            ]
        )

    lines.extend(["", "## Architecture chain", ""])
    if is_operator:
        lines.extend(
            [
                "```mermaid",
                "flowchart LR",
                "  O[agents/operators/*.yaml]",
                "  U[uri2ops package]",
                "  D[domains/*/operator_registry]",
                "  O --> U --> D",
                "```",
                "",
                "- **Operator contract** defines schemes, operations, adapters and policy.",
                "- **uri2ops** executes browser/screen/input operations via selected adapter.",
                "- **Domain registries** hold vertical scenarios; operator stays domain-agnostic.",
            ]
        )
    elif agent_kind == "system":
        lines.extend(
            [
                "```mermaid",
                "flowchart LR",
                "  C[contracts/agents/*.yaml]",
                "  P[packages/* system agent]",
                "  H[hypervisor + uri call surface]",
                "  C --> P --> H",
                "```",
                "",
                "- **System agent** lives under `packages/*`, not `agents/generated/*`.",
                "- **Contract YAML** defines observer/controller capabilities.",
                "- **Dashboard/chat** invoke the agent through health, card, and URI views.",
            ]
        )
    elif agent_kind == "custom":
        lines.extend(
            [
                "```mermaid",
                "flowchart LR",
                "  C[contracts/agents/*.yaml]",
                "  A[agents/custom/* FastAPI]",
                "  H[hypervisor + uri call surface]",
                "  C --> A --> H",
                "```",
                "",
                "- **Custom agent** lives under `agents/custom/*` (generator-safe).",
                "- **Contract YAML** defines capabilities and runtime defaults.",
                "- **Hand-written routes** implement skills and agent-to-agent flows.",
            ]
        )
    else:
        lines.extend(
            [
                "```mermaid",
                "flowchart LR",
                "  C[contracts/agents/*.yaml]",
                "  G[resource-agent-factory generator]",
                "  A[agents/generated/* FastAPI]",
                "  R[Resource Runtime :8000]",
                "  D[domains/*/handlers]",
                "  C --> G --> A",
                "  A -->|read_resource / commands| R",
                "  R --> D",
                "```",
                "",
                "- **Contract YAML** defines capabilities and runtime defaults.",
                "- **Generator** emits `main.py`, `routes.py`, `agent_card.py`, `README.md` (+ Markpact blocks).",
                "- **Thin agent** exposes health/card/skills and forwards business calls to Resource Runtime.",
                "- **Domain handlers** (`python://domains.*.handlers.*`) implement commands when runtime is up.",
            ]
        )

    if markpact_blocks:
        lines.extend(["", "## Markpact blocks (from README)", ""])
        for block in markpact_blocks:
            lines.extend([f"### `{block['label']}`", "", "```yaml", block["body"], "```", ""])

    related_resources = [
        res for res in registry.resources if res.owner_agent == agent_name or agent_name.split("-")[0] in res.uri
    ]
    if related_resources:
        lines.extend(["", "## Related resources (contract registry)", ""])
        for res in related_resources[:12]:
            lines.append(f"- `{res.uri}` → projection `{res.projection}`, renderer `{res.renderer}`")

    if agent_caps:
        lines.extend(["", "## Registry index", ""])
        for cap in agent_caps:
            detail = cap.uri or cap.command or "—"
            lines.append(f"- `{cap.name}` ({cap.type}): `{detail}`")

    lines.append("")
    return "\n".join(lines)

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Literal

import yaml

CapabilityType = Literal["resource_read", "command"]


@dataclass(frozen=True)
class Capability:
    name: str
    type: CapabilityType
    description: str = ""
    uri: str | None = None
    output_schema: str | None = None
    renderer: str | None = None
    command: str | None = None
    input_schema: str | None = None
    emits: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class AgentSpec:
    source_path: Path
    name: str
    python_package: str
    version: str
    description: str
    runtime_url_env: str
    runtime_url_default: str
    capabilities: list[Capability]

    @property
    def output_dir_name(self) -> str:
        return self.python_package


def load_agent_spec(path: str | Path) -> AgentSpec:
    source_path = Path(path)
    raw = yaml.safe_load(source_path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError(f"{source_path} must contain a YAML mapping")

    agent = raw.get("agent") or {}
    capabilities_raw = raw.get("capabilities") or []

    capabilities: list[Capability] = []
    for item in capabilities_raw:
        capabilities.append(
            Capability(
                name=item["name"],
                type=item["type"],
                description=item.get("description", ""),
                uri=item.get("uri"),
                output_schema=item.get("output_schema"),
                renderer=item.get("renderer"),
                command=item.get("command"),
                input_schema=item.get("input_schema"),
                emits=item.get("emits", []) or [],
            )
        )

    return AgentSpec(
        source_path=source_path,
        name=agent["name"],
        python_package=agent.get("python_package") or agent["name"].replace("-", "_"),
        version=str(agent.get("version", "0.1.0")),
        description=agent.get("description", ""),
        runtime_url_env=agent.get("runtime_url_env", "RESOURCE_RUNTIME_URL"),
        runtime_url_default=agent.get("runtime_url_default", "http://localhost:8000"),
        capabilities=capabilities,
    )


def spec_to_plain_dict(
    spec: AgentSpec,
    contract_hash: str,
    *,
    source_ref: str | None = None,
) -> dict[str, Any]:
    contract = source_ref or str(spec.source_path)
    return {
        "name": spec.name,
        "version": spec.version,
        "description": spec.description,
        "generated_from": {
            "contract": contract,
            "contract_hash": contract_hash,
        },
        "capabilities": [cap.__dict__ for cap in spec.capabilities],
    }

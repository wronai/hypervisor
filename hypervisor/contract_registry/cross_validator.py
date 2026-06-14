from __future__ import annotations

from pathlib import Path
import re

from hypervisor.contract_registry.loader import load_contract_registry
from hypervisor.contract_registry.models import ContractRegistry


def _load_proto_text(root: Path) -> str:
    parts: list[str] = []
    for path in sorted((root / "contracts" / "proto").glob("*.proto")):
        parts.append(path.read_text(encoding="utf-8"))
    return "\n".join(parts)


def _schema_exists(proto_text: str, schema_ref: str) -> bool:
    # schema_ref like app.users.v1.UserView; check final message name in proto files.
    name = schema_ref.split(".")[-1]
    return re.search(rf"\bmessage\s+{re.escape(name)}\b", proto_text) is not None


def validate_cross_references(registry: ContractRegistry) -> list[str]:
    errors: list[str] = []
    view_names = {v.name for v in registry.views}
    renderer_names = {v.viewKind for v in registry.views} | {"detail", "table", "timeline", "chart"}
    resource_uris = {r.uri for r in registry.resources}
    resource_schemas = {r.schema for r in registry.resources}
    proto_text = _load_proto_text(registry.root)

    for resource in registry.resources:
        if resource.projection not in view_names:
            errors.append(f"resource {resource.uri} references missing projection/view {resource.projection}")
        if resource.renderer not in renderer_names:
            errors.append(f"resource {resource.uri} references unknown renderer {resource.renderer}")
        if proto_text and not _schema_exists(proto_text, resource.schema):
            errors.append(f"resource {resource.uri} references missing proto schema {resource.schema}")

    for capability in registry.capabilities:
        if capability.type == "resource_read":
            if not capability.uri:
                errors.append(f"capability {capability.agent}.{capability.name} lacks uri")
            elif capability.uri not in resource_uris:
                errors.append(f"capability {capability.agent}.{capability.name} references missing resource {capability.uri}")
            if capability.output_schema and capability.output_schema not in resource_schemas:
                errors.append(f"capability {capability.agent}.{capability.name} output_schema does not match any resource schema: {capability.output_schema}")
        if capability.renderer and capability.renderer not in renderer_names:
            errors.append(f"capability {capability.agent}.{capability.name} references unknown renderer {capability.renderer}")
        for schema_ref in [capability.input_schema, capability.output_schema]:
            if schema_ref and proto_text and not _schema_exists(proto_text, schema_ref):
                errors.append(f"capability {capability.agent}.{capability.name} references missing proto schema {schema_ref}")
    return errors


def validate_root(root: str | Path = ".") -> list[str]:
    return validate_cross_references(load_contract_registry(root))

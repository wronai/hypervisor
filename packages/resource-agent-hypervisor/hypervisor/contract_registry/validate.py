from __future__ import annotations

from hypervisor.contract_registry.models import ContractRegistry


def validate_registry(registry: ContractRegistry) -> list[str]:
    errors: list[str] = []

    resource_uris = set()
    for res in registry.resources:
        if res.uri in resource_uris:
            errors.append(f"duplicate resource uri: {res.uri}")
        resource_uris.add(res.uri)
        if not res.uri.startswith("resource://"):
            errors.append(f"resource uri must start with resource://: {res.uri}")
        if "postgres" in res.uri or "_view" in res.uri.split("/")[2:]:
            errors.append(f"resource uri should be semantic, not storage-oriented: {res.uri}")
        if not registry.view_by_name(res.projection):
            errors.append(f"resource {res.uri} references missing view/projection {res.projection}")

    view_names = {view.name for view in registry.views}
    if len(view_names) != len(registry.views):
        errors.append("duplicate view names detected")

    for cap in registry.capabilities:
        if cap.type == "resource_read":
            if not cap.uri:
                errors.append(f"{cap.agent}.{cap.name}: resource_read requires uri")
                continue
            resource = registry.resource_by_uri(cap.uri)
            if not resource:
                errors.append(f"{cap.agent}.{cap.name}: references unknown uri {cap.uri}")
                continue
            if cap.output_schema and cap.output_schema != resource.schema:
                errors.append(
                    f"{cap.agent}.{cap.name}: output_schema {cap.output_schema} != resource schema {resource.schema}"
                )
            if cap.renderer and cap.renderer != resource.renderer:
                errors.append(
                    f"{cap.agent}.{cap.name}: renderer {cap.renderer} != resource renderer {resource.renderer}"
                )
        elif cap.type == "command":
            if not cap.command:
                errors.append(f"{cap.agent}.{cap.name}: command capability requires command")
            if not cap.input_schema:
                errors.append(f"{cap.agent}.{cap.name}: command capability requires input_schema")
        else:
            errors.append(f"{cap.agent}.{cap.name}: unsupported capability type {cap.type}")

    return errors

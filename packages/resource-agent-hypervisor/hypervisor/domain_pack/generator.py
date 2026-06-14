from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from hypervisor.contract_registry.merger import merge_main_contracts
from hypervisor.domain_pack import templates
from hypervisor.domain_pack.writer import repo_root, write_file


@dataclass
class DomainModel:
    tree: dict[str, Any]
    domain_id: str
    domain: dict[str, Any]
    agent: dict[str, Any]
    out_dir: Path

    @classmethod
    def from_uri_tree(cls, tree: dict[str, Any], out_dir: Path) -> DomainModel:
        domain = tree["domain"]
        return cls(
            tree=tree,
            domain_id=domain["id"],
            domain=domain,
            agent=tree["agent"],
            out_dir=out_dir,
        )


def parse_uri_tree(uri_tree_path: str | Path) -> dict[str, Any]:
    path = Path(uri_tree_path)
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def derive_domain_model(tree: dict[str, Any], out_dir: Path) -> DomainModel:
    return DomainModel.from_uri_tree(tree, Path(out_dir))


def generate_proto(model: DomainModel) -> str:
    if model.domain_id == "weather_map":
        return templates.weather_proto()
    return templates.generic_proto(model.domain_id)


def generate_resources(model: DomainModel) -> dict[str, Any]:
    resources: dict[str, Any] = {"resources": []}
    for key, resource in model.tree.get("resources", {}).items():
        resources["resources"].append(
            {
                "id": f"{model.domain_id}.{key}.v1",
                "kind": "resource",
                "uri_template": resource["uri_template"],
                "stability": "experimental",
                "version": "v1",
                "schema_ref": resource["schema_ref"],
                "projection_ref": f"{model.domain_id}_{key}_view",
                "renderer_ref": resource.get("renderer_ref", "json"),
                "owner_agent": model.agent["id"],
                "read_method": "resources/read",
                "mime_type": resource.get("mime_type", "application/json"),
            }
        )
    return resources


def generate_views(resources: dict[str, Any]) -> dict[str, Any]:
    views: dict[str, Any] = {"views": []}
    for resource in resources["resources"]:
        views["views"].append(
            {
                "name": resource["projection_ref"],
                "schema_ref": resource["schema_ref"],
                "renderer": resource["renderer_ref"],
                "mime_type": resource["mime_type"],
                "rebuildable": True,
            }
        )
    return views


def generate_commands(model: DomainModel) -> dict[str, Any]:
    commands: dict[str, Any] = {"commands": []}
    for _, command in model.tree.get("commands", {}).items():
        commands["commands"].append(
            {
                "name": command["name"],
                "uri": command["uri"],
                "handler_uri": command.get("handler_uri"),
                "input_schema_ref": command.get("input_schema_ref"),
                "emits": command.get("emits", []),
            }
        )
    return commands


def generate_renderers(model: DomainModel) -> dict[str, Any]:
    renderers: dict[str, Any] = {
        "renderers": [{"id": "json", "view_kind": "json", "allowed_mime_types": ["application/json"]}]
    }
    if any(resource.get("renderer_ref") == "html" for resource in model.tree.get("resources", {}).values()):
        renderers["renderers"].append(
            {"id": "html", "view_kind": "html", "allowed_mime_types": ["text/html", "application/json"]}
        )
    return renderers


def generate_handlers(model: DomainModel) -> tuple[str, str]:
    handler_name = "generate_weather_map.py" if model.domain_id == "weather_map" else "run.py"
    handler_source = (
        templates.weather_handler() if model.domain_id == "weather_map" else templates.generic_handler()
    )
    return handler_name, handler_source


def generate_agent_contract(model: DomainModel) -> dict[str, Any]:
    if model.domain_id == "weather_map":
        capabilities = [
            {
                "name": "read_weather_map",
                "type": "resource_read",
                "description": "Read generated weather map HTML view for a location and forecast horizon.",
                "uri": "resource://weather/maps/{place}/forecast/{days}",
                "output_schema": "app.weather.v1.WeatherMapHtmlView",
                "renderer": "html",
            },
            {
                "name": "generate_weather_map",
                "type": "command",
                "description": "Generate a weather map forecast HTML view for a location.",
                "command": "GenerateWeatherMap",
                "input_schema": "app.weather.v1.GenerateWeatherMapCommand",
                "emits": ["WeatherMapGenerationRequested", "WeatherMapGenerated"],
            },
        ]
    else:
        capabilities = [
            {
                "name": "run",
                "type": "command",
                "command": "RunTask",
                "input_schema": f"{templates.package_name(model.domain_id)}.RunTaskCommand",
                "emits": ["TaskRequested", "TaskCompleted"],
            }
        ]

    return {
        "agent": {
            "name": model.agent["id"],
            "python_package": model.agent["id"].replace("-", "_"),
            "version": "0.1.0",
            "description": model.domain.get("description", "Generated thin agent"),
            "runtime_url_env": "RESOURCE_RUNTIME_URL",
            "runtime_url_default": "http://localhost:8000",
        },
        "capabilities": capabilities,
    }


def write_domain_pack(
    model: DomainModel,
    *,
    proto_text: str,
    resources: dict[str, Any],
    views: dict[str, Any],
    commands: dict[str, Any],
    renderers: dict[str, Any],
    handler_name: str,
    handler_source: str,
    agent_yaml: dict[str, Any],
    root: Path | None = None,
) -> dict[str, str]:
    project_root = root or repo_root()
    out_dir = model.out_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    files: dict[str, str] = {}

    files["uri_tree"] = write_file(
        out_dir / "uri_tree.yaml",
        yaml.safe_dump(model.tree, sort_keys=False, allow_unicode=True),
    )
    files["domain"] = write_file(
        out_dir / "domain.yaml",
        yaml.safe_dump(
            {"domain": model.domain, "dependencies": model.tree.get("dependencies", [])},
            sort_keys=False,
            allow_unicode=True,
        ),
    )
    files["proto"] = write_file(out_dir / "proto" / f"{model.domain_id}.proto", proto_text)
    files["resources"] = write_file(
        out_dir / "resources.yaml",
        yaml.safe_dump(resources, sort_keys=False, allow_unicode=True),
    )
    files["views"] = write_file(
        out_dir / "views.yaml",
        yaml.safe_dump(views, sort_keys=False, allow_unicode=True),
    )
    files["commands"] = write_file(
        out_dir / "commands.yaml",
        yaml.safe_dump(commands, sort_keys=False, allow_unicode=True),
    )
    files["renderers"] = write_file(
        out_dir / "renderers.yaml",
        yaml.safe_dump(renderers, sort_keys=False, allow_unicode=True),
    )

    handler_dir = project_root / "domains" / model.domain_id / "handlers"
    files["handler"] = write_file(handler_dir / handler_name, handler_source)
    write_file(project_root / "domains" / model.domain_id / "__init__.py", "")
    write_file(handler_dir / "__init__.py", "")

    agent_path = project_root / "contracts" / "agents" / f"{model.agent['id'].replace('-', '_')}.yaml"
    files["agent_contract"] = write_file(
        agent_path,
        yaml.safe_dump(agent_yaml, sort_keys=False, allow_unicode=True),
    )

    registry_ref = {
        "domain_pack": str(out_dir.relative_to(project_root)) if out_dir.is_relative_to(project_root) else str(out_dir),
        "agent_contract": str(agent_path.relative_to(project_root)),
    }
    files["registry_fragment"] = write_file(
        out_dir / "registry.fragment.yaml",
        yaml.safe_dump(registry_ref, sort_keys=False, allow_unicode=True),
    )
    return files


def generate_domain_pack_from_tree(
    tree: dict[str, Any],
    out_dir: Path,
    *,
    root: Path | None = None,
) -> dict[str, str]:
    project_root = root or repo_root()
    model = derive_domain_model(tree, out_dir)
    proto_text = generate_proto(model)
    resources = generate_resources(model)
    views = generate_views(resources)
    commands = generate_commands(model)
    renderers = generate_renderers(model)
    handler_name, handler_source = generate_handlers(model)
    agent_yaml = generate_agent_contract(model)

    files = write_domain_pack(
        model,
        proto_text=proto_text,
        resources=resources,
        views=views,
        commands=commands,
        renderers=renderers,
        handler_name=handler_name,
        handler_source=handler_source,
        agent_yaml=agent_yaml,
        root=project_root,
    )
    merge_main_contracts(model.domain_id, resources, views, proto_text, root=project_root)
    return files


def generate_domain_pack(
    uri_tree_path: str | Path,
    domain_dir: str | Path,
    *,
    root: Path | None = None,
) -> dict[str, str]:
    tree = parse_uri_tree(uri_tree_path)
    return generate_domain_pack_from_tree(tree, Path(domain_dir), root=root)

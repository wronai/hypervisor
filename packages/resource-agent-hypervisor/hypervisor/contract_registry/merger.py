from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from hypervisor.domain_pack.writer import repo_root, write_file


def merge_main_contracts(
    domain_id: str,
    resources: dict[str, Any],
    views: dict[str, Any],
    proto_text: str,
    *,
    root: Path | None = None,
) -> None:
    """Register generated domain artifacts in global contracts."""
    project_root = root or repo_root()
    contracts = project_root / "contracts"

    proto_name = "weather.proto" if domain_id == "weather_map" else f"{domain_id}.proto"
    write_file(contracts / "proto" / proto_name, proto_text)

    resources_path = contracts / "resources.yaml"
    existing = (
        yaml.safe_load(resources_path.read_text(encoding="utf-8"))
        if resources_path.exists()
        else {"resources": []}
    )
    existing_uris = {r.get("uri") for r in existing.get("resources", [])}
    for resource in resources.get("resources", []):
        item = {
            "uri": resource["uri_template"],
            "projection": resource["projection_ref"],
            "schema": resource["schema_ref"],
            "renderer": resource["renderer_ref"],
            "owner_agent": resource.get("owner_agent"),
            "stability": resource.get("stability", "experimental"),
            "version": resource.get("version", "v1"),
        }
        if item["uri"] not in existing_uris:
            existing.setdefault("resources", []).append(item)
            existing_uris.add(item["uri"])
    write_file(resources_path, yaml.safe_dump(existing, sort_keys=False, allow_unicode=True))

    views_path = contracts / "views.yaml"
    existing_views = (
        yaml.safe_load(views_path.read_text(encoding="utf-8"))
        if views_path.exists()
        else {"views": []}
    )
    existing_names = {view.get("name") for view in existing_views.get("views", [])}
    for view in views.get("views", []):
        item = {
            "name": view["name"],
            "viewKind": view.get("renderer", "json"),
            "mimeType": view.get("mime_type", "application/json"),
            "columns": ["place", "days", "html_url"]
            if view.get("renderer") == "html"
            else ["place", "days", "model"],
            "rendererHint": view.get("renderer", "json"),
        }
        if item["name"] not in existing_names:
            existing_views.setdefault("views", []).append(item)
            existing_names.add(item["name"])
    write_file(views_path, yaml.safe_dump(existing_views, sort_keys=False, allow_unicode=True))

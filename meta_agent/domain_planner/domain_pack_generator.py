from __future__ import annotations

from pathlib import Path
from typing import Any
import re
import yaml

ROOT = Path(__file__).resolve().parents[2]


def _write(path: Path, content: str) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return str(path)


def _package(domain_id: str) -> str:
    return f"app.{domain_id}.v1"


def _generic_proto(domain_id: str) -> str:
    pkg = _package(domain_id)
    return f'''syntax = "proto3";

package {pkg};

message RunTaskCommand {{
  string input = 1;
}}

message TaskRequested {{
  string input = 1;
  int64 requested_at = 2;
}}

message TaskCompleted {{
  string result_id = 1;
  string output = 2;
  int64 completed_at = 3;
}}

message TaskResultView {{
  string result_id = 1;
  string output = 2;
}}
'''


def _weather_proto() -> str:
    return '''syntax = "proto3";

package app.weather.v1;

message GenerateWeatherMapCommand {
  string place = 1;
  int32 days = 2;
  string forecast_model = 3;
  string output_mime_type = 4;
  bool publish_as_url = 5;
}

message WeatherMapGenerationRequested {
  string place = 1;
  int32 days = 2;
  string forecast_model = 3;
  int64 requested_at = 4;
}

message WeatherMapGenerated {
  string place = 1;
  int32 days = 2;
  string html_url = 3;
  string html_content_hash = 4;
  int64 generated_at = 5;
}

message ForecastDataView {
  string place = 1;
  int32 days = 2;
  string model = 3;
  string forecast_json = 4;
}

message WeatherMapHtmlView {
  string place = 1;
  int32 days = 2;
  string html_url = 3;
  string mime_type = 4;
  string generated_at = 5;
}
'''


def _weather_handler() -> str:
    return '''from __future__ import annotations

from datetime import datetime, timezone
import hashlib


def handler(payload: dict) -> dict:
    place = payload.get("place", "unknown")
    days = int(payload.get("days", 14))
    model = payload.get("forecast_model") or payload.get("model") or "auto"
    html = f"""<!doctype html><html><head><meta charset='utf-8'><title>Weather map {place}</title></head><body><h1>Weather map: {place}</h1><p>Forecast horizon: {days} days</p><p>Model: {model}</p><div id='map'>Generated placeholder map view.</div></body></html>"""
    digest = hashlib.sha256(html.encode("utf-8")).hexdigest()
    url = f"/artifacts/weather-map/{place}/forecast/{days}/index.html"
    return {
        "ok": True,
        "place": place,
        "days": days,
        "model": model,
        "html_url": url,
        "html_content_hash": digest,
        "mime_type": "text/html",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "html": html,
    }
'''


def _generic_handler() -> str:
    return '''from __future__ import annotations


def handler(payload: dict) -> dict:
    return {"ok": True, "payload": payload, "message": "Generated domain handler stub"}
'''


def _merge_main_contracts(domain_id: str, resources: dict, views: dict, proto_text: str) -> None:
    """Register generated domain in main contracts so registry/cross-validation can see it."""
    contracts = ROOT / "contracts"
    # proto
    proto_name = "weather.proto" if domain_id == "weather_map" else f"{domain_id}.proto"
    _write(contracts / "proto" / proto_name, proto_text)

    # resources.yaml uses compact v0.3 format: uri/projection/schema/renderer
    resources_path = contracts / "resources.yaml"
    existing = yaml.safe_load(resources_path.read_text(encoding="utf-8")) if resources_path.exists() else {"resources": []}
    existing_uris = {r.get("uri") for r in existing.get("resources", [])}
    for r in resources.get("resources", []):
        item = {
            "uri": r["uri_template"],
            "projection": r["projection_ref"],
            "schema": r["schema_ref"],
            "renderer": r["renderer_ref"],
            "owner_agent": r.get("owner_agent"),
            "stability": r.get("stability", "experimental"),
            "version": r.get("version", "v1"),
        }
        if item["uri"] not in existing_uris:
            existing.setdefault("resources", []).append(item)
            existing_uris.add(item["uri"])
    _write(resources_path, yaml.safe_dump(existing, sort_keys=False, allow_unicode=True))

    # views.yaml uses v0.3 format: name/viewKind/mimeType/columns/rendererHint
    views_path = contracts / "views.yaml"
    existing_v = yaml.safe_load(views_path.read_text(encoding="utf-8")) if views_path.exists() else {"views": []}
    existing_names = {v.get("name") for v in existing_v.get("views", [])}
    for v in views.get("views", []):
        item = {
            "name": v["name"],
            "viewKind": v.get("renderer", "json"),
            "mimeType": v.get("mime_type", "application/json"),
            "columns": ["place", "days", "html_url"] if v.get("renderer") == "html" else ["place", "days", "model"],
            "rendererHint": v.get("renderer", "json"),
        }
        if item["name"] not in existing_names:
            existing_v.setdefault("views", []).append(item)
            existing_names.add(item["name"])
    _write(views_path, yaml.safe_dump(existing_v, sort_keys=False, allow_unicode=True))


def generate_domain_pack_from_tree(tree: dict[str, Any], out_dir: Path) -> dict[str, str]:
    domain = tree["domain"]
    domain_id = domain["id"]
    py_pkg = domain_id
    out_dir.mkdir(parents=True, exist_ok=True)
    files: dict[str, str] = {}

    files["uri_tree"] = _write(out_dir / "uri_tree.yaml", yaml.safe_dump(tree, sort_keys=False, allow_unicode=True))
    files["domain"] = _write(out_dir / "domain.yaml", yaml.safe_dump({"domain": domain, "dependencies": tree.get("dependencies", [])}, sort_keys=False, allow_unicode=True))
    proto_text = _weather_proto() if domain_id == "weather_map" else _generic_proto(domain_id)
    files["proto"] = _write(out_dir / "proto" / f"{domain_id}.proto", proto_text)

    resources = {"resources": []}
    for key, res in tree.get("resources", {}).items():
        resources["resources"].append({
            "id": f"{domain_id}.{key}.v1",
            "kind": "resource",
            "uri_template": res["uri_template"],
            "stability": "experimental",
            "version": "v1",
            "schema_ref": res["schema_ref"],
            "projection_ref": f"{domain_id}_{key}_view",
            "renderer_ref": res.get("renderer_ref", "json"),
            "owner_agent": tree["agent"]["id"],
            "read_method": "resources/read",
            "mime_type": res.get("mime_type", "application/json"),
        })
    files["resources"] = _write(out_dir / "resources.yaml", yaml.safe_dump(resources, sort_keys=False, allow_unicode=True))

    views = {"views": []}
    for r in resources["resources"]:
        views["views"].append({"name": r["projection_ref"], "schema_ref": r["schema_ref"], "renderer": r["renderer_ref"], "mime_type": r["mime_type"], "rebuildable": True})
    files["views"] = _write(out_dir / "views.yaml", yaml.safe_dump(views, sort_keys=False, allow_unicode=True))
    _merge_main_contracts(domain_id, resources, views, proto_text)

    commands = {"commands": []}
    for _, cmd in tree.get("commands", {}).items():
        commands["commands"].append({"name": cmd["name"], "uri": cmd["uri"], "handler_uri": cmd.get("handler_uri"), "input_schema_ref": cmd.get("input_schema_ref"), "emits": cmd.get("emits", [])})
    files["commands"] = _write(out_dir / "commands.yaml", yaml.safe_dump(commands, sort_keys=False, allow_unicode=True))

    renderers = {"renderers": [{"id": "json", "view_kind": "json", "allowed_mime_types": ["application/json"]}]}
    if any(r.get("renderer_ref") == "html" for r in tree.get("resources", {}).values()):
        renderers["renderers"].append({"id": "html", "view_kind": "html", "allowed_mime_types": ["text/html", "application/json"]})
    files["renderers"] = _write(out_dir / "renderers.yaml", yaml.safe_dump(renderers, sort_keys=False, allow_unicode=True))

    handler_name = "generate_weather_map.py" if domain_id == "weather_map" else "run.py"
    files["handler"] = _write(ROOT / "domains" / py_pkg / "handlers" / handler_name, _weather_handler() if domain_id == "weather_map" else _generic_handler())
    _write(ROOT / "domains" / py_pkg / "__init__.py", "")
    _write(ROOT / "domains" / py_pkg / "handlers" / "__init__.py", "")

    if domain_id == "weather_map":
        agent_caps = [
            {"name": "read_weather_map", "type": "resource_read", "description": "Read generated weather map HTML view for a location and forecast horizon.", "uri": "resource://weather/maps/{place}/forecast/{days}", "output_schema": "app.weather.v1.WeatherMapHtmlView", "renderer": "html"},
            {"name": "generate_weather_map", "type": "command", "description": "Generate a weather map forecast HTML view for a location.", "command": "GenerateWeatherMap", "input_schema": "app.weather.v1.GenerateWeatherMapCommand", "emits": ["WeatherMapGenerationRequested", "WeatherMapGenerated"]},
        ]
    else:
        agent_caps = [{"name": "run", "type": "command", "command": "RunTask", "input_schema": f"{_package(domain_id)}.RunTaskCommand", "emits": ["TaskRequested", "TaskCompleted"]}]

    agent_yaml = {
        "agent": {
            "name": tree["agent"]["id"],
            "python_package": tree["agent"]["id"].replace("-", "_"),
            "version": "0.1.0",
            "description": domain.get("description", "Generated thin agent"),
            "runtime_url_env": "RESOURCE_RUNTIME_URL",
            "runtime_url_default": "http://localhost:8000",
        },
        "capabilities": agent_caps,
    }
    agent_path = ROOT / "contracts" / "agents" / f"{tree['agent']['id'].replace('-', '_')}.yaml"
    files["agent_contract"] = _write(agent_path, yaml.safe_dump(agent_yaml, sort_keys=False, allow_unicode=True))
    registry_ref = {"domain_pack": str(out_dir.relative_to(ROOT)) if out_dir.is_relative_to(ROOT) else str(out_dir), "agent_contract": str(agent_path.relative_to(ROOT))}
    files["registry_fragment"] = _write(out_dir / "registry.fragment.yaml", yaml.safe_dump(registry_ref, sort_keys=False, allow_unicode=True))
    return files

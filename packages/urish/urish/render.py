from __future__ import annotations

import json
from typing import Any

import yaml


def render_result(result: dict[str, Any], *, output: str = "json", quiet: bool = False) -> str:
    if output == "json":
        return json.dumps(result, indent=2, ensure_ascii=False)
    if output == "yaml":
        return yaml.safe_dump(result, sort_keys=False, allow_unicode=True)
    if output == "raw":
        data = result.get("data")
        if isinstance(data, str):
            return data
        if isinstance(data, dict) and "stdout" in data:
            return str(data.get("stdout") or "")
        return json.dumps(data, ensure_ascii=False)
    if output == "text" or quiet:
        return _render_text(result, quiet=quiet)
    return _render_table(result)


def _render_text(result: dict[str, Any], *, quiet: bool) -> str:
    if quiet:
        return "ok" if result.get("ok") else "failed"
    ok = "OK" if result.get("ok") else "FAIL"
    wf = result.get("workflow_status", "-")
    svc = result.get("service_result_status", "-")
    rtype = result.get("result_type", "-")
    duration = (result.get("meta") or {}).get("duration_ms", "-")
    lines = [f"{ok} {wf}/{svc} {rtype} {duration}ms"]
    data = result.get("data")
    if isinstance(data, dict):
        if "stdout" in data and data["stdout"]:
            lines.extend(["stdout:", str(data["stdout"]).rstrip()])
        elif "text" in data:
            lines.append(str(data["text"]))
    elif data is not None:
        lines.append(str(data))
    error = result.get("error")
    if error:
        lines.append(f"error: {error}")
    return "\n".join(lines)


def _render_table(result: dict[str, Any]) -> str:
    return _render_text(result, quiet=False)

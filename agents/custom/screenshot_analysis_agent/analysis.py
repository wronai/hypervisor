from __future__ import annotations

import hashlib
import json
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any
from urllib.parse import unquote, urlparse

from uri2ops.operator.artifact_resolver import resolve_artifact_path
from uri3.paths import find_repo_root

ANALYSIS_DIR = Path("output") / "analysis" / "screenshots"
JSONL_NAME = "screenshot-analysis.jsonl"
MARKDOWN_NAME = "screenshot-analysis.md"


def repo_root() -> Path:
    return find_repo_root(strict=False)


def _path_from_file_uri(uri: str) -> Path:
    parsed = urlparse(uri)
    if parsed.scheme != "file":
        return Path(uri)
    if parsed.netloc and parsed.path:
        return Path(unquote(f"/{parsed.netloc}{parsed.path}"))
    if parsed.netloc:
        return Path(unquote(parsed.netloc))
    return Path(unquote(parsed.path))


def resolve_observation_path(uri: str, *, root: Path | None = None) -> Path:
    base = root or repo_root()
    parsed = urlparse(uri)
    if parsed.scheme == "artifact":
        return resolve_artifact_path(uri, root=base)
    if parsed.scheme == "file":
        path = _path_from_file_uri(uri)
        return path if path.is_absolute() else base / path
    path = Path(uri)
    return path if path.is_absolute() else base / path


def _png_size(data: bytes) -> dict[str, int] | None:
    if len(data) < 24 or not data.startswith(b"\x89PNG\r\n\x1a\n"):
        return None
    if data[12:16] != b"IHDR":
        return None
    return {
        "width": int.from_bytes(data[16:20], "big"),
        "height": int.from_bytes(data[20:24], "big"),
    }


def _json_summary(data: bytes) -> dict[str, Any] | None:
    try:
        payload = json.loads(data.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return None
    if not isinstance(payload, dict):
        return {"json_type": type(payload).__name__}
    visible = []
    for key in ("url", "target_uri", "title", "text", "screenshot", "screen"):
        value = payload.get(key)
        if value is not None:
            visible.append(f"{key}={value}")
    return {
        "json_keys": sorted(str(key) for key in payload),
        "visible_text": "; ".join(visible) if visible else "json metadata artifact",
    }


def _read_previous(jsonl_path: Path) -> dict[str, Any] | None:
    if not jsonl_path.exists():
        return None
    lines = [line for line in jsonl_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    if not lines:
        return None
    try:
        loaded = json.loads(lines[-1])
    except json.JSONDecodeError:
        return None
    return loaded if isinstance(loaded, dict) else None


def _append_markdown(path: Path, observation: dict[str, Any]) -> None:
    first_write = not path.exists()
    with path.open("a", encoding="utf-8") as handle:
        if first_write:
            handle.write("# Screenshot observations\n\n")
        handle.write(f"## {observation['observed_at']} - {observation['run_label']}\n\n")
        handle.write(f"- source: `{observation.get('source_url') or 'unknown'}`\n")
        handle.write(f"- artifact: `{observation['artifact_uri']}`\n")
        handle.write(f"- media: `{observation['media_type']}`\n")
        handle.write(f"- sha256: `{observation['sha256']}`\n")
        handle.write(f"- changed_from_previous: `{observation['changed_from_previous']}`\n")
        handle.write(f"- summary: {observation['summary']}\n\n")


def analyze_artifact(
    artifact_uri: str,
    *,
    source_url: str | None = None,
    run_label: str = "manual",
    root: Path | None = None,
) -> dict[str, Any]:
    base = root or repo_root()
    path = resolve_observation_path(artifact_uri, root=base)
    if not path.exists():
        return {
            "ok": False,
            "result_type": "screenshot_analysis",
            "error": f"artifact not found: {artifact_uri}",
            "path": str(path),
        }

    data = path.read_bytes()
    sha256 = hashlib.sha256(data).hexdigest()
    png = _png_size(data)
    json_summary = _json_summary(data)
    if png:
        media_type = "image/png"
        summary = f"PNG screenshot {png['width']}x{png['height']}, {len(data)} bytes."
    elif json_summary:
        media_type = "application/json"
        summary = f"JSON screenshot metadata: {json_summary.get('visible_text')}"
    else:
        media_type = "application/octet-stream"
        summary = f"Binary artifact, {len(data)} bytes."

    out_dir = base / ANALYSIS_DIR
    out_dir.mkdir(parents=True, exist_ok=True)
    jsonl_path = out_dir / JSONL_NAME
    previous = _read_previous(jsonl_path)
    observation = {
        "ok": True,
        "result_type": "screenshot_analysis",
        "observed_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "run_label": run_label,
        "source_url": source_url,
        "artifact_uri": artifact_uri,
        "path": str(path),
        "media_type": media_type,
        "size_bytes": len(data),
        "sha256": sha256,
        "image": png,
        "json": json_summary,
        "summary": summary,
        "previous_sha256": previous.get("sha256") if previous else None,
        "changed_from_previous": bool(previous and previous.get("sha256") != sha256),
        "analysis_jsonl_uri": f"file://{jsonl_path.resolve().as_posix()}",
        "analysis_markdown_uri": f"file://{(out_dir / MARKDOWN_NAME).resolve().as_posix()}",
    }
    with jsonl_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(observation, ensure_ascii=False, sort_keys=True) + "\n")
    _append_markdown(out_dir / MARKDOWN_NAME, observation)
    return observation


def _post_json(url: str, payload: dict[str, Any], *, timeout: float = 30.0) -> dict[str, Any]:
    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            data = response.read()
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"{url} failed with HTTP {exc.code}: {detail}") from exc
    loaded = json.loads(data.decode("utf-8"))
    if not isinstance(loaded, dict):
        raise RuntimeError(f"{url} returned non-object JSON")
    return loaded


def _extract_screenshot_artifact(result: dict[str, Any]) -> str | None:
    fallback: str | None = None
    for step in result.get("steps") or []:
        if not isinstance(step, dict):
            continue
        payload = step.get("result")
        if not isinstance(payload, dict):
            continue
        artifact_uri = payload.get("artifact_uri") or payload.get("screenshot_uri")
        if not artifact_uri:
            continue
        candidate = str(artifact_uri)
        step_id = str(step.get("id") or "").lower()
        step_uri = str(step.get("uri") or "").lower()
        operation = str(step.get("operation") or "").lower()
        if (
            "screenshot" in step_id
            or "screenshot" in step_uri
            or operation in {"screenshot", "capture"}
        ):
            return candidate
        fallback = fallback or candidate
    return fallback


def capture_with_operator(
    *,
    operator_url: str,
    target_url: str,
    adapter: str = "mock",
    approve: bool = True,
    run_label: str = "agent-screenshot-analysis",
    root: Path | None = None,
) -> dict[str, Any]:
    task = {
        "task": {
            "id": f"{run_label}-capture",
            "description": "Capture a page screenshot for screenshot-analysis-agent.",
        },
        "steps": [
            {
                "id": "open_page",
                "uri": "browser://chrome/page/open",
                "operation": "open",
                "kind": "command",
                "payload": {"url": target_url},
            },
            {
                "id": "screenshot_page",
                "uri": "browser://chrome/page/screenshot",
                "operation": "screenshot",
                "kind": "query",
                "depends_on": ["open_page"],
            },
        ],
    }
    operator_result = _post_json(
        f"{operator_url.rstrip('/')}/run",
        {"task": task, "dry_run": False, "approve": approve, "adapter": adapter},
    )
    artifact_uri = _extract_screenshot_artifact(operator_result)
    if not artifact_uri:
        return {
            "ok": False,
            "result_type": "capture_and_analysis",
            "error": "desktop operator did not return screenshot artifact_uri",
            "operator_result": operator_result,
        }
    analysis = analyze_artifact(
        artifact_uri,
        source_url=target_url,
        run_label=run_label,
        root=root,
    )
    return {
        "ok": bool(operator_result.get("workflow_result", {}).get("ok") and analysis.get("ok")),
        "result_type": "capture_and_analysis",
        "operator_url": operator_url,
        "target_url": target_url,
        "artifact_uri": artifact_uri,
        "operator_result": operator_result,
        "analysis": analysis,
        "schedule_uri": "cron://screenshots/capture-analysis/every-5-min",
    }

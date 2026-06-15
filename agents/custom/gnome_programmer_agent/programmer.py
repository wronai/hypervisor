from __future__ import annotations

import json
from pathlib import Path
from typing import Any
from urllib import error, request

from uri3.paths import find_repo_root


def repo_root() -> Path:
    return find_repo_root(strict=False)


def _post_json(url: str, payload: dict[str, Any], *, timeout: float = 60.0) -> dict[str, Any]:
    req = request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with request.urlopen(req, timeout=timeout) as response:
            data = json.loads(response.read().decode("utf-8"))
    except error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"{url} failed with HTTP {exc.code}: {detail}") from exc
    if not isinstance(data, dict):
        raise RuntimeError(f"{url} returned non-object JSON")
    return data


def _operator_task(
    *,
    operator_url: str,
    adapter: str,
    approve: bool,
    steps: list[dict[str, Any]],
    run_label: str,
) -> dict[str, Any]:
    return _post_json(
        f"{operator_url.rstrip('/')}/run",
        {
            "task": {
                "task": {
                    "id": run_label,
                    "description": "GNOME programmer session via desktop-operator.",
                },
                "steps": steps,
            },
            "dry_run": False,
            "approve": approve,
            "adapter": adapter,
        },
    )


def observe_desktop(
    *,
    operator_url: str = "http://localhost:8791",
    adapter: str = "mock",
    approve: bool = True,
    run_label: str = "gnome-programmer",
    root: Path | None = None,
) -> dict[str, Any]:
    base = root or repo_root()
    result = _operator_task(
        operator_url=operator_url,
        adapter=adapter,
        approve=approve,
        run_label=run_label,
        steps=[
            {
                "id": "observe_desktop",
                "uri": "screen://desktop/observe",
                "operation": "observe",
                "kind": "query",
            }
        ],
    )
    artifact_uri = _extract_artifact(result)
    out_dir = base / "output" / "analysis" / "gnome-programmer"
    out_dir.mkdir(parents=True, exist_ok=True)
    payload = {
        "ok": bool(result.get("workflow_result", {}).get("ok", result.get("ok", True))),
        "artifact_uri": artifact_uri,
        "operator_result": result,
    }
    (out_dir / "observe-latest.json").write_text(
        json.dumps(payload, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    return payload


def type_on_desktop(
    *,
    text: str,
    operator_url: str = "http://localhost:8791",
    adapter: str = "mock",
    approve: bool = True,
    run_label: str = "gnome-programmer",
) -> dict[str, Any]:
    result = _operator_task(
        operator_url=operator_url,
        adapter=adapter,
        approve=approve,
        run_label=run_label,
        steps=[
            {
                "id": "type_on_desktop",
                "uri": "input://desktop/type",
                "operation": "type",
                "kind": "command",
                "payload": {"text": text},
            }
        ],
    )
    return {"ok": bool(result.get("workflow_result", {}).get("ok", result.get("ok", True))), "operator_result": result}


def programmer_session(
    *,
    operator_url: str = "http://localhost:8791",
    adapter: str = "mock",
    approve: bool = True,
    command_text: str = "",
    run_label: str = "gnome-programmer",
    root: Path | None = None,
) -> dict[str, Any]:
    base = root or repo_root()
    observe = observe_desktop(
        operator_url=operator_url,
        adapter=adapter,
        approve=approve,
        run_label=run_label,
        root=base,
    )
    typed = None
    if command_text.strip():
        typed = type_on_desktop(
            text=command_text,
            operator_url=operator_url,
            adapter=adapter,
            approve=approve,
            run_label=f"{run_label}-type",
        )
    payload = {
        "ok": observe.get("ok") and (typed is None or typed.get("ok")),
        "observe": observe,
        "type": typed,
        "adapter": adapter,
    }
    out_dir = base / "output" / "analysis" / "gnome-programmer"
    out_dir.mkdir(parents=True, exist_ok=True)
    jsonl = out_dir / "programmer-session.jsonl"
    with jsonl.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, ensure_ascii=False) + "\n")
    (out_dir / "programmer-session-latest.json").write_text(
        json.dumps(payload, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    return payload


def _extract_artifact(result: dict[str, Any]) -> str | None:
    for step in result.get("steps") or []:
        if not isinstance(step, dict):
            continue
        payload = step.get("result")
        if isinstance(payload, dict):
            artifact_uri = payload.get("artifact_uri") or payload.get("screenshot_uri")
            if artifact_uri:
                return str(artifact_uri)
    workflow = result.get("workflow_result") or {}
    for step in workflow.get("steps") or []:
        if not isinstance(step, dict):
            continue
        payload = step.get("result")
        if isinstance(payload, dict):
            artifact_uri = payload.get("artifact_uri") or payload.get("screenshot_uri")
            if artifact_uri:
                return str(artifact_uri)
    return None

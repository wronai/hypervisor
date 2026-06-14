from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import yaml


def load_payload(
    raw: str | None = None,
    *,
    payload_file: str | None = None,
    stdin: bool = False,
    stdin_mode: str = "data",
) -> dict[str, Any]:
    if stdin:
        text = sys.stdin.read()
        if not text.strip():
            return {}
        data = json.loads(text)
        if stdin_mode == "envelope" and isinstance(data, dict) and "data" in data:
            inner = data["data"]
            return inner if isinstance(inner, dict) else {"value": inner}
        if isinstance(data, dict):
            return data
        return {"value": data}

    if payload_file:
        path = Path(payload_file)
        text = path.read_text(encoding="utf-8")
        if path.suffix in {".yaml", ".yml"}:
            loaded = yaml.safe_load(text)
            return loaded if isinstance(loaded, dict) else {}
        return json.loads(text)

    if raw is None or raw == "":
        return {}
    if raw.startswith("@"):
        return load_payload(payload_file=raw[1:])
    return json.loads(raw)

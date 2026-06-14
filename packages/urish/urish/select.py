from __future__ import annotations

from typing import Any


def select_path(data: Any, path: str) -> Any:
    if not path:
        return data
    current = data
    for part in path.split("."):
        if part == "":
            continue
        if isinstance(current, dict):
            current = current.get(part)
        elif isinstance(current, list):
            try:
                current = current[int(part)]
            except (ValueError, IndexError) as exc:
                raise KeyError(path) from exc
        else:
            raise KeyError(path)
    return current


def select_from_envelope(envelope: dict[str, Any], path: str) -> Any:
    if path.startswith("data."):
        return select_path(envelope.get("data"), path[5:])
    if path == "data":
        return envelope.get("data")
    return select_path(envelope, path)

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from uri3.logs.reader import DEFAULT_STREAM_FILES
from uri3.paths import find_repo_root


def append_log(
    stream: str,
    message: str,
    *,
    level: str = "INFO",
    logger: str | None = None,
    root: Path | None = None,
    **fields: Any,
) -> Path:
    repo = root or find_repo_root()
    relative = DEFAULT_STREAM_FILES.get(stream, f"output/logs/{stream}.log")
    path = repo / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "level": level.upper(),
        "logger": logger or stream,
        "message": message,
        **fields,
    }
    with open(path, "a", encoding="utf-8") as handle:
        handle.write(json.dumps(entry, ensure_ascii=False) + "\n")
    return path

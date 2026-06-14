from __future__ import annotations

import json
import re
from typing import Any


def empty_entry(line: str, line_no: int) -> dict[str, Any]:
    return {"line": line_no, "level": "INFO", "message": "", "raw": line, "timestamp": None}


def parse_json_entry(line: str, line_no: int) -> dict[str, Any] | None:
    stripped = line.strip()
    if not stripped:
        return None
    try:
        data = json.loads(stripped)
    except json.JSONDecodeError:
        return None
    if not isinstance(data, dict):
        return None
    return {
        "line": line_no,
        "timestamp": data.get("timestamp") or data.get("time") or data.get("@timestamp"),
        "level": str(data.get("level") or data.get("severity") or "INFO").upper(),
        "logger": data.get("logger") or data.get("component") or data.get("name"),
        "message": data.get("message") or data.get("msg") or stripped,
        "fields": {
            key: value
            for key, value in data.items()
            if key not in {"timestamp", "time", "level", "logger", "message", "msg"}
        },
        "raw": line,
    }


_TEXT_LOG_RE = re.compile(
    r"^(?:(?P<timestamp>\d{4}-\d{2}-\d{2}[ T]\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:?\d{2})?)\s+)?"
    r"(?:(?P<level>DEBUG|INFO|WARNING|ERROR|CRITICAL)\s+)?"
    r"(?:(?P<logger>[\w.\-]+)\s+[-:]\s+)?"
    r"(?P<message>.*)$",
    re.IGNORECASE,
)


def parse_text_entry(line: str, line_no: int) -> dict[str, Any] | None:
    stripped = line.strip()
    if not stripped:
        return None
    match = _TEXT_LOG_RE.match(stripped)
    if not match:
        return None
    groups = match.groupdict()
    return {
        "line": line_no,
        "timestamp": groups.get("timestamp"),
        "level": (groups.get("level") or "INFO").upper(),
        "logger": groups.get("logger"),
        "message": groups.get("message") or stripped,
        "raw": line,
    }


def parse_log_line(line: str, line_no: int) -> dict[str, Any]:
    if not line.strip():
        return empty_entry(line, line_no)
    return parse_json_entry(line, line_no) or parse_text_entry(line, line_no) or {
        "line": line_no,
        "level": "INFO",
        "message": line.strip(),
        "raw": line,
        "timestamp": None,
    }

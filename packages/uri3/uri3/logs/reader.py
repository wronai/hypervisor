from __future__ import annotations

import json
import re
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from uri3.paths import find_repo_root
from uri3.resolvers.log_resolver import LOG_LEVELS, LogRef, parse_log_uri

DEFAULT_STREAM_FILES = {
    "hypervisor": "output/logs/hypervisor.log",
    "uri3": "output/logs/uri3.log",
    "nl2uri": "output/logs/nl2uri.log",
    "nl2a": "output/logs/nl2a.log",
    "factory": "output/logs/factory.log",
    "meta_agent": "output/logs/meta_agent.log",
    "default": "output/logs/hypervisor.log",
}


def resolve_log_path(ref: LogRef, *, root: Path | None = None) -> Path:
    repo = root or find_repo_root()
    if ref.path is not None:
        return ref.path if ref.path.is_absolute() else repo / ref.path
    relative = DEFAULT_STREAM_FILES.get(ref.stream, f"output/logs/{ref.stream}.log")
    return repo / relative


def _parse_since(value: str | None) -> datetime | None:
    if not value:
        return None
    value = value.strip()
    now = datetime.now(timezone.utc)
    if value.endswith("h"):
        return now - timedelta(hours=float(value[:-1]))
    if value.endswith("m"):
        return now - timedelta(minutes=float(value[:-1]))
    if value.endswith("d"):
        return now - timedelta(days=float(value[:-1]))
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)
    except ValueError:
        return None


def _parse_entry(line: str, line_no: int) -> dict[str, Any]:
    stripped = line.strip()
    if not stripped:
        return {"line": line_no, "level": "INFO", "message": "", "raw": line, "timestamp": None}

    try:
        data = json.loads(stripped)
        if isinstance(data, dict):
            return {
                "line": line_no,
                "timestamp": data.get("timestamp") or data.get("time") or data.get("@timestamp"),
                "level": str(data.get("level") or data.get("severity") or "INFO").upper(),
                "logger": data.get("logger") or data.get("component") or data.get("name"),
                "message": data.get("message") or data.get("msg") or stripped,
                "fields": {k: v for k, v in data.items() if k not in {"timestamp", "time", "level", "logger", "message", "msg"}},
                "raw": line,
            }
    except json.JSONDecodeError:
        pass

    match = re.match(
        r"^(?:(?P<timestamp>\d{4}-\d{2}-\d{2}[ T]\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:?\d{2})?)\s+)?"
        r"(?:(?P<level>DEBUG|INFO|WARNING|ERROR|CRITICAL)\s+)?"
        r"(?:(?P<logger>[\w.\-]+)\s+[-:]\s+)?"
        r"(?P<message>.*)$",
        stripped,
        re.IGNORECASE,
    )
    if match:
        groups = match.groupdict()
        return {
            "line": line_no,
            "timestamp": groups.get("timestamp"),
            "level": (groups.get("level") or "INFO").upper(),
            "logger": groups.get("logger"),
            "message": groups.get("message") or stripped,
            "raw": line,
        }

    return {"line": line_no, "level": "INFO", "message": stripped, "raw": line, "timestamp": None}


def _entry_timestamp(entry: dict[str, Any]) -> datetime | None:
    raw = entry.get("timestamp")
    if not raw:
        return None
    try:
        parsed = datetime.fromisoformat(str(raw).replace("Z", "+00:00"))
        return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)
    except ValueError:
        return None


def _level_rank(level: str | None) -> int:
    if not level:
        return 1
    try:
        return LOG_LEVELS.index(level.upper())
    except ValueError:
        return 1


def _matches_filters(entry: dict[str, Any], ref: LogRef, since_dt: datetime | None, until_dt: datetime | None) -> bool:
    if ref.level and _level_rank(entry.get("level")) < _level_rank(ref.level):
        return False
    if ref.logger:
        logger = str(entry.get("logger") or "")
        if ref.logger.lower() not in logger.lower():
            return False
    if ref.grep:
        haystack = " ".join(
            str(entry.get(key) or "")
            for key in ("message", "logger", "raw")
        ).lower()
        if ref.grep.lower() not in haystack:
            return False
    ts = _entry_timestamp(entry)
    if since_dt and ts and ts < since_dt:
        return False
    if until_dt and ts and ts > until_dt:
        return False
    return True


def read_logs(uri: str, *, root: Path | None = None) -> list[dict[str, Any]]:
    ref = parse_log_uri(uri)
    path = resolve_log_path(ref, root=root)
    if not path.exists():
        return []

    since_dt = _parse_since(ref.since)
    until_dt = _parse_since(ref.until)
    matched: list[dict[str, Any]] = []

    with open(path, "r", encoding="utf-8", errors="replace") as handle:
        for line_no, line in enumerate(handle, start=1):
            entry = _parse_entry(line, line_no)
            if _matches_filters(entry, ref, since_dt, until_dt):
                matched.append(entry)

    if ref.tail and ref.limit:
        matched = matched[-ref.limit :]
    elif ref.offset:
        matched = matched[ref.offset :]
    if ref.limit and not ref.tail:
        matched = matched[: ref.limit]
    return matched


def summarize_logs(uri: str, *, root: Path | None = None) -> dict[str, Any]:
    ref = parse_log_uri(uri)
    path = resolve_log_path(ref, root=root)
    entries = read_logs(uri, root=root)
    levels = Counter(str(item.get("level") or "INFO").upper() for item in entries)
    loggers = Counter(str(item.get("logger") or "unknown") for item in entries)
    return {
        "uri": uri,
        "path": str(path),
        "exists": path.exists(),
        "size_bytes": path.stat().st_size if path.exists() else 0,
        "matched": len(entries),
        "levels": dict(levels),
        "loggers": dict(loggers),
        "filters": ref.to_dict(),
    }

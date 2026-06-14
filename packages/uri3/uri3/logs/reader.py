from __future__ import annotations

from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from uri3.logs.filters import matches_filters
from uri3.logs.parsing import parse_log_line
from uri3.paths import find_repo_root
from uri3.resolvers.log_resolver import LogRef, parse_log_uri

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
            entry = parse_log_line(line, line_no)
            if matches_filters(entry, ref, since_dt, until_dt):
                matched.append(entry)

    if ref.tail and ref.limit:
        matched = matched[-ref.limit :]
    elif ref.offset:
        matched = matched[ref.offset :]
    if ref.limit and not ref.tail:
        matched = matched[: ref.limit]
    return matched


def read_logs_result(uri: str, *, root: Path | None = None) -> list[dict[str, Any]] | dict[str, Any]:
    summary = summarize_logs(uri, root=root)
    if not summary["exists"]:
        return {
            **summary,
            "entries": [],
            "hint": "Log file not found. Run `nl2a` or `hypervisor run-agent` to create output/logs/*.log entries.",
        }
    entries = read_logs(uri, root=root)
    if not entries:
        return {**summary, "entries": [], "hint": "No log lines matched the current filters."}
    return entries


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

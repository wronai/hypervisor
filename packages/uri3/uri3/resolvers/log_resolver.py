from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlparse


LOG_LEVELS = ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL")


@dataclass(frozen=True)
class LogRef:
    uri: str
    stream: str
    path: Path | None
    level: str | None = None
    grep: str | None = None
    logger: str | None = None
    since: str | None = None
    until: str | None = None
    limit: int = 100
    offset: int = 0
    tail: bool = False
    format: str = "auto"
    query: dict[str, list[str]] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "uri": self.uri,
            "stream": self.stream,
            "path": str(self.path) if self.path else None,
            "level": self.level,
            "grep": self.grep,
            "logger": self.logger,
            "since": self.since,
            "until": self.until,
            "limit": self.limit,
            "offset": self.offset,
            "tail": self.tail,
            "format": self.format,
        }


def _first(query: dict[str, list[str]], key: str, default: str | None = None) -> str | None:
    values = query.get(key)
    if not values:
        return default
    return values[0]


def _int(query: dict[str, list[str]], key: str, default: int) -> int:
    raw = _first(query, key)
    if raw is None:
        return default
    try:
        return max(0, int(raw))
    except ValueError:
        return default


def _bool(query: dict[str, list[str]], key: str, default: bool = False) -> bool:
    raw = (_first(query, key) or "").lower()
    if not raw:
        return default
    return raw in {"1", "true", "yes", "on"}


def parse_log_uri(uri: str) -> LogRef:
    parsed = urlparse(uri)
    if parsed.scheme != "log":
        raise ValueError(f"Not a log URI: {uri}")

    query = parse_qs(parsed.query)
    stream = parsed.netloc or "hypervisor"
    path: Path | None = None

    if stream == "file":
        file_path = parsed.path or ""
        if not file_path or file_path == "/":
            raise ValueError("log://file/ requires a path, e.g. log://file/output/logs/hypervisor.log")
        path = Path(file_path.lstrip("/"))
    elif parsed.path and parsed.path not in {"", "/"}:
        path = Path(parsed.path.lstrip("/"))

    level = _first(query, "level") or _first(query, "min_level")
    if level:
        level = level.upper()

    return LogRef(
        uri=uri,
        stream=stream,
        path=path,
        level=level,
        grep=_first(query, "grep") or _first(query, "q") or _first(query, "contain"),
        logger=_first(query, "logger") or _first(query, "component"),
        since=_first(query, "since") or _first(query, "from"),
        until=_first(query, "until") or _first(query, "to"),
        limit=_int(query, "limit", 100),
        offset=_int(query, "offset", 0),
        tail=_bool(query, "tail", False),
        format=_first(query, "format", "auto") or "auto",
        query=query,
    )


def resolve_log(uri: str) -> dict[str, Any]:
    ref = parse_log_uri(uri)
    payload = ref.to_dict()
    payload["scheme"] = "log"
    payload["transport"] = "file"
    return payload


class LogResolver:
    scheme = "log"

    def resolve(self, uri: str):
        return resolve_log(uri)

    def read(self, uri: str, *, summary: bool = False):
        from uri3.logs.reader import read_logs, summarize_logs

        if summary:
            return summarize_logs(uri)
        return read_logs(uri)

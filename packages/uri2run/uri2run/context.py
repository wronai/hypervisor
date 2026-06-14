from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class RunContext:
    root: Path | None = None
    timeout: float = 30.0
    extra: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_mapping(cls, context: dict[str, Any] | None) -> RunContext:
        raw = context or {}
        root = raw.get("root")
        return cls(
            root=Path(root) if root else None,
            timeout=float(raw.get("timeout") or 30.0),
            extra=dict(raw),
        )

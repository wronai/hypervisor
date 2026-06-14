from __future__ import annotations

import hashlib
from pathlib import Path


def file_sha256(path: str | Path) -> str:
    data = Path(path).read_bytes()
    return "sha256:" + hashlib.sha256(data).hexdigest()

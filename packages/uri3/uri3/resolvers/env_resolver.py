from __future__ import annotations

import os
from urllib.parse import urlparse

from uri3.protocols.parser import parse_uri


def resolve_env(uri: str) -> dict[str, str | bool | None]:
    parsed = urlparse(uri)
    name = parsed.netloc or parsed.path.lstrip("/")
    if not name:
        raise ValueError("env:// URI requires variable name")
    return {"name": name, "exists": name in os.environ, "value": os.environ.get(name)}


class EnvResolver:
    scheme = "env"

    def resolve(self, uri):
        return resolve_env(uri)

from __future__ import annotations

from typing import Any

from uri3.resolvers.explain import explain_uri


def explain_target(uri: str, *, registry: str | None = None) -> dict[str, Any]:
    return explain_uri(uri, registry_root=registry or None)

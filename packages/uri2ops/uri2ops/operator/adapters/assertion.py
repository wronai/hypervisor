from __future__ import annotations

from typing import Any


def check(payload: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    expected = payload.get("expected")
    actual = payload.get("actual")
    if actual is None:
        actual = payload.get("actual_from")
    ok = str(expected) in str(actual)
    return {"ok": ok, "expected": expected, "actual": actual}

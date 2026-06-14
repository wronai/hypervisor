from __future__ import annotations

from typing import Any


def exit_code_for_result(result: dict[str, Any], *, policy_blocked: bool = False) -> int:
    if policy_blocked:
        return 4
    if result.get("validation_failed"):
        return 3
    if result.get("not_found"):
        return 5
    if result.get("dependency_missing"):
        return 6
    if result.get("execution_status") == "failed":
        return 2
    if not result.get("ok", True):
        return 1
    if result.get("service_result_status") == "failed":
        return 1
    return 0

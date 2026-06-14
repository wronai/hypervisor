from __future__ import annotations

from typing import Any

from uri3.results import service_result


def run_mock(payload: dict[str, Any], context: dict[str, Any]):
    return service_result(ok=True, result_type="mock", data={"payload": payload, "context": context})

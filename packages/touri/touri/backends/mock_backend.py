from __future__ import annotations

from typing import Any

from touri.models import service_result


def call_mock_backend(payload: dict[str, Any], context: dict[str, Any]):
    return service_result(ok=True, result_type="mock", data={"payload": payload, "context": context})

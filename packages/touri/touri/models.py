from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

try:
    from uri3.results import ErrorEnvelope, ServiceResult, service_result
except ImportError:  # pragma: no cover
    from dataclasses import dataclass as _dataclass

    @_dataclass
    class ErrorEnvelope:
        code: str
        source: str = ""
        recoverable: bool = False
        detail: str = ""
        data_quality: dict[str, Any] = field(default_factory=dict)

        def to_dict(self) -> dict[str, Any]:
            return asdict(self)

    @_dataclass
    class ServiceResult:
        ok: bool
        result_type: str = "data"
        workflow_status: str | None = None
        execution_status: str | None = None
        service_result_status: str | None = None
        uri: str | None = None
        capability: str | None = None
        backend: str | None = None
        data: Any = None
        artifact_uri: str | None = None
        errors: list[Any] = field(default_factory=list)
        warnings: list[str] = field(default_factory=list)
        meta: dict[str, Any] = field(default_factory=dict)

        def finalize(self, *, execution_completed: bool = True) -> ServiceResult:
            return self

        def to_dict(self) -> dict[str, Any]:
            return asdict(self)

    def service_result(ok: bool, result_type: str = "data", **kwargs: Any) -> ServiceResult:
        return ServiceResult(ok=ok, result_type=result_type, **kwargs)


@dataclass
class CapabilityRef:
    id: str
    scheme: str
    uri_template: str
    operation: str = "call"
    kind: str = "query"
    description: str = ""


@dataclass
class BackendRef:
    type: str
    target: str | None = None
    command: str | None = None
    method: str | None = None
    url: str | None = None
    operation: str | None = None
    flow: str | None = None
    graph: str | None = None
    extra: dict[str, Any] = field(default_factory=dict)


@dataclass
class CapabilityManifest:
    version: int
    capability: CapabilityRef
    backend: BackendRef
    input: dict[str, Any] = field(default_factory=dict)
    output: dict[str, Any] = field(default_factory=dict)
    policy: dict[str, Any] = field(default_factory=dict)
    events: dict[str, Any] = field(default_factory=dict)
    data_quality: dict[str, Any] = field(default_factory=dict)
    fallbacks: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

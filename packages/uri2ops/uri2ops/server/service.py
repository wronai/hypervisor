from __future__ import annotations

from pathlib import Path
from typing import Any

from uri2ops.operation_registry.models import OperationSpec
from uri2ops.operator.models import OperatorTask
from uri2ops.operator.runner import plan_task, run_task
from uri2ops.operator.task import parse_task
from uri2ops.operator.validator import validate_task_data
from uri2ops.remote_registry.loader import list_remote_sources, registry_document, resolve_operation_registry


class OperatorService:
    def __init__(self, *, root: Path | None = None) -> None:
        self.root = Path(root) if root else Path.cwd()

    def registry(self):
        return resolve_operation_registry(root=self.root)

    def registry_export(self) -> dict[str, Any]:
        return registry_document(self.registry())

    def list_operations(self) -> list[dict[str, Any]]:
        return [spec.to_dict() for spec in self.registry().list()]

    def describe_operation(self, scheme: str, operation: str) -> OperationSpec:
        return self.registry().require(scheme, operation)

    def list_registry_sources(self) -> list[dict[str, Any]]:
        return list_remote_sources(self.root)

    def validate_task(self, task_data: dict[str, Any]) -> list[str]:
        return validate_task_data(task_data, registry=self.registry())

    def plan_task(self, task_data: dict[str, Any]) -> list[dict[str, Any]]:
        task = parse_task(task_data)
        return plan_task(task, root=self.root)

    def run_task(
        self,
        task_data: dict[str, Any],
        *,
        dry_run: bool = False,
        approve: bool = False,
        adapter: str = "mock",
    ) -> dict[str, Any]:
        task: OperatorTask = parse_task(task_data)
        result = run_task(task, dry_run=dry_run, approve=approve, adapter=adapter, root=self.root)
        return result.to_dict()

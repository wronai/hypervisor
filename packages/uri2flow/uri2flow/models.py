from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class FlowStep:
    id: str | None
    uri: str
    payload: dict[str, Any] = field(default_factory=dict)
    after: list[str] = field(default_factory=list)
    condition: str | None = None
    operation: str | None = None
    kind: str | None = None


@dataclass
class FlowDocument:
    id: str
    description: str | None = None
    source_prompt: str | None = None
    steps: list[FlowStep] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        data: dict[str, Any] = {"flow": {"id": self.id}}
        if self.description:
            data["flow"]["description"] = self.description
        if self.source_prompt:
            data["flow"]["source_prompt"] = self.source_prompt
        data["do"] = []
        for step in self.steps:
            item: dict[str, Any] = {"uri": step.uri}
            if step.id:
                item["id"] = step.id
            if step.payload:
                item["with"] = step.payload
            if step.after:
                item["after"] = step.after[0] if len(step.after) == 1 else step.after
            if step.condition:
                item["if"] = step.condition
            if step.operation:
                item["operation"] = step.operation
            if step.kind:
                item["kind"] = step.kind
            data["do"].append(item)
        return data

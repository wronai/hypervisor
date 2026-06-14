from __future__ import annotations

from hypervisor.contract_registry.models import ContractRegistry


def build_capability_test_plan(registry: ContractRegistry) -> list[dict]:
    plan: list[dict] = []
    for cap in registry.capabilities:
        if cap.type == "resource_read":
            plan.append(
                {
                    "agent": cap.agent,
                    "capability": cap.name,
                    "kind": "resource_read",
                    "check": "uri_resolves_and_schema_matches",
                    "uri": cap.uri,
                    "expected_schema": cap.output_schema,
                }
            )
        elif cap.type == "command":
            plan.append(
                {
                    "agent": cap.agent,
                    "capability": cap.name,
                    "kind": "command",
                    "check": "command_has_input_schema_and_emitted_events",
                    "command": cap.command,
                    "input_schema": cap.input_schema,
                    "emits": cap.emits,
                }
            )
    return plan

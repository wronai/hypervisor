"""Capability verification test plans."""

from __future__ import annotations

from typing import Any

# Backward-compatible alias used during package extraction.
from uri2verify.capability_plan import build_capability_test_plan

__all__ = ["build_capability_test_plan"]


def capability_test_plan_from_registry(registry: Any) -> list[dict[str, Any]]:
    """Build plan from any registry object exposing ``capabilities``."""
    return build_capability_test_plan(registry.capabilities)

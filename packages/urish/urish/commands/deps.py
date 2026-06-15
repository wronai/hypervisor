from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class RuntimeCommandDeps:
    policy_options: Callable[..., Any]
    context_policy: Callable[[], str | None]
    emit: Callable[..., None]
    finish: Callable[..., None]

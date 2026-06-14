from __future__ import annotations

import importlib
from typing import Any

from uri2run.result import result_from_output
from uri3.results import ServiceResult


def split_python_uri(uri: str) -> tuple[str, str]:
    if not uri.startswith("python://"):
        raise ValueError(f"Expected python:// URI, got {uri}")
    ref = uri.removeprefix("python://")
    if ":" not in ref:
        raise ValueError("python backend target must be python://module:function")
    module, func = ref.split(":", 1)
    return module, func


def run_python(target: str, payload: dict[str, Any], context: dict[str, Any]) -> ServiceResult:
    module_name, func_name = split_python_uri(target)
    module = importlib.import_module(module_name)
    func = getattr(module, func_name)
    output = func(payload, context) if callable(func) else func
    return result_from_output(output)

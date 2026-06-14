from __future__ import annotations

import shlex
import subprocess
from typing import Any

from uri3.results import service_result


def _command_with_args(command: str, payload: dict[str, Any]) -> str:
    args = payload.get("args")
    if not isinstance(args, list):
        return command
    suffix = " ".join(shlex.quote(str(arg)) for arg in args)
    return f"{command} {suffix}".strip()


def run_shell(command: str, payload: dict[str, Any], context: dict[str, Any]):
    del context
    completed = subprocess.run(
        _command_with_args(command, payload),
        shell=True,
        text=True,
        capture_output=True,
        check=False,
    )
    return service_result(
        ok=completed.returncode == 0,
        result_type="shell",
        data={
            "stdout": completed.stdout,
            "stderr": completed.stderr,
            "returncode": completed.returncode,
        },
        meta={"transport": "shell"},
    )

from __future__ import annotations

import subprocess
from typing import Any

from touri.models import service_result


def call_shell_backend(command: str, payload: dict[str, Any], context: dict[str, Any]):
    completed = subprocess.run(command, shell=True, text=True, capture_output=True, check=False)
    return service_result(
        ok=completed.returncode == 0,
        result_type="shell",
        data={"stdout": completed.stdout, "stderr": completed.stderr, "returncode": completed.returncode},
    )

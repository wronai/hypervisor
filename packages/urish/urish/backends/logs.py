from __future__ import annotations

from typing import Any

from uri3.logs.reader import read_logs_result, summarize_logs


def read_log_uri(uri: str, *, root=None) -> dict[str, Any]:
    summary = summarize_logs(uri, root=root)
    entries = read_logs_result(uri, root=root)
    ok = bool(summary.get("exists", True))
    return {
        "ok": ok,
        "workflow_status": "completed",
        "execution_status": "completed",
        "service_result_status": "succeeded" if ok else "failed",
        "result_type": "logs",
        "data": {"summary": summary, "entries": entries},
        "meta": {"runtime": "uri3", "transport": "log", "target": uri},
    }

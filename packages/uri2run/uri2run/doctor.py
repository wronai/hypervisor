from __future__ import annotations

from typing import Any


def doctor_transport_dependencies() -> dict[str, Any]:
    checks: list[dict[str, Any]] = []

    def _import_check(transport: str, module: str, *, extra: str | None = None) -> None:
        try:
            __import__(module)
            checks.append({"id": transport, "ok": True, "missing": []})
        except ImportError as exc:
            item = {
                "id": transport,
                "ok": False,
                "missing": [module],
                "error": str(exc),
            }
            if extra:
                item["suggested_fix"] = [extra]
            checks.append(item)

    _import_check("python", "uri2run.transports.python_transport")
    _import_check("shell", "uri2run.transports.shell_transport")
    _import_check("http", "httpx")
    _import_check(
        "uri2ops_server",
        "uvicorn",
        extra='pip install -e "packages/uri2ops[server]"',
    )
    failed = [item for item in checks if not item.get("ok")]
    return {"ok": not failed, "transports": checks, "failed": len(failed)}

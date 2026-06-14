from __future__ import annotations

import json
import sys
from pathlib import Path

from hypervisor.contract_registry.cross_validator import validate_root
from hypervisor.contract_registry.loader import load_contract_registry
from hypervisor.contract_registry.registry_builder import write_registry_manifest
from hypervisor.contract_registry.registry_exporter import export_markdown
from hypervisor.contract_registry.schema_validator import validate_contract_files
from hypervisor.contract_registry.validate import validate_registry


def main(argv: list[str] | None = None) -> int:
    argv = argv or sys.argv[1:]
    command = "check"
    root_arg = "."
    if argv and argv[0] in {"check", "schema", "cross", "build", "export-md"}:
        command = argv[0]
        root_arg = argv[1] if len(argv) > 1 else "."
    elif argv:
        root_arg = argv[0]
    root = Path(root_arg)

    if command == "schema":
        results = validate_contract_files(root)
        failed = [r for r in results if not r.ok]
        for result in results:
            print(json.dumps({"path": result.path, "ok": result.ok, "errors": result.errors}, indent=2))
        return 1 if failed else 0

    if command == "cross":
        errors = validate_root(root)
        if errors:
            print("Cross-reference validation failed:")
            for error in errors:
                print(f"- {error}")
            return 1
        print("Cross-reference validation OK")
        return 0

    if command == "build":
        path = write_registry_manifest(root)
        print(f"Wrote {path}")
        return 0

    if command == "export-md":
        path = export_markdown(root)
        print(f"Wrote {path}")
        return 0

    # Full check: schema + previous logical validation + cross-reference validation.
    schema_results = validate_contract_files(root)
    schema_errors = [f"{r.path}: {e}" for r in schema_results for e in r.errors]
    registry = load_contract_registry(root)
    logical_errors = validate_registry(registry)
    cross_errors = validate_root(root)
    errors = schema_errors + logical_errors + cross_errors
    if errors:
        print("Contract registry validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    path = write_registry_manifest(root)
    summary = {
        "resources": len(registry.resources),
        "views": len(registry.views),
        "capabilities": len(registry.capabilities),
        "resolved_registry": str(path),
    }
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

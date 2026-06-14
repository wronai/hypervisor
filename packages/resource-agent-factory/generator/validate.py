from __future__ import annotations

import sys
from pathlib import Path

from generator.model import load_agent_spec


def validate_agent(path: Path) -> list[str]:
    errors: list[str] = []
    try:
        spec = load_agent_spec(path)
    except Exception as exc:  # noqa: BLE001
        return [f"{path}: cannot load spec: {exc}"]

    names = set()
    for cap in spec.capabilities:
        if cap.name in names:
            errors.append(f"{path}: duplicate capability name {cap.name}")
        names.add(cap.name)

        if cap.type == "resource_read":
            if not cap.uri:
                errors.append(f"{path}: {cap.name} resource_read requires uri")
            if not cap.output_schema:
                errors.append(f"{path}: {cap.name} resource_read requires output_schema")
            if not cap.renderer:
                errors.append(f"{path}: {cap.name} resource_read requires renderer")
        elif cap.type == "command":
            if not cap.command:
                errors.append(f"{path}: {cap.name} command capability requires command")
            if not cap.input_schema:
                errors.append(f"{path}: {cap.name} command capability requires input_schema")
        else:
            errors.append(f"{path}: {cap.name} unsupported type {cap.type}")

    return errors


def iter_agent_specs(root: Path) -> list[Path]:
    if root.is_file():
        return [root]
    return sorted((root / "agents").glob("*.yaml")) if (root / "agents").exists() else sorted(root.glob("*.yaml"))


def main(argv: list[str] | None = None) -> int:
    argv = argv or sys.argv[1:]
    root = Path(argv[0] if argv else "contracts")
    paths = iter_agent_specs(root)
    if not paths:
        print(f"No agent specs found under {root}")
        return 1

    all_errors: list[str] = []
    for path in paths:
        all_errors.extend(validate_agent(path))

    if all_errors:
        print("Contract validation failed:")
        for error in all_errors:
            print(f"- {error}")
        return 1

    print(f"Validated {len(paths)} agent spec(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

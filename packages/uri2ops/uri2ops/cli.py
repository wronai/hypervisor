from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import yaml

from uri2ops.operation_registry.loader import load_operation_registry
from uri2ops.operation_registry.validator import validate_operation_registry
from uri2ops.operator.runner import plan_task, run_task
from uri2ops.operator.task import load_task
from uri2ops.operator.validator import validate_task_file
from uri2ops.remote_registry.loader import list_remote_sources, resolve_operation_registry


def _print(data) -> None:
    print(yaml.safe_dump(data, sort_keys=False, allow_unicode=True))


def operations_cmd(args) -> int:
    registry = resolve_operation_registry()
    if args.action == "list":
        _print({"operations": [spec.to_dict() for spec in registry.list()]})
        return 0
    if args.action == "describe":
        spec = registry.require(args.scheme, args.operation)
        _print(spec.to_dict())
        return 0
    if args.action == "validate":
        errors = validate_operation_registry(registry)
        if errors:
            _print({"ok": False, "errors": errors})
            return 1
        _print({"ok": True})
        return 0
    raise SystemExit(f"Unknown operations action: {args.action}")


def registry_cmd(args) -> int:
    if args.action == "list":
        _print({"sources": list_remote_sources()})
        return 0
    if args.action == "validate":
        registry = resolve_operation_registry()
        errors = validate_operation_registry(registry)
        if errors:
            _print({"ok": False, "errors": errors})
            return 1
        _print({"ok": True, "operations": len(registry.list())})
        return 0
    raise SystemExit(f"Unknown registry action: {args.action}")


def validate_cmd(args) -> int:
    errors = validate_task_file(args.path)
    if errors:
        _print({"ok": False, "errors": errors})
        return 1
    _print({"ok": True, "path": args.path})
    return 0


def plan_cmd(args) -> int:
    task = load_task(args.path)
    _print({"task": task.id, "plan": plan_task(task)})
    return 0


def run_cmd(args) -> int:
    task = load_task(args.path)
    result = run_task(task, dry_run=args.dry_run, approve=args.approve, adapter=args.adapter)
    _print(result.to_dict())
    return 0 if result.ok else 2


def serve_cmd(args) -> int:
    try:
        import uvicorn
    except ImportError as exc:
        raise SystemExit("uvicorn is required for uri2ops serve: pip install uvicorn") from exc
    from uri2ops.server.app import create_app

    base_url = f"http://{args.host}:{args.port}"
    app = create_app(root=Path.cwd(), base_url=base_url)
    uvicorn.run(app, host=args.host, port=args.port, log_level="info")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="uri2ops")
    sub = parser.add_subparsers(dest="cmd", required=True)

    ops = sub.add_parser("operations")
    ops_sub = ops.add_subparsers(dest="action", required=True)
    ops_sub.add_parser("list")
    desc = ops_sub.add_parser("describe")
    desc.add_argument("scheme")
    desc.add_argument("operation")
    ops_sub.add_parser("validate")
    ops.set_defaults(func=operations_cmd)

    reg = sub.add_parser("registry")
    reg_sub = reg.add_subparsers(dest="action", required=True)
    reg_sub.add_parser("list")
    reg_sub.add_parser("validate")
    reg.set_defaults(func=registry_cmd)

    val = sub.add_parser("validate")
    val.add_argument("path")
    val.set_defaults(func=validate_cmd)

    plan = sub.add_parser("plan")
    plan.add_argument("path")
    plan.set_defaults(func=plan_cmd)

    run = sub.add_parser("run")
    run.add_argument("path")
    run.add_argument("--dry-run", action="store_true")
    run.add_argument("--approve", action="store_true")
    run.add_argument("--adapter", default="mock", choices=["mock", "playwright", "adb", "uia", "auto"])
    run.set_defaults(func=run_cmd)

    serve = sub.add_parser("serve", help="Run uri2ops HTTP daemon with A2A and MCP wrappers")
    serve.add_argument("--host", default="127.0.0.1")
    serve.add_argument("--port", type=int, default=8791)
    serve.set_defaults(func=serve_cmd)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())

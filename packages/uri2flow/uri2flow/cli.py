from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Sequence

from .expander import dump_yaml, expand_flow
from .parser import load_flow
from .validator import validate_flow


def cmd_validate(args: argparse.Namespace) -> int:
    warnings = validate_flow(args.path)
    payload = {"ok": True, "warnings": warnings}
    print(json.dumps(payload, ensure_ascii=False, indent=2) if args.json else dump_yaml(payload))
    return 0


def cmd_expand(args: argparse.Namespace) -> int:
    graph = expand_flow(args.path)
    output = json.dumps(graph, ensure_ascii=False, indent=2) if args.json else dump_yaml(graph)
    if args.out:
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        Path(args.out).write_text(output, encoding="utf-8")
    else:
        print(output)
    return 0


def cmd_print(args: argparse.Namespace) -> int:
    flow = load_flow(args.path)
    print(dump_yaml(flow.to_dict()))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="uri2flow", description="Compile compact URI flow YAML into workflow graph YAML")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("validate", help="validate compact *.uri.flow.yaml")
    p.add_argument("path")
    p.add_argument("--json", action="store_true")
    p.set_defaults(func=cmd_validate)

    p = sub.add_parser("expand", help="expand compact flow into full workflow graph")
    p.add_argument("path")
    p.add_argument("--out")
    p.add_argument("--json", action="store_true")
    p.set_defaults(func=cmd_expand)

    p = sub.add_parser("print", help="normalize and print compact flow")
    p.add_argument("path")
    p.set_defaults(func=cmd_print)

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())

from __future__ import annotations

import argparse
import json
from collections.abc import Sequence
from typing import Any

from urigen.apply import apply_ecosystem
from urigen.explain import explain_ecosystem
from urigen.generator import generate_ecosystem
from urigen.io import dump_yaml, write_yaml
from urigen.models import profile_catalog
from urigen.proposal import plan_ecosystem
from urigen.schema_check import schema_check_ecosystem
from urigen.verify import verify_ecosystem


def _emit(payload: dict[str, Any], *, json_out: bool) -> None:
    rendered = json.dumps(payload, indent=2, ensure_ascii=False) if json_out else dump_yaml(payload)
    print(rendered.rstrip())


def cmd_plan(args: argparse.Namespace) -> int:
    payload = plan_ecosystem(args.prompt, profile=args.profile, ecosystem_id=args.id or None)
    if args.out:
        write_yaml(args.out, payload)
    _emit(payload, json_out=args.json)
    return 0


def cmd_generate(args: argparse.Namespace) -> int:
    payload = generate_ecosystem(args.proposal, out=args.out)
    _emit(payload, json_out=args.json)
    return 0 if payload.get("ok") else 1


def cmd_verify(args: argparse.Namespace) -> int:
    payload = verify_ecosystem(args.ecosystem, write_report=not args.no_report)
    _emit(payload, json_out=args.json)
    return 0 if payload.get("ok") else 1


def cmd_explain(args: argparse.Namespace) -> int:
    payload = explain_ecosystem(args.ecosystem)
    _emit(payload, json_out=args.json)
    return 0


def cmd_apply(args: argparse.Namespace) -> int:
    payload = apply_ecosystem(
        args.ecosystem,
        approve=args.approve,
        plan_only=args.plan,
        rollback=args.rollback,
        root=args.root or None,
    )
    _emit(payload, json_out=args.json)
    return 0 if payload.get("ok") else 1


def cmd_schema_check(args: argparse.Namespace) -> int:
    payload = schema_check_ecosystem(args.path, root=args.root or None)
    _emit(payload, json_out=args.json)
    return 0 if payload.get("ok") else 1


def cmd_profiles(args: argparse.Namespace) -> int:
    payload = {"ok": True, "profiles": list(profile_catalog().values())}
    _emit(payload, json_out=args.json)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="urigen", description="URI Ecosystem Generator")
    sub = parser.add_subparsers(dest="cmd", required=True)

    plan = sub.add_parser("plan", help="create an ecosystem proposal")
    plan.add_argument("-p", "--prompt", required=True)
    plan.add_argument("--profile", default="minimal")
    plan.add_argument("--id", default="")
    plan.add_argument("--out", default="")
    plan.add_argument("--json", action="store_true")
    plan.set_defaults(func=cmd_plan)

    generate = sub.add_parser("generate", help="generate ecosystem artifacts")
    generate.add_argument("proposal")
    generate.add_argument("--out", required=True)
    generate.add_argument("--json", action="store_true")
    generate.set_defaults(func=cmd_generate)

    verify = sub.add_parser("verify", help="verify generated ecosystem artifacts")
    verify.add_argument("ecosystem")
    verify.add_argument("--json", action="store_true")
    verify.add_argument("--no-report", action="store_true")
    verify.set_defaults(func=cmd_verify)

    explain = sub.add_parser("explain", help="explain ecosystem dependencies and runtime path")
    explain.add_argument("ecosystem")
    explain.add_argument("--json", action="store_true")
    explain.set_defaults(func=cmd_explain)

    apply_cmd = sub.add_parser("apply", help="approval-gated apply plan")
    apply_cmd.add_argument("ecosystem")
    apply_cmd.add_argument("--approve", action="store_true")
    apply_cmd.add_argument(
        "--plan",
        action="store_true",
        help="Generate apply_plan.yaml and diff without mutating repo",
    )
    apply_cmd.add_argument(
        "--rollback",
        action="store_true",
        help="Rollback last apply using rollback/manifest.json",
    )
    apply_cmd.add_argument("--root", default="", help="Repository root for apply targets")
    apply_cmd.add_argument("--json", action="store_true")
    apply_cmd.set_defaults(func=cmd_apply)

    schema = sub.add_parser("schema", help="Check ecosystem YAML artifact envelopes")
    schema_sub = schema.add_subparsers(dest="schema_cmd", required=True)
    schema_check = schema_sub.add_parser(
        "check",
        help="Check $schema/kind/apiVersion/uri.self in ecosystem dir",
    )
    schema_check.add_argument("path")
    schema_check.add_argument("--root", default="")
    schema_check.add_argument("--json", action="store_true")
    schema_check.set_defaults(func=cmd_schema_check)

    profiles = sub.add_parser("profiles", help="list supported ecosystem profiles and aliases")
    profiles.add_argument("--json", action="store_true")
    profiles.set_defaults(func=cmd_profiles)

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())

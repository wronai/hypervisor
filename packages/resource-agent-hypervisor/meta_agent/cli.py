from __future__ import annotations

import argparse
from pathlib import Path

import yaml

from generator.validate import validate_agent
from generator.verify import verify_generated
from meta_agent.orchestrator import ROOT, asdict_result, pipeline_from_prompt, save_proposal_from_prompt, validate_repair_generate
from meta_agent.repair import repair_agent_spec


def main() -> int:
    parser = argparse.ArgumentParser(description="Meta-agent for creating, repairing, validating and generating resource agents.")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("plan", help="Create YAML proposal from natural-language prompt")
    p.add_argument("prompt")
    p.add_argument("--out", default=None)

    p = sub.add_parser("validate", help="Validate an agent YAML spec")
    p.add_argument("spec")

    p = sub.add_parser("repair", help="Repair common errors in agent YAML spec")
    p.add_argument("spec")
    p.add_argument("--write", action="store_true")

    p = sub.add_parser("generate", help="Validate, optionally repair and generate agent")
    p.add_argument("spec")
    p.add_argument("--no-repair", action="store_true")

    p = sub.add_parser("pipeline", help="Prompt -> YAML -> validate/repair -> generate -> verify")
    p.add_argument("prompt")
    p.add_argument("--out", default=None)
    p.add_argument("--no-repair", action="store_true")

    p = sub.add_parser("verify", help="Verify generated agents against contract hash")

    args = parser.parse_args()

    if args.cmd == "plan":
        path = save_proposal_from_prompt(args.prompt, Path(args.out) if args.out else None)
        print(path)
        print(path.read_text(encoding="utf-8"))
        return 0

    if args.cmd == "validate":
        errors = validate_agent(Path(args.spec))
        if errors:
            print("FAILED")
            for e in errors:
                print(f"- {e}")
            return 1
        print("OK")
        return 0

    if args.cmd == "repair":
        result = repair_agent_spec(Path(args.spec), write=args.write)
        print(yaml.safe_dump({
            "changed": result.changed,
            "errors_before": result.errors_before,
            "errors_after": result.errors_after,
            "warnings": result.warnings,
            "repaired_yaml": result.repaired_yaml,
        }, sort_keys=False, allow_unicode=True))
        return 0 if not result.errors_after else 1

    if args.cmd == "generate":
        result = validate_repair_generate(Path(args.spec), auto_repair=not args.no_repair)
        print(yaml.safe_dump(asdict_result(result), sort_keys=False, allow_unicode=True))
        return 0 if result.status == "generated" else 1

    if args.cmd == "pipeline":
        result = pipeline_from_prompt(args.prompt, output_path=Path(args.out) if args.out else None, auto_repair=not args.no_repair)
        print(yaml.safe_dump(asdict_result(result), sort_keys=False, allow_unicode=True))
        return 0 if result.status == "generated" else 1

    if args.cmd == "verify":
        errors = verify_generated(ROOT / "agents" / "generated")
        if errors:
            print("FAILED")
            for e in errors:
                print(f"- {e}")
            return 1
        print("OK")
        return 0

    return 1


if __name__ == "__main__":
    raise SystemExit(main())

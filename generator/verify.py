from __future__ import annotations

import re
import sys
from pathlib import Path

from generator.hashutil import file_sha256

HASH_RE = re.compile(r"Contract hash: (sha256:[a-f0-9]{64})")
SOURCE_RE = re.compile(r"Source: ([^\n]+)")


def verify_generated_agent(agent_dir: Path) -> list[str]:
    errors: list[str] = []
    main_file = agent_dir / "main.py"
    if not main_file.exists():
        return [f"{agent_dir}: missing main.py"]
    text = main_file.read_text(encoding="utf-8")
    source_match = SOURCE_RE.search(text)
    hash_match = HASH_RE.search(text)
    if not source_match or not hash_match:
        return [f"{agent_dir}: missing generated source/hash header"]

    source = Path(source_match.group(1))
    expected_hash = hash_match.group(1)
    if not source.exists():
        errors.append(f"{agent_dir}: source contract not found: {source}")
    elif file_sha256(source) != expected_hash:
        errors.append(f"{agent_dir}: contract_hash mismatch; regenerate agent")

    return errors



def verify_generated(root: Path) -> list[str]:
    agent_dirs = [p for p in root.iterdir() if p.is_dir()] if root.exists() else []
    errors: list[str] = []
    if not agent_dirs:
        return [f"No generated agents found in {root}"]
    for agent_dir in agent_dirs:
        errors.extend(verify_generated_agent(agent_dir))
    return errors


def main(argv: list[str] | None = None) -> int:
    argv = argv or sys.argv[1:]
    root = Path(argv[0] if argv else "agents/generated")
    agent_dirs = [p for p in root.iterdir() if p.is_dir()] if root.exists() else []
    if not agent_dirs:
        print(f"No generated agents found in {root}")
        return 1

    errors = verify_generated(root)

    if errors:
        print("Generated verification failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print(f"Verified {len(agent_dirs)} generated agent(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

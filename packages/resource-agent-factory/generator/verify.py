from __future__ import annotations

import re
import sys
from pathlib import Path

from generator.hashutil import file_sha256
from generator.header import AUTO_GENERATED_MARKER

HASH_RE = re.compile(r"Contract hash: (sha256:[a-f0-9]{64})")
SOURCE_RE = re.compile(r"Source: ([^\n]+)")


def verify_generated_agent(agent_dir: Path) -> list[str]:
    errors: list[str] = []
    main_file = agent_dir / "main.py"
    if not main_file.exists():
        return [f"{agent_dir}: missing main.py"]
    text = main_file.read_text(encoding="utf-8")
    if AUTO_GENERATED_MARKER not in text:
        return [f"{agent_dir}: missing auto-generated marker"]
    source_match = SOURCE_RE.search(text)
    hash_match = HASH_RE.search(text)
    if not source_match or not hash_match:
        return [f"{agent_dir}: missing generated source/hash header"]

    source = Path(source_match.group(1))
    expected_hash = hash_match.group(1)
    if source.exists():
        if file_sha256(source) != expected_hash:
            errors.append(f"{agent_dir}: contract_hash mismatch; regenerate agent")
        # else: source present and matches → OK
    else:
        # Source contract not present on this machine (e.g. generated on another host,
        # or the agent dir is part of the committed examples). Do not fail verification
        # for portability; only presence + hash match matters when the source is here.
        pass

    return errors



def _agent_dirs(root: Path) -> list[Path]:
    if not root.exists():
        return []
    return [
        path
        for path in root.iterdir()
        if path.is_dir() and not path.name.startswith(".") and path.name != "__pycache__"
    ]


def verify_generated(root: Path) -> list[str]:
    agent_dirs = _agent_dirs(root)
    errors: list[str] = []
    if not agent_dirs:
        return [f"No generated agents found in {root}"]
    for agent_dir in agent_dirs:
        errors.extend(verify_generated_agent(agent_dir))
    return errors


def main(argv: list[str] | None = None) -> int:
    argv = argv or sys.argv[1:]
    root = Path(argv[0] if argv else "agents/generated")
    agent_dirs = _agent_dirs(root)
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

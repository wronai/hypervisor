from __future__ import annotations

import os
import shlex
from typing import Callable

from urish.context import CONTEXT_ENV, load_context


def run_repl(*, execute: Callable[[list[str]], int]) -> int:
    ctx = os.environ.get(CONTEXT_ENV) or load_context().get("metadata", {}).get("id", "local-dev")
    policy = (load_context(ctx).get("spec") or {}).get("default_policy", "dev")
    prompt = f"uri[{ctx}|{policy}]> "
    while True:
        try:
            line = input(prompt).strip()
        except (EOFError, KeyboardInterrupt):
            print()
            return 0
        if not line:
            continue
        if line in {"exit", "quit", ":q"}:
            return 0
        if line.startswith("context use "):
            ctx = line.split(" ", 2)[2].strip()
            os.environ[CONTEXT_ENV] = ctx
            policy = (load_context(ctx).get("spec") or {}).get("default_policy", "dev")
            prompt = f"uri[{ctx}|{policy}]> "
            print(f"context: {ctx}")
            continue
        argv = shlex.split(line)
        code = execute(argv)
        if code not in {0, None}:
            print(f"exit code: {code}")

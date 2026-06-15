from __future__ import annotations

import os
import re
import shlex
from collections.abc import Callable
from dataclasses import dataclass

from urish.context import CONTEXT_ENV, load_context
from urish.policy import classify_uri

REPL_BANNER = """TellMesh URI shell — wpisz URI lub polecenie (exit / quit / :q aby wyjść).

Przykłady:
  health://agent/weather-map-agent.local
  view://process/agent/weather-map-agent.local/latest
  hypervisor://local/weather-agent/run
  workflow://weather_map/forecast/dry-run
  agent run weather-map-agent.local
  browser://chrome/page/open  (real mode dodaje --approve)

NL (język naturalny):
  ask zdiagnozuj agenta invoices-agent.local
  zdiagnozuj agenta invoices-agent.local

Meta:
  .help          — domyślny tryb (teraz: {mode})
  .dry-run on|off — przełącz dry-run / real
  .json / .text / .yaml — format odpowiedzi (.json = pełny envelope)
  context use <id> — przełącz kontekst
"""

_SHELL_OUTPUT_PREFIXES = (
    "fail ",
    "error:",
    "exit code:",
    "warning:",
    "traceback",
    "uri[",
)

_NL_HINT_WORDS = re.compile(
    r"\b("
    r"zdiagnozuj|napraw|pokaż|pokaz|sprawdź|sprawdz|uruchom|wystaw|wejdź|wejdz|"
    r"agenta|workflow|health|repair|invoice|faktur|pogod"
    r")\b",
    re.I,
)


@dataclass
class ReplState:
    dry_run: bool = False
    output: str = "text"
    policy: str = ""
    context_id: str = "local-dev"


def _known_commands() -> frozenset[str]:
    from urish.cli import _KNOWN_COMMANDS

    return _KNOWN_COMMANDS


def _line_has_uri(line: str) -> bool:
    return "://" in line


def _first_token(line: str) -> str:
    try:
        parts = shlex.split(line)
    except ValueError:
        return ""
    return parts[0] if parts else ""


# Meta command handlers: exact lowercased trigger -> (mutator, printer_or_none)
# Handlers return None to indicate "handled as meta (no argv)".
_META_HANDLERS: dict[str, Callable[[str, ReplState], None]] = {}


def _register_meta(trigger: str):
    def deco(fn: Callable[[str, ReplState], None]) -> Callable[[str, ReplState], None]:
        _META_HANDLERS[trigger] = fn
        return fn
    return deco


@_register_meta(".help")
@_register_meta("help")
@_register_meta("?")
def _meta_help(_raw: str, state: ReplState) -> None:
    print(REPL_BANNER.format(mode=_mode_label(state)))


@_register_meta(".dry-run on")
def _meta_dry_on(_raw: str, state: ReplState) -> None:
    state.dry_run = True
    print("dry-run: on")


@_register_meta(".dry-run off")
def _meta_dry_off(_raw: str, state: ReplState) -> None:
    state.dry_run = False
    print("dry-run: off")


@_register_meta(".json")
def _meta_json(_raw: str, state: ReplState) -> None:
    state.output = "json"
    print("output: json")


@_register_meta(".yaml")
def _meta_yaml(_raw: str, state: ReplState) -> None:
    state.output = "yaml"
    print("output: yaml")


@_register_meta(".text")
def _meta_text(_raw: str, state: ReplState) -> None:
    state.output = "text"
    print("output: text")


def _looks_like_shell_output(line: str) -> bool:
    stripped = line.strip()
    if not stripped:
        return False
    lowered = stripped.lower()
    if any(lowered.startswith(prefix) for prefix in _SHELL_OUTPUT_PREFIXES):
        return True
    if re.match(r"^(fail|ok|blocked)\b", lowered):
        return True
    if "blocked/" in lowered and "policy" in lowered:
        return True
    return False


def _looks_like_natural_language(line: str) -> bool:
    stripped = line.strip()
    if not stripped or "://" in stripped:
        return False
    if _looks_like_shell_output(stripped):
        return False
    lowered = stripped.lower()
    if lowered.startswith("ask "):
        return True
    if " " not in stripped:
        return False
    return _NL_HINT_WORDS.search(stripped) is not None


def _handle_context_use(stripped: str, state: ReplState) -> bool:
    if not stripped.lower().startswith("context use "):
        return False
    state.context_id = stripped.split(" ", 2)[2].strip()
    os.environ[CONTEXT_ENV] = state.context_id
    ctx = load_context(state.context_id)
    state.policy = (ctx.get("spec") or {}).get("default_policy", state.policy or "dev")
    print(f"context: {state.context_id} · policy: {state.policy}")
    return True


def parse_repl_line(line: str, state: ReplState) -> list[str] | None:
    """Parse one REPL line into CLI argv, or None when handled as meta-command."""
    stripped = line.strip()
    if not stripped:
        return None

    lowered = stripped.lower()
    handler = _META_HANDLERS.get(lowered)
    if handler:
        handler(stripped, state)
        return None

    if _handle_context_use(stripped, state):
        return None

    if _looks_like_shell_output(stripped):
        print("To wygląda na output terminala, nie polecenie. Wklej sam URI albo użyj: ask …")
        return None

    known = _known_commands()
    first = _first_token(stripped)

    if _line_has_uri(stripped) and first not in known:
        return _argv_for_uri_line(stripped, state)

    if first not in known and first not in {"exit", "quit", ":q"}:
        if _looks_like_natural_language(stripped):
            return _argv_for_ask(stripped, state)

    argv = shlex.split(stripped)
    return _apply_repl_defaults(argv, state)


def _argv_for_uri_line(line: str, state: ReplState) -> list[str]:
    try:
        parts = shlex.split(line)
    except ValueError:
        parts = [line]
    uri = next((part for part in parts if "://" in part), parts[0])
    extra = [part for part in parts if part != uri]
    argv = ["call", uri, *extra]
    return _apply_repl_defaults(argv, state)


def _argv_for_ask(prompt: str, state: ReplState) -> list[str]:
    argv = ["ask", prompt]
    if state.dry_run:
        argv.append("--dry-run")
    if state.output == "json":
        argv.append("--json")
    elif state.output == "yaml":
        argv.extend(["--output", "yaml"])
    return argv


def _mode_label(state: ReplState) -> str:
    return "dry-run" if state.dry_run else "real"


def _uri_implies_dry_run(uri: str) -> bool:
    parts = [part for part in uri.split("/") if part]
    return bool(parts) and parts[-1] == "dry-run"


def _append_flag_once(extras: list[str], flags: set[str], flag: str) -> None:
    if flag not in flags:
        extras.append(flag)
        flags.add(flag)


def _append_call_mutation_flags(
    extras: list[str],
    flags: set[str],
    *,
    state: ReplState,
    target_uri: str,
) -> None:
    if state.dry_run:
        if "--dry-run" not in flags and "--approve" not in flags:
            _append_flag_once(extras, flags, "--dry-run")
        return
    if (
        "--dry-run" not in flags
        and "--approve" not in flags
        and not _uri_implies_dry_run(target_uri)
        and classify_uri(target_uri) != "read"
    ):
        _append_flag_once(extras, flags, "--approve")


def _append_run_mutation_flags(extras: list[str], flags: set[str], *, state: ReplState) -> None:
    if state.dry_run:
        if "--dry-run" not in flags and "--approve" not in flags:
            _append_flag_once(extras, flags, "--dry-run")
        return
    if "--dry-run" not in flags and "--approve" not in flags:
        _append_flag_once(extras, flags, "--approve")


def _append_command_flags(
    extras: list[str],
    flags: set[str],
    *,
    command: str,
    state: ReplState,
    target_uri: str,
) -> None:
    if command == "call":
        _append_call_mutation_flags(extras, flags, state=state, target_uri=target_uri)
    elif command in {"ask", "nl"}:
        if state.dry_run:
            _append_flag_once(extras, flags, "--dry-run")
    elif command == "run":
        _append_run_mutation_flags(extras, flags, state=state)


def _append_output_flags(
    extras: list[str],
    flags: set[str],
    *,
    command: str,
    state: ReplState,
) -> None:
    if state.output == "json":
        _append_flag_once(extras, flags, "--json")
        return
    if state.output == "yaml" and "--output" not in flags:
        extras.extend(["--output", "yaml"])
        flags.add("--output")
        return
    if state.output == "text" and command in {"call", "plan", "explain", "run"}:
        if "--output" not in flags and "--json" not in flags:
            extras.extend(["--output", "text"])
            flags.add("--output")


def _append_policy_flag(extras: list[str], flags: set[str], *, state: ReplState) -> None:
    if state.policy and "--policy" not in flags:
        extras.extend(["--policy", state.policy])
        flags.add("--policy")


def _apply_repl_defaults(argv: list[str], state: ReplState) -> list[str]:
    if not argv:
        return argv
    command = argv[0]
    extras = list(argv[1:])
    flags = set(extras)
    target_uri = extras[0] if command in {"call", "run", "plan", "explain"} and extras else ""

    _append_command_flags(extras, flags, command=command, state=state, target_uri=str(target_uri))
    _append_output_flags(extras, flags, command=command, state=state)
    _append_policy_flag(extras, flags, state=state)

    return [command, *extras]


def run_repl(*, execute: Callable[[list[str]], int]) -> int:
    ctx = os.environ.get(CONTEXT_ENV) or load_context().get("metadata", {}).get("id", "local-dev")
    loaded = load_context(ctx)
    policy = (loaded.get("spec") or {}).get("default_policy", "dev")
    state = ReplState(dry_run=False, output="text", policy=policy, context_id=ctx)
    print(REPL_BANNER.format(mode=_mode_label(state)))

    prompt = f"uri[{state.context_id}|{state.policy}]> "
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

        argv = parse_repl_line(line, state)
        if argv is None:
            prompt = f"uri[{state.context_id}|{state.policy}]> "
            continue

        code = execute(argv)
        if code not in {0, None}:
            print(f"exit code: {code}")
        prompt = f"uri[{state.context_id}|{state.policy}]> "

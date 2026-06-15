from __future__ import annotations

from dataclasses import dataclass
from typing import Literal
from urllib.parse import urlparse

ActionKind = Literal["read", "mutation", "repair", "apply", "deploy"]
PolicyName = Literal["safe", "dev", "prod"]


@dataclass
class PolicyOptions:
    dry_run: bool = False
    approve: bool = False
    no_approve: bool = False
    readonly: bool = False
    sandbox: bool = False
    policy: PolicyName = "dev"

    @classmethod
    def from_flags(
        cls,
        *,
        dry_run: bool = False,
        approve: bool = False,
        no_approve: bool = False,
        readonly: bool = False,
        sandbox: bool = False,
        policy: str = "dev",
    ) -> PolicyOptions:
        selected = policy if policy in {"safe", "dev", "prod"} else "dev"
        return cls(
            dry_run=dry_run,
            approve=approve and not no_approve,
            no_approve=no_approve,
            readonly=readonly,
            sandbox=sandbox,
            policy=selected,  # type: ignore[arg-type]
        )


READ_SCHEMES = {
    "log",
    "health",
    "runtime",
    "readiness",
    "schema",
    "contract",
    "view",
    "explain",
    "http",
    "https",
    "resource",
    "artifact",
    "ticket",
    "incident",
    "proposal",
    "evolution",
    "file",
}
MUTATION_SCHEMES = {
    "shell",
    "bash",
    "zsh",
    "powershell",
    "cmd",
    "python",
    "docker",
    "ssh",
    "agent",
    "agent-factory",
    "workflow",
    "flow",
    "repair",
    "apply",
    "evolution",
    "ecosystem",
    "hypervisor",
}


def _path_has_any(path: str, tokens: tuple[str, ...]) -> bool:
    return any(token in path for token in tokens)


def _classify_repair(scheme: str, path: str) -> ActionKind | None:
    if scheme == "repair" and _path_has_any(path, ("/diagnose", "/plan")):
        return "read"
    if scheme == "repair" or _path_has_any(path, ("/repair", "/apply")):
        return "repair"
    return None


def _classify_apply(scheme: str, path: str) -> ActionKind | None:
    if scheme in {"evolution", "ecosystem"} and _path_has_any(path, ("apply", "deploy")):
        return "apply"
    return None


def _classify_hypervisor_mutation(scheme: str, path: str) -> ActionKind | None:
    if scheme == "hypervisor" and _path_has_any(path, ("/run", "/stop", "/restart")):
        return "mutation"
    return None


def _classify_physical_operator(scheme: str, path: str) -> ActionKind | None:
    if scheme not in {"robot", "device"}:
        return None
    if _path_has_any(
        path,
        (
            "/move",
            "/stop",
            "/start",
            "/mission",
            "/write",
            "/set",
            "/reset",
            "/enable",
            "/disable",
            "/dock",
            "/undock",
            "/home",
        ),
    ):
        return "mutation"
    return "read"


def _classify_desktop_operator(scheme: str, path: str) -> ActionKind | None:
    if scheme not in {"browser", "screen", "input", "pcwin", "android"}:
        return None
    if _path_has_any(
        path,
        (
            "/open",
            "/click",
            "/type",
            "/tap",
            "/focus",
            "/submit",
            "/write",
            "/set",
            "/run",
            "/start",
        ),
    ):
        return "mutation"
    return "read"


def _classify_read(scheme: str, path: str, parsed) -> ActionKind | None:
    if scheme not in READ_SCHEMES or _path_has_any(path, ("/apply", "/run", "/create")):
        return None
    if scheme in {"http", "https"} and parsed.query and "method=POST" in parsed.query.upper():
        return "mutation"
    return "read"


def _classify_mutation_scheme(scheme: str, path: str) -> ActionKind | None:
    if scheme in MUTATION_SCHEMES:
        return "mutation"
    return None


def classify_uri(uri: str) -> ActionKind:
    parsed = urlparse(uri)
    scheme = (parsed.scheme or "").lower()
    path = (parsed.path or "").lower()
    for classifier in (
        lambda: _classify_repair(scheme, path),
        lambda: _classify_apply(scheme, path),
        lambda: _classify_hypervisor_mutation(scheme, path),
        lambda: _classify_physical_operator(scheme, path),
        lambda: _classify_desktop_operator(scheme, path),
        lambda: _classify_read(scheme, path, parsed),
        lambda: _classify_mutation_scheme(scheme, path),
    ):
        result = classifier()
        if result is not None:
            return result
    return "read"


def evaluate_policy(
    uri: str,
    *,
    options: PolicyOptions,
    context_policy: str | None = None,
) -> tuple[bool, str | None, bool]:
    """Return (allowed, reason, force_dry_run)."""
    action = classify_uri(uri)
    effective = options.policy
    if context_policy in {"safe", "dev", "prod"}:
        effective = context_policy  # type: ignore[assignment]

    if options.readonly and action != "read":
        return False, "readonly mode blocks mutations", False

    if action == "read":
        return True, None, False

    if options.dry_run:
        return True, None, True

    if action in {"repair", "apply", "deploy"}:
        if options.approve:
            return True, None, False
        if effective == "safe":
            return False, f"{action} requires --dry-run under policy=safe", False
        if effective == "prod":
            return False, f"{action} requires --approve under policy=prod", False
        return False, f"{action} requires --dry-run or --approve under policy=dev", False

    if action == "mutation":
        if options.approve:
            return True, None, False
        if effective == "safe":
            return False, "mutation blocked under policy=safe (use --dry-run)", False
        if effective == "prod":
            return False, "mutation requires --approve under policy=prod", False
        return False, "mutation requires --dry-run by default under policy=dev", False

    return True, None, False

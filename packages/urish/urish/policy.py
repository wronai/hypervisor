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


def classify_uri(uri: str) -> ActionKind:
    parsed = urlparse(uri)
    scheme = (parsed.scheme or "").lower()
    path = (parsed.path or "").lower()

    if scheme == "repair" or _path_has_any(path, ("/repair", "/apply")):
        return "repair"
    if scheme in {"evolution", "ecosystem"} and _path_has_any(path, ("apply", "deploy")):
        return "apply"
    if scheme == "hypervisor" and _path_has_any(path, ("/run", "/stop", "/restart")):
        return "mutation"
    if scheme in READ_SCHEMES and not _path_has_any(path, ("/apply", "/run", "/create")):
        if scheme in {"http", "https"} and parsed.query and "method=POST" in parsed.query.upper():
            return "mutation"
        return "read"
    if scheme in MUTATION_SCHEMES:
        return "mutation"
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

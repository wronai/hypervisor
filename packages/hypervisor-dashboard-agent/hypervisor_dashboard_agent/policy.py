from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from urish.policy import PolicyOptions, evaluate_policy


@dataclass
class ApprovalDecision:
    allowed: bool
    reason: str | None
    force_dry_run: bool
    requires_approval: bool


def decision_for_uri(
    uri: str,
    *,
    approved: bool = False,
    dry_run: bool = False,
    readonly: bool = False,
    policy: str = "dev",
) -> ApprovalDecision:
    options = PolicyOptions.from_flags(
        dry_run=dry_run,
        approve=approved,
        readonly=readonly,
        policy=policy,
    )
    allowed, reason, force_dry_run = evaluate_policy(uri, options=options)
    requires_approval = not allowed and reason is not None and "requires" in (reason or "")
    return ApprovalDecision(
        allowed=allowed,
        reason=reason,
        force_dry_run=force_dry_run,
        requires_approval=requires_approval or (not allowed and not dry_run and not approved),
    )


def preview_action(uri: str, *, policy: str = "dev") -> dict[str, Any]:
    read_decision = decision_for_uri(uri, readonly=False, policy=policy)
    approve_decision = decision_for_uri(uri, approved=True, policy=policy)
    return {
        "uri": uri,
        "readonly_allowed": read_decision.allowed and not read_decision.force_dry_run,
        "dry_run_allowed": decision_for_uri(uri, dry_run=True, policy=policy).allowed,
        "execute_allowed_with_approval": approve_decision.allowed,
        "requires_approval": approve_decision.requires_approval or not read_decision.allowed,
        "policy": policy,
        "reason": read_decision.reason,
    }

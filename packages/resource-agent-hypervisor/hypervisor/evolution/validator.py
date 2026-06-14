from __future__ import annotations

from hypervisor.evolution.models import EvolutionProposal


def validate_proposal(proposal: EvolutionProposal) -> list[str]:
    errors: list[str] = []
    if not proposal.proposal_id:
        errors.append("proposal_id is required")
    if proposal.type not in {"new_agent", "add_capability", "add_resource", "change"}:
        errors.append(f"unsupported proposal type: {proposal.type}")
    if not proposal.reason:
        errors.append("reason is required")
    if proposal.compatibility.get("breaking_change") and not proposal.compatibility.get("requires_approval"):
        errors.append("breaking changes must set compatibility.requires_approval=true")
    return errors

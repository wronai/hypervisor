from hypervisor.policy_gate.gate import evaluate_change


def test_policy_gate_allows_non_breaking_change():
    decision = evaluate_change({"breaking_change": False})
    assert decision.allowed is True
    assert decision.requires_approval is False


def test_policy_gate_blocks_breaking_change_without_approval():
    decision = evaluate_change({"breaking_change": True, "removed_resources": ["resource://users/{id}"]})
    assert decision.allowed is False
    assert decision.requires_approval is True


def test_policy_gate_allows_breaking_change_with_approval():
    decision = evaluate_change({"breaking_change": True}, approved=True)
    assert decision.allowed is True

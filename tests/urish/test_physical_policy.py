from __future__ import annotations

from urish.policy import PolicyOptions, classify_uri, evaluate_policy


def test_physical_operator_policy_distinguishes_reads_and_mutations():
    assert classify_uri("robot://robot/amr-1/state") == "read"
    assert classify_uri("device://device/sensor-1/status") == "read"
    assert classify_uri("device://device/sensor-1/read") == "read"

    assert classify_uri("robot://robot/amr-1/move") == "mutation"
    assert classify_uri("robot://robot/amr-1/mission/patrol/start") == "mutation"
    assert classify_uri("device://device/relay-1/write") == "mutation"


def test_physical_mutations_default_to_real_in_dev_policy():
    allowed, reason, force_dry_run = evaluate_policy(
        "robot://robot/amr-1/move",
        options=PolicyOptions(policy="dev"),
    )
    assert allowed is True
    assert reason is None
    assert force_dry_run is False

    allowed, reason, force_dry_run = evaluate_policy(
        "robot://robot/amr-1/move",
        options=PolicyOptions(no_approve=True, policy="dev"),
    )
    assert allowed is False
    assert "no-approve" in (reason or "").lower()
    assert force_dry_run is False

    allowed, reason, force_dry_run = evaluate_policy(
        "robot://robot/amr-1/move",
        options=PolicyOptions(dry_run=True, policy="dev"),
    )
    assert allowed is True
    assert reason is None
    assert force_dry_run is True

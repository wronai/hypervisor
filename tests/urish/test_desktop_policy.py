from __future__ import annotations

from urish.policy import PolicyOptions, classify_uri, evaluate_policy


def test_desktop_operator_policy_distinguishes_reads_and_mutations():
    assert classify_uri("screen://desktop/observe") == "read"
    assert classify_uri("browser://chrome/page/active/dom") == "read"
    assert classify_uri("browser://chrome/page/active/screenshot") == "read"
    assert classify_uri("android://device/test/screenshot") == "read"
    assert classify_uri("android://device/test/dump_ui") == "read"

    assert classify_uri("browser://chrome/page/open") == "mutation"
    assert classify_uri("browser://chrome/page/active/click") == "mutation"
    assert classify_uri("input://keyboard/type") == "mutation"
    assert classify_uri("pcwin://window/main/focus") == "mutation"
    assert classify_uri("pcwin://control/submit/click") == "mutation"
    assert classify_uri("android://device/test/tap") == "mutation"


def test_desktop_mutations_default_to_real_in_dev_policy():
    allowed, reason, force_dry_run = evaluate_policy(
        "browser://chrome/page/open",
        options=PolicyOptions(policy="dev"),
    )
    assert allowed is True
    assert reason is None
    assert force_dry_run is False

    allowed, reason, force_dry_run = evaluate_policy(
        "browser://chrome/page/open",
        options=PolicyOptions(no_approve=True, policy="dev"),
    )
    assert allowed is False
    assert "no-approve" in (reason or "").lower()
    assert force_dry_run is False

    allowed, reason, force_dry_run = evaluate_policy(
        "browser://chrome/page/open",
        options=PolicyOptions(dry_run=True, policy="dev"),
    )
    assert allowed is True
    assert reason is None
    assert force_dry_run is True

    allowed, reason, force_dry_run = evaluate_policy(
        "input://keyboard/type",
        options=PolicyOptions(approve=True, policy="prod"),
    )
    assert allowed is True
    assert reason is None
    assert force_dry_run is False

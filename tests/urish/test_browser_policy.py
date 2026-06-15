from __future__ import annotations

from urish.policy import PolicyOptions, classify_uri, evaluate_policy


def test_browser_operator_policy_distinguishes_reads_and_mutations():
    assert classify_uri("browser://chrome/page/active/dom") == "read"
    assert classify_uri("browser://chrome/page/active/screenshot") == "read"
    assert classify_uri("browser://chrome/page/open") == "mutation"
    assert classify_uri("browser://chrome/page/active/click") == "mutation"


def test_browser_mutations_default_to_real_in_dev_policy():
    allowed, reason, force_dry_run = evaluate_policy(
        "browser://chrome/page/open",
        options=PolicyOptions(policy="dev"),
    )
    assert allowed is True
    assert reason is None
    assert force_dry_run is False

from hypervisor.contract_registry.loader import load_contract_registry
from hypervisor.verifier.capability_tests import build_capability_test_plan


def test_capability_test_plan_is_built_from_registry():
    registry = load_contract_registry(".")
    plan = build_capability_test_plan(registry)
    names = {item["capability"] for item in plan}
    assert "read_user" in names
    assert "create_user" in names

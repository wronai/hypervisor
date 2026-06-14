from hypervisor.contract_registry.loader import load_contract_registry
from hypervisor.contract_registry.validate import validate_registry


def test_contract_registry_loads_and_validates():
    registry = load_contract_registry(".")
    assert len(registry.resources) >= 2
    assert len(registry.views) >= 2
    assert len(registry.capabilities) >= 4
    assert validate_registry(registry) == []


def test_user_read_capability_matches_resource_contract():
    registry = load_contract_registry(".")
    cap = registry.capability_by_name("user-agent", "read_user")
    assert cap is not None
    res = registry.resource_by_uri(cap.uri)
    assert res is not None
    assert cap.output_schema == res.schema
    assert cap.renderer == res.renderer

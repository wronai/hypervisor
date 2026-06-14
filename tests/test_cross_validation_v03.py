from hypervisor.contract_registry.cross_validator import validate_root


def test_cross_validation_ok():
    assert validate_root('.') == []

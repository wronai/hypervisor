from hypervisor.contract_registry.schema_validator import validate_contract_files


def test_schema_validation_ok():
    results = validate_contract_files('.')
    assert results
    assert all(r.ok for r in results), [r for r in results if not r.ok]

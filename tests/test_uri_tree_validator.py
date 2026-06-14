from uri3.validators.uri_tree_validator import validate_uri_tree

def test_uri_tree_schema_ok():
    assert validate_uri_tree("domains/weather_map/uri_tree.yaml") == []

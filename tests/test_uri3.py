from uri3.validators.uri_validator import validate_uri
from uri3.graph.uri_graph import build_graph_from_tree

def test_validate_uri():
    assert validate_uri("llm://openrouter/qwen/qwen3-coder-next")
    assert validate_uri("env://OPENROUTER_API_KEY")

def test_graph_weather_tree():
    g = build_graph_from_tree("domains/weather_map/uri_tree.yaml")
    assert "domain://weather-map" in g.nodes
    assert any(n.kind == "agent" for n in g.nodes.values())

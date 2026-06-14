from nl2uri.planner import rule_based_plan

def test_weather_prompt_generates_weather_uri_tree():
    result = rule_based_plan("generuj mape pogody dwa tygodnie do przodu w html")
    tree = result.tree
    assert tree["domain"]["id"] == "weather_map"
    assert tree["inputs"]["days"]["default"] == 14
    assert "html_map" in tree["resources"]
    assert tree["agent"]["id"] == "weather-map-agent"

from pathlib import Path

from meta_agent.domain_planner.llm_planner import plan_domain_from_prompt
from meta_agent.domain_planner.domain_pack_generator import generate_domain_pack_from_tree


def test_weather_prompt_generates_uri_tree():
    tree = plan_domain_from_prompt("generuj mape pogody dwa tygodnie do przodu w html", use_llm=False)
    assert tree["domain"]["id"] == "weather_map"
    assert tree["inputs"]["days"]["default"] == 14
    assert "html_map" in tree["resources"]
    assert tree["resources"]["html_map"]["renderer_ref"] == "html"


def test_domain_pack_generation(tmp_path):
    tree = plan_domain_from_prompt("generuj mape pogody dwa tygodnie do przodu w html", use_llm=False)
    files = generate_domain_pack_from_tree(tree, tmp_path / "weather_map")
    assert Path(files["uri_tree"]).exists()
    assert Path(files["resources"]).exists()
    assert Path(files["agent_contract"]).exists()

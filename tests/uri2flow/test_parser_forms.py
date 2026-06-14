from uri2flow.parser import parse_flow


def test_accepts_string_and_mapping_forms():
    flow = parse_flow({
        "flow": {"id": "x"},
        "do": [
            "agent://a",
            {"browser://chrome/page/open": {"url": "http://x"}},
            {"id": "read", "uri": "http://x", "after": "open"},
        ]
    })
    assert len(flow.steps) == 3
    assert flow.steps[1].payload["url"] == "http://x"
    assert flow.steps[2].after == ["open"]

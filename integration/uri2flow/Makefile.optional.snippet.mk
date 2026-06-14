# Optional Makefile targets for uri2flow. Append manually if useful.

uri2flow-test:
	pytest tests/uri2flow -q

uri2flow-validate:
	uri2flow validate examples/15_compact_uri_flow/weather.uri.flow.yaml

uri2flow-expand:
	mkdir -p output
	uri2flow expand examples/15_compact_uri_flow/weather.uri.flow.yaml --out output/weather.uri.graph.yaml

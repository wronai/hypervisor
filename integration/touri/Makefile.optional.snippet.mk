.PHONY: touri-test touri-demo

touri-test:
	pytest tests/touri -q

touri-demo:
	pip install -e packages/touri
	touri validate examples/20_touri_capabilities/weather_forecast.uri.capability.yaml
	touri call weather://forecast/Gdansk/14/html --registry examples/20_touri_capabilities

from dataclasses import dataclass
import re
@dataclass
class PlanResult:
    tree: dict
    used_llm: bool = False

def _slug(text):
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9ąćęłńóśźż]+", "-", text)
    return text.strip("-") or "generated-domain"

def rule_based_plan(prompt: str) -> PlanResult:
    lower = prompt.lower()
    is_weather = any(w in lower for w in ["pogod", "weather", "forecast", "mapa pogody"])
    wants_html = "html" in lower or "url" in lower or "adres" in lower
    days = 14 if "dwa tyg" in lower or "2 tyg" in lower else 7
    if is_weather:
        tree = {
            "domain": {"id":"weather_map","uri":"domain://weather-map","description":"Generate weather forecast map as HTML URL."},
            "inputs": {"place":{"uri":"input://weather-map/place","type":"string","required":True},"days":{"uri":"input://weather-map/days","type":"integer","default":days},"forecast_model":{"uri":"input://weather-map/forecast-model","type":"string","default":"auto"}},
            "models": {"planner":{"uri":"llm://openrouter/qwen/qwen3-coder-next","api_key_uri":"env://OPENROUTER_API_KEY"}},
            "commands": {"generate_weather_map":{"uri":"command://weather-map/generate","handler_uri":"python://domains.weather_map.handlers.generate_weather_map:handler","input_schema_ref":"app.weather.v1.GenerateWeatherMapCommand","emits":["event://weather-map/WeatherMapGenerationRequested","event://weather-map/WeatherMapGenerated"]}},
            "events": {"generation_requested":{"uri":"event://weather-map/WeatherMapGenerationRequested","schema_ref":"app.weather.v1.WeatherMapGenerationRequested"},"generated":{"uri":"event://weather-map/WeatherMapGenerated","schema_ref":"app.weather.v1.WeatherMapGenerated"}},
            "resources": {"forecast":{"uri_template":"resource://weather/forecast/{place}/{days}","schema_ref":"app.weather.v1.ForecastDataView","renderer_ref":"json"},"html_map":{"uri_template":"resource://weather/maps/{place}/forecast/{days}","schema_ref":"app.weather.v1.WeatherMapHtmlView","renderer_ref":"html" if wants_html else "json"}},
            "artifacts": {"html":{"uri_template":"artifact://weather-map/{place}/forecast/{days}/index.html","mime_type":"text/html","public_url_template":"http://localhost:8000/artifacts/weather-map/{place}/forecast/{days}/index.html"}},
            "agent": {"id":"weather-map-agent","uri":"agent://weather-map-agent","card_uri":"a2a://weather-map-agent/.well-known/agent-card.json","capabilities":[{"name":"generate_weather_map","uri":"a2a://weather-map-agent/skills/generate_weather_map"},{"name":"read_weather_map","uri":"a2a://weather-map-agent/skills/read_weather_map"}]},
            "deployment": {"default":{"uri":"local://agents/generated/weather_map_agent"}}
        }
        return PlanResult(tree)
    slug = _slug(prompt[:50])
    return PlanResult({"domain":{"id":slug.replace('-','_'),"uri":f"domain://{slug}","description":prompt},"commands":{},"resources":{},"agent":{"id":f"{slug}-agent","uri":f"agent://{slug}-agent","capabilities":[]}})

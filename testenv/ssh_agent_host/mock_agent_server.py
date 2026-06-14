#!/usr/bin/env python3
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs

AGENT_CARD = {
    "name": "remote-weather-map-agent",
    "version": "0.1.0",
    "description": "Mock A2A-ready agent running inside the SSH test container.",
    "url": "http://localhost:8101",
    "capabilities": [
        {"name": "read_weather_map", "type": "resource_read", "uri": "resource://weather/maps/{place}/forecast/{days}"},
        {"name": "generate_weather_map", "type": "command", "command": "GenerateWeatherMap"}
    ],
    "generated_from": {
        "domain": "domain://weather-map",
        "agent": "agent://weather-map-agent",
        "contract_hash": "dev-sha256-placeholder"
    }
}

class Handler(BaseHTTPRequestHandler):
    def _json(self, payload, status=200):
        data = json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == "/health":
            return self._json({"ok": True, "service": "remote-weather-map-agent"})
        if parsed.path in {"/.well-known/agent-card.json", "/.well-known/agent.json"}:
            return self._json(AGENT_CARD)
        if parsed.path == "/capabilities":
            return self._json({"capabilities": AGENT_CARD["capabilities"]})
        if parsed.path == "/resources/read":
            qs = parse_qs(parsed.query)
            uri = qs.get("uri", [""])[0]
            return self._json({
                "ok": True,
                "uri": uri,
                "mime_type": "text/html",
                "data": {
                    "html_url": "http://localhost:8101/artifacts/weather-map/demo/index.html",
                    "note": "Mock resource response from SSH test container"
                }
            })
        return self._json({"ok": False, "error": "not_found", "path": parsed.path}, status=404)

    def log_message(self, fmt, *args):
        print("mock-agent:", fmt % args)

if __name__ == "__main__":
    HTTPServer(("0.0.0.0", 8101), Handler).serve_forever()

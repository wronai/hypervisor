from __future__ import annotations

import hashlib
from datetime import datetime, timezone


def handler(payload: dict) -> dict:
    place = payload.get("place", "unknown")
    days = int(payload.get("days", 14))
    model = payload.get("forecast_model") or payload.get("model") or "auto"
    html = (
        "<!doctype html><html><head><meta charset='utf-8'>"
        f"<title>Weather map {place}</title></head><body>"
        f"<h1>Weather map: {place}</h1><p>Forecast horizon: {days} days</p>"
        f"<p>Model: {model}</p><div id='map'>Generated placeholder map view.</div>"
        "</body></html>"
    )
    digest = hashlib.sha256(html.encode("utf-8")).hexdigest()
    url = f"/artifacts/weather-map/{place}/forecast/{days}/index.html"
    return {
        "ok": True,
        "place": place,
        "days": days,
        "model": model,
        "html_url": url,
        "html_content_hash": digest,
        "mime_type": "text/html",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "html": html,
    }

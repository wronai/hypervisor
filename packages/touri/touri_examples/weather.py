def handler(payload, context):
    place = payload.get("place", "Gdansk")
    days = int(payload.get("days", 14))
    return {
        "ok": True,
        "result_type": "artifact",
        "data": {
            "place": place,
            "days": days,
            "html_url": f"http://localhost:8000/artifacts/weather/{place}/{days}/index.html",
        },
        "artifact_uri": f"artifact://weather/{place}/{days}/index.html",
        "meta": {"demo": True},
    }

import httpx
class HttpResolver:
    scheme = "http"
    def resolve(self, uri):
        r = httpx.get(uri, timeout=10)
        r.raise_for_status()
        return r.json() if "json" in r.headers.get("content-type", "") else r.text

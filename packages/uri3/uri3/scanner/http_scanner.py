import httpx
from uri3.scanner.base import ScanItem
KNOWN_PATHS = ["/health", "/capabilities", "/.well-known/agent-card.json", "/.well-known/agent.json"]

def scan_http(base_url: str):
    base = base_url.rstrip("/")
    found = []
    for path in KNOWN_PATHS:
        uri = base + path
        try:
            r = httpx.get(uri, timeout=3)
            kind = "agent_card" if "agent" in path else path.strip("/") or "root"
            found.append(ScanItem(uri, kind, "reachable" if r.status_code < 500 else "error", {"status_code": r.status_code}))
        except Exception as e:
            found.append(ScanItem(uri, "endpoint", "unreachable", {"error": str(e)}))
    return found

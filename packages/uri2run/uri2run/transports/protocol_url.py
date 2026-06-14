from __future__ import annotations

from urllib.parse import urlparse


def protocol_to_http_url(uri: str) -> str:
    """Map mcp:// or a2a:// runtime URIs to an HTTP endpoint base."""
    parsed = urlparse(uri)
    if parsed.scheme not in {"mcp", "a2a"}:
        raise ValueError(f"Not a protocol runtime URI: {uri}")
    if not parsed.netloc:
        raise ValueError(f"{parsed.scheme}:// URI requires host[:port]")
    path = parsed.path or ""
    return f"http://{parsed.netloc}{path}"

from uri3.protocols.parser import parse_uri
from uri3.scanner.http_scanner import scan_http

def scan(uri: str):
    if parse_uri(uri).scheme in {"http", "https"}:
        return scan_http(uri)
    return []

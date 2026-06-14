import os
from uri3.protocols.parser import parse_uri

class EnvResolver:
    scheme = "env"
    def resolve(self, uri):
        p = parse_uri(uri)
        key = p.netloc or p.path.lstrip("/")
        if key not in os.environ:
            raise KeyError(f"Missing environment variable: {key}")
        return os.environ[key]

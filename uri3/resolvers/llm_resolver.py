from dataclasses import dataclass
from uri3.protocols.parser import parse_uri

@dataclass
class LLMRef:
    provider: str
    model: str
    raw_uri: str

class LLMResolver:
    scheme = "llm"
    def resolve(self, uri) -> LLMRef:
        p = parse_uri(uri)
        return LLMRef(provider=p.netloc, model=p.path.lstrip("/"), raw_uri=uri)

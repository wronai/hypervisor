from uri3.protocols.parser import parse_uri
from uri3.resolvers.env_resolver import EnvResolver
from uri3.resolvers.llm_resolver import LLMResolver
from uri3.resolvers.python_resolver import PythonResolver
from uri3.resolvers.http_resolver import HttpResolver

class Uri3Router:
    def __init__(self):
        self.resolvers = {"env": EnvResolver(), "llm": LLMResolver(), "python": PythonResolver(), "http": HttpResolver(), "https": HttpResolver()}
    def resolve(self, uri):
        scheme = parse_uri(uri).scheme
        resolver = self.resolvers.get(scheme)
        if not resolver:
            return {"uri": uri, "scheme": scheme, "status": "unresolved", "reason": "resolver_not_registered"}
        return resolver.resolve(uri)
    def call(self, uri, payload=None):
        scheme = parse_uri(uri).scheme
        resolver = self.resolvers.get(scheme)
        if not resolver or not hasattr(resolver, "call"):
            raise ValueError(f"Resolver for {scheme} does not support call")
        return resolver.call(uri, payload)

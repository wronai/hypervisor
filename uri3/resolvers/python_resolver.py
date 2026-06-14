import importlib
from uri3.protocols.parser import parse_uri

class PythonResolver:
    scheme = "python"
    def resolve(self, uri):
        p = parse_uri(uri)
        ref = (p.netloc + p.path).replace("/", ".")
        module_name, _, attr = ref.partition(":")
        if not attr:
            raise ValueError("python:// URI must end with :attribute")
        return getattr(importlib.import_module(module_name), attr)
    def call(self, uri, payload=None):
        return self.resolve(uri)(payload or {})

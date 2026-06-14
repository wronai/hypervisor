from __future__ import annotations

from uri3.graph.uri_graph import build_graph_from_tree
from uri3.logs.reader import read_logs, summarize_logs
from uri3.resolvers.router import Uri3Router, UriResolution, call, resolve
from uri3.scanner.scanner import scan
from nl2uri.planner import rule_based_plan


class Uri3Client:
    """Thin hypervisor adapter over uri3 routing, scanning and graph utilities."""

    def __init__(self):
        self.router = Uri3Router()

    def resolve(self, uri: str) -> UriResolution | dict:
        return self.router.resolve(uri)

    def call(self, uri: str, payload: dict | None = None):
        return self.router.call(uri, payload)

    def scan(self, uri: str):
        return scan(uri)

    def logs(self, uri: str, *, summary: bool = False):
        return summarize_logs(uri) if summary else read_logs(uri)

    def graph(self, path: str):
        return build_graph_from_tree(path)

    def nl2uri(self, prompt: str):
        return rule_based_plan(prompt).tree

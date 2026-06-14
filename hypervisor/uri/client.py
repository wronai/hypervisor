from uri3.resolvers.router import Uri3Router
from uri3.scanner.scanner import scan
from uri3.graph.uri_graph import build_graph_from_tree
from nl2uri.planner import rule_based_plan
class Uri3Client:
    def __init__(self): self.router = Uri3Router()
    def resolve(self, uri): return self.router.resolve(uri)
    def scan(self, uri): return scan(uri)
    def graph(self, path): return build_graph_from_tree(path)
    def nl2uri(self, prompt): return rule_based_plan(prompt).tree

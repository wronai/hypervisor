#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"

"${PYTHON:-python3}" - <<'PY'
import http.server
import socket
import tempfile
import threading
from pathlib import Path

import yaml

host = "127.0.0.1"
sock = socket.socket()
sock.bind((host, 0))
port = sock.getsockname()[1]
sock.close()


class Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.end_headers()
        self.wfile.write(b"<html><body>ok</body></html>")

    def log_message(self, format, *args):
        return


server = http.server.ThreadingHTTPServer((host, port), Handler)
thread = threading.Thread(target=server.serve_forever, daemon=True)
thread.start()

task = {
    "task": {
        "id": "browser-health-check",
        "description": "Open a local health page in Playwright and verify OK text.",
    },
    "steps": [
        {
            "id": "open_health",
            "uri": "browser://chrome/page/open",
            "operation": "open",
            "kind": "command",
            "payload": {"url": f"http://{host}:{port}/health"},
        },
        {
            "id": "read_dom",
            "uri": "browser://chrome/page/active",
            "operation": "extract_dom",
            "kind": "query",
            "depends_on": ["open_health"],
        },
        {
            "id": "verify_ok",
            "uri": "assertion://contains",
            "operation": "check",
            "kind": "query",
            "payload": {"actual_from": "read_dom.text", "expected": "ok"},
            "depends_on": ["read_dom"],
        },
    ],
}

with tempfile.NamedTemporaryFile("w", suffix=".yaml", delete=False) as handle:
    yaml.safe_dump(task, handle, sort_keys=False)
    task_path = handle.name

from uri2ops.operator.validator import validate_task_file
from uri2ops.operator.runner import run_task
from uri2ops.operator.task import load_task

errors = validate_task_file(task_path)
if errors:
    raise SystemExit("validation failed: " + "; ".join(errors))

result = run_task(load_task(task_path), adapter="playwright", approve=True)
print(yaml.safe_dump(result.to_dict(), sort_keys=False, allow_unicode=True))
server.shutdown()
raise SystemExit(0 if result.ok else 2)
PY

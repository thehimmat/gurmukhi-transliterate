"""Dev server for gurmukhi-transliterate: the demo page and the REST API.

It serves the same files Vercel deploys, so local and deployed behaviour
can't drift: ``/`` is ``index.html`` and ``/api/<name>`` runs the handler in
``api/<name>.py``.

    python server.py [port]        # default 3005, or $PORT
"""

import importlib.util
import json
import os
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
_API = {}


def api_handler(name: str):
    """The ``handler`` class of ``api/<name>.py``, or None."""
    if name not in _API:
        path = ROOT / "api" / f"{name}.py"
        if not name.isidentifier() or not path.is_file():
            return None
        spec = importlib.util.spec_from_file_location(f"api_{name}", path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        _API[name] = module.handler
    return _API[name]


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        pass  # suppress default access log

    def send_body(self, body: bytes, content_type: str, status: int = 200):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        path = urlparse(self.path).path
        if path in ("/", "/index.html"):
            self.send_body((ROOT / "index.html").read_bytes(), "text/html; charset=utf-8")
        elif path.startswith("/api/") and (handler := api_handler(path[len("/api/"):])):
            handler.do_GET(self)   # the Vercel handler, run on this request
        else:
            self.send_body(json.dumps({"error": "not found"}).encode(), "application/json", 404)


def serve(port: int) -> HTTPServer:
    return HTTPServer(("", port), Handler)


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else int(os.environ.get("PORT", 3005))
    server = serve(port)
    print(f"Running at http://localhost:{port}")
    server.serve_forever()

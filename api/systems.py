import sys
import os
import json
from http.server import BaseHTTPRequestHandler

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from gurmukhi_transliterate import SYSTEMS, SYSTEM_ORDER

# Every romanization system, in display order: the demo builds its menus from this.
SYSTEM_LIST = [{"id": "iso15919", "label": "ISO 15919"}, {"id": "practical", "label": "Practical"}] + [
    {"id": sid, "label": SYSTEMS[sid].label} for sid in SYSTEM_ORDER
]


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        body = json.dumps(SYSTEM_LIST, ensure_ascii=False).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

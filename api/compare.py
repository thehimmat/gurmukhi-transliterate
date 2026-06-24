import sys
import os
import json
from urllib.parse import urlparse, parse_qs
from http.server import BaseHTTPRequestHandler

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from gurmukhi_transliterate import comparison_table


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)
        text = params.get("text", [""])[0]
        delete_schwa = bool(params.get("schwa", [""])[0])
        systems_param = params.get("systems", [None])[0]
        systems = systems_param.split(",") if systems_param else None

        result = comparison_table(text, systems=systems, delete_schwa=delete_schwa)
        body = json.dumps(result, ensure_ascii=False).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

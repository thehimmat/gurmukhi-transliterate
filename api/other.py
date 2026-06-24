import sys
import os
import json
from urllib.parse import urlparse, parse_qs
from http.server import BaseHTTPRequestHandler

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from gurmukhi_transliterate import GurmukhiRomanizer, SYSTEMS


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)
        text = params.get("text", [""])[0]
        system = params.get("system", [""])[0]
        delete_schwa = bool(params.get("schwa", [""])[0])

        if not system or system not in SYSTEMS:
            body = json.dumps({"error": f"unknown system '{system}'"}).encode()
            self.send_response(400)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(body)
            return

        result = GurmukhiRomanizer(system).romanize(text, delete_schwa=delete_schwa)
        body = json.dumps({"system": system, "result": result}, ensure_ascii=False).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

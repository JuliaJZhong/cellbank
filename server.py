#!/usr/bin/env python3
"""
CellTracker local server.
Run from the celltracker/ directory:  python3 server.py
Then open http://localhost:8787 in your browser.
"""

import json
import os
import subprocess
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
PORT = 8787


class Handler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        # Suppress noisy default logs; print a cleaner version
        print(f"  {self.command} {self.path} → {args[1] if len(args) > 1 else ''}")

    def send_json(self, code, obj):
        body = json.dumps(obj, indent=2).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", len(body))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def send_file(self, path):
        with open(path, "rb") as f:
            body = f.read()
        ext = os.path.splitext(path)[1]
        ctype = {".html": "text/html", ".js": "text/javascript", ".css": "text/css"}.get(ext, "application/octet-stream")
        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", len(body))
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path

        if path == "/" or path == "/index.html":
            self.send_file(os.path.join(os.path.dirname(__file__), "index.html"))
            return

        if path.startswith("/data/"):
            fname = os.path.basename(path)
            fpath = os.path.join(DATA_DIR, fname)
            if os.path.exists(fpath) and fpath.endswith(".json"):
                with open(fpath) as f:
                    body = f.read().encode()
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", len(body))
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(body)
                return
            self.send_json(404, {"error": "not found"})
            return

        self.send_json(404, {"error": "not found"})

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length)
        try:
            payload = json.loads(body) if body else {}
        except json.JSONDecodeError:
            self.send_json(400, {"error": "invalid JSON"})
            return

        parsed = urlparse(self.path)
        path = parsed.path

        if path == "/api/save":
            # payload: { "file": "vials.json", "data": {...} }
            fname = payload.get("file", "")
            if not fname.endswith(".json") or "/" in fname or "\\" in fname:
                self.send_json(400, {"error": "invalid filename"})
                return
            fpath = os.path.join(DATA_DIR, fname)
            with open(fpath, "w") as f:
                json.dump(payload["data"], f, indent=2)
            self.send_json(200, {"ok": True})
            return

        if path == "/api/commit":
            # payload: { "message": "commit message" }
            msg = payload.get("message", "Update cell tracker data")
            try:
                repo_root = os.path.dirname(__file__)
                subprocess.run(["git", "add", "data/"], cwd=repo_root, check=True)
                result = subprocess.run(
                    ["git", "commit", "-m", msg],
                    cwd=repo_root,
                    capture_output=True, text=True
                )
                if result.returncode == 0:
                    self.send_json(200, {"ok": True, "output": result.stdout.strip()})
                else:
                    # Nothing to commit is not a real error
                    self.send_json(200, {"ok": True, "output": result.stderr.strip() or "Nothing to commit."})
            except Exception as e:
                self.send_json(500, {"error": str(e)})
            return

        self.send_json(404, {"error": "unknown endpoint"})


if __name__ == "__main__":
    os.makedirs(DATA_DIR, exist_ok=True)
    print(f"\n🧬 CellTracker server running at http://localhost:{PORT}")
    print(f"   Serving from: {os.path.dirname(__file__)}")
    print(f"   Press Ctrl+C to stop.\n")
    HTTPServer(("localhost", PORT), Handler).serve_forever()

#!/usr/bin/env python3
import json
import os
from http.server import SimpleHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
# Serve the entire project root (one level up from scripts/)
PROJECT_ROOT = os.path.dirname(ROOT_DIR)

class RefineHandler(SimpleHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self._send_cors_headers()
        self.end_headers()

    def _send_cors_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def do_POST(self):
        parsed = urlparse(self.path)
        if parsed.path == "/api/save_status":
            content_length = int(self.headers.get("Content-Length", "0"))
            body = self.rfile.read(content_length or 0)
            try:
                payload = json.loads(body.decode("utf-8"))
            except Exception:
                self.send_response(400)
                self._send_cors_headers()
                self.end_headers()
                self.wfile.write(b'{"error":"invalid json"}')
                return

            campaign_id = payload.get("campaignId")
            deletes = payload.get("deletes", [])
            images = payload.get("images", None)
            if not campaign_id or not isinstance(deletes, list):
                self.send_response(400)
                self._send_cors_headers()
                self.end_headers()
                self.wfile.write(b'{"error":"campaignId and deletes[] required"}')
                return

            # status.json path
            status_path = os.path.join(PROJECT_ROOT, "outputs", "campaigns", campaign_id, "status.json")
            os.makedirs(os.path.dirname(status_path), exist_ok=True)

            # Merge: update only deletes; preserve other fields if file exists
            status = {}
            if os.path.exists(status_path):
                try:
                    with open(status_path, "r") as f:
                        status = json.load(f) or {}
                except Exception:
                    status = {}
            status["deletes"] = deletes
            # If images array provided, update deleted flags on matching paths; preserve warnings and other fields
            if images is not None:
                # Ensure images structure exists
                existing = status.get("images")
                if isinstance(existing, list):
                    # Build map from path to deleted
                    path_to_deleted = {img.get("path"): bool(img.get("deleted")) for img in images if isinstance(img, dict)}
                    for img in existing:
                        p = img.get("path")
                        if p in path_to_deleted:
                            img["deleted"] = path_to_deleted[p]
                else:
                    status["images"] = images

            try:
                with open(status_path, "w") as f:
                    json.dump(status, f, indent=2)
            except Exception as e:
                self.send_response(500)
                self._send_cors_headers()
                self.end_headers()
                self.wfile.write(json.dumps({"error": f"failed to write status.json: {e}"}).encode("utf-8"))
                return

            self.send_response(200)
            self._send_cors_headers()
            self.end_headers()
            self.wfile.write(b'{"ok":true}')
            return

        # Unknown POST
        self.send_response(404)
        self._send_cors_headers()
        self.end_headers()
        self.wfile.write(b'{"error":"not found"}')

    # Serve static files relative to PROJECT_ROOT
    def translate_path(self, path):
        # Reuse SimpleHTTPRequestHandler translation but anchor at PROJECT_ROOT
        # Copied and adapted to change base directory
        # Normalize path
        path = path.split('?',1)[0]
        path = path.split('#',1)[0]
        import posixpath
        parts = [p for p in path.split('/') if p]
        import os
        p = PROJECT_ROOT
        for part in parts:
            if os.path.dirname(part) or part in (os.curdir, os.pardir):
                continue
            p = os.path.join(p, part)
        return p

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == "/api/latest_campaign":
            try:
                base = os.path.join(PROJECT_ROOT, "outputs", "campaigns")
                if not os.path.isdir(base):
                    self.send_response(404)
                    self._send_cors_headers()
                    self.end_headers()
                    self.wfile.write(b'{"error":"no campaigns dir"}')
                    return
                def latest_entry(path):
                    try:
                        entries = [os.path.join(path, d) for d in os.listdir(path)]
                    except Exception:
                        return None
                    dirs = [d for d in entries if os.path.isdir(d)]
                    if not dirs:
                        return None
                    return max(dirs, key=lambda d: os.path.getmtime(d))
                latest_top = latest_entry(base)
                if not latest_top:
                    self.send_response(404)
                    self._send_cors_headers()
                    self.end_headers()
                    self.wfile.write(b'{"error":"no campaigns found"}')
                    return
                latest_sub = latest_entry(latest_top)
                if latest_sub:
                    cid = os.path.basename(latest_top) + "/" + os.path.basename(latest_sub)
                else:
                    cid = os.path.basename(latest_top)
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self._send_cors_headers()
                self.end_headers()
                self.wfile.write(json.dumps({"campaign": cid}).encode("utf-8"))
                return
            except Exception as e:
                self.send_response(500)
                self._send_cors_headers()
                self.end_headers()
                self.wfile.write(json.dumps({"error": f"{e}"}).encode("utf-8"))
                return
        return super().do_GET()

def run(port: int):
    server = HTTPServer(("0.0.0.0", port), RefineHandler)
    print(f"Refine server running on http://localhost:{port}")
    server.serve_forever()

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()
    run(args.port)



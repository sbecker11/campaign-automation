#!/usr/bin/env python3
import json
import os
import subprocess
import threading
from http.server import SimpleHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
# Serve the entire project root (one level up from scripts/)
PROJECT_ROOT = os.path.dirname(ROOT_DIR)
# Outputs repository (separate repo for campaign outputs)
OUTPUTS_REPO_ROOT = os.path.join(PROJECT_ROOT, "..", "campaign-automation-outputs")

# Global server reference for shutdown
_server_instance = None

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
            images = payload.get("images", None)
            if not campaign_id:
                self.send_response(400)
                self._send_cors_headers()
                self.end_headers()
                self.wfile.write(b'{"error":"campaignId required"}')
                return

            # campaign_generated.json path
            status_filename = "campaign_generated.json"
            status_path = os.path.join(PROJECT_ROOT, "outputs", "campaigns", campaign_id, status_filename)
            os.makedirs(os.path.dirname(status_path), exist_ok=True)

            # Merge: update only visibility and comments; preserve other fields if file exists
            status = {}
            if os.path.exists(status_path):
                try:
                    with open(status_path, "r") as f:
                        status = json.load(f) or {}
                except Exception:
                    status = {}
            # If images array provided, update hidden flags and comments on matching paths; preserve warnings and other fields
            if images is not None:
                # Build map from path to payload (hidden/comment)
                by_path = {
                    img.get("path"): {
                        "hidden": bool(img.get("hidden")),
                        "comment": img.get("comment") if isinstance(img.get("comment"), str) else "",
                    }
                    for img in images
                    if isinstance(img, dict) and img.get("path")
                }
                
                # Update image_variants within products array
                products = status.get("products", [])
                if isinstance(products, list):
                    for product in products:
                        product_image_variants = product.get("image_variants", [])
                        if isinstance(product_image_variants, list):
                            for img in product_image_variants:
                                p = img.get("path")
                                if p in by_path:
                                    # Always update hidden status (explicitly set boolean)
                                    img["hidden"] = bool(by_path[p]["hidden"])
                                    # Always update comment (even if empty string)
                                    img["comment"] = by_path[p]["comment"]

            try:
                with open(status_path, "w") as f:
                    json.dump(status, f, indent=2)
            except Exception as e:
                self.send_response(500)
                self._send_cors_headers()
                self.end_headers()
                self.wfile.write(json.dumps({"error": f"failed to write {status_filename}: {e}"}).encode("utf-8"))
                return

            self.send_response(200)
            self._send_cors_headers()
            self.end_headers()
            self.wfile.write(b'{"ok":true}')
            return

        if parsed.path == "/api/commit_campaign":
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

            campaign_id_timestamp = payload.get("campaignIdTimestamp")
            if not campaign_id_timestamp:
                self.send_response(400)
                self._send_cors_headers()
                self.end_headers()
                self.wfile.write(b'{"error":"campaignIdTimestamp required"}')
                return

            # Check if outputs repo exists
            if not os.path.isdir(OUTPUTS_REPO_ROOT):
                self.send_response(500)
                self._send_cors_headers()
                self.end_headers()
                self.wfile.write(json.dumps({"error": f"Outputs repository not found at {OUTPUTS_REPO_ROOT}"}).encode("utf-8"))
                return

            # Campaign path in outputs repo
            campaign_path = os.path.join("outputs", "campaigns", campaign_id_timestamp)
            full_campaign_path = os.path.join(OUTPUTS_REPO_ROOT, campaign_path)
            
            # Check if campaign directory exists
            if not os.path.isdir(full_campaign_path):
                self.send_response(404)
                self._send_cors_headers()
                self.end_headers()
                self.wfile.write(json.dumps({"error": f"Campaign directory not found: {campaign_path}"}).encode("utf-8"))
                return

            # Execute git commands in sequence (in outputs repo)
            results = []
            commands = [
                ["git", "checkout", "-b", campaign_id_timestamp],
                ["git", "add", campaign_path],
                ["git", "commit", "-m", f"Add campaign: {campaign_id_timestamp}"],
                ["git", "push", "--set-upstream", "origin", campaign_id_timestamp]
            ]
            
            try:
                for idx, cmd in enumerate(commands):
                    # Format command for display - add quotes around commit message
                    if idx == 2 and len(cmd) >= 4 and cmd[2] == "-m":
                        display_cmd = f"{cmd[0]} {cmd[1]} {cmd[2]} \"{cmd[3]}\""
                    else:
                        display_cmd = " ".join(cmd)
                    result = {"command": display_cmd, "success": False, "output": "", "error": ""}
                    try:
                        proc = subprocess.run(
                            cmd,
                            cwd=OUTPUTS_REPO_ROOT,
                            capture_output=True,
                            text=True,
                            timeout=30
                        )
                        result["success"] = (proc.returncode == 0)
                        result["output"] = proc.stdout
                        result["error"] = proc.stderr
                        
                        # Special handling for checkout -b: if it fails, try to checkout existing branch
                        if idx == 0 and not result["success"]:
                            # Check both stderr and stdout for "already exists" message (case-insensitive)
                            error_text = (result["error"] + " " + result["output"]).lower()
                            if "already exists" in error_text or "fatal: a branch named" in error_text:
                                # Check if we're already on this branch
                                current_branch = subprocess.run(
                                    ["git", "branch", "--show-current"],
                                    cwd=OUTPUTS_REPO_ROOT,
                                    capture_output=True,
                                    text=True,
                                    timeout=30
                                )
                                current_branch_name = current_branch.stdout.strip() if current_branch.returncode == 0 else ""
                                
                                if current_branch_name == campaign_id_timestamp:
                                    # Already on the correct branch, treat as success
                                    result["success"] = True
                                    result["output"] = f"Already on branch '{campaign_id_timestamp}'"
                                    result["error"] = ""
                                    result["command"] = f"git checkout -b {campaign_id_timestamp} (already on branch)"
                                else:
                                    # Try to checkout the existing branch instead
                                    checkout_existing = subprocess.run(
                                        ["git", "checkout", campaign_id_timestamp],
                                        cwd=OUTPUTS_REPO_ROOT,
                                        capture_output=True,
                                        text=True,
                                        timeout=30
                                    )
                                    if checkout_existing.returncode == 0:
                                        result["success"] = True
                                        result["output"] = checkout_existing.stdout.strip() or f"Switched to existing branch '{campaign_id_timestamp}'"
                                        result["error"] = ""
                                        result["command"] = f"git checkout {campaign_id_timestamp} (branch already existed)"
                                    else:
                                        # Checkout failed - might be due to uncommitted changes
                                        checkout_error = checkout_existing.stderr.strip().lower()
                                        if "local changes" in checkout_error or "would be overwritten" in checkout_error:
                                            # Stash changes, checkout branch, then pop stash
                                            stash_result = subprocess.run(
                                                ["git", "stash"],
                                                cwd=OUTPUTS_REPO_ROOT,
                                                capture_output=True,
                                                text=True,
                                                timeout=30
                                            )
                                            if stash_result.returncode == 0:
                                                # Now try checkout again
                                                checkout_after_stash = subprocess.run(
                                                    ["git", "checkout", campaign_id_timestamp],
                                                    cwd=OUTPUTS_REPO_ROOT,
                                                    capture_output=True,
                                                    text=True,
                                                    timeout=30
                                                )
                                                if checkout_after_stash.returncode == 0:
                                                    # Pop the stash to restore changes
                                                    pop_result = subprocess.run(
                                                        ["git", "stash", "pop"],
                                                        cwd=OUTPUTS_REPO_ROOT,
                                                        capture_output=True,
                                                        text=True,
                                                        timeout=30
                                                    )
                                                    result["success"] = True
                                                    result["output"] = f"Stashed changes, switched to branch '{campaign_id_timestamp}', and restored changes"
                                                    result["error"] = ""
                                                    result["command"] = f"git checkout {campaign_id_timestamp} (stashed and restored changes)"
                                                else:
                                                    result["error"] = f"Stashed changes but checkout still failed: {checkout_after_stash.stderr.strip()}"
                                            else:
                                                result["error"] = f"Failed to stash changes: {stash_result.stderr.strip()}"
                                        else:
                                            result["error"] = f"Branch exists but checkout failed: {checkout_existing.stderr.strip()}"
                        
                        results.append(result)
                        # If any command fails, stop execution
                        if not result["success"]:
                            break
                    except subprocess.TimeoutExpired:
                        result["error"] = "Command timed out after 30 seconds"
                        results.append(result)
                        break
                    except Exception as e:
                        result["error"] = str(e)
                        results.append(result)
                        break
                
                self.send_response(200)
                self._send_cors_headers()
                self.end_headers()
                self.wfile.write(json.dumps({"ok": True, "results": results}).encode("utf-8"))
            except Exception as e:
                self.send_response(500)
                self._send_cors_headers()
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode("utf-8"))
            return

        if parsed.path == "/api/shutdown":
            # Shutdown the server after sending response
            def shutdown_server():
                import time
                time.sleep(0.5)  # Give time for response to be sent
                if _server_instance:
                    _server_instance.shutdown()
            
            threading.Thread(target=shutdown_server, daemon=True).start()
            self.send_response(200)
            self._send_cors_headers()
            self.end_headers()
            self.wfile.write(b'{"ok":true,"message":"Server shutting down"}')
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
    global _server_instance
    server = HTTPServer(("0.0.0.0", port), RefineHandler)
    _server_instance = server
    print(f"Refine server running on http://localhost:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
        print("Refine server stopped")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()
    run(args.port)



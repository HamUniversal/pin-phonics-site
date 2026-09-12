#!/usr/bin/env python3
"""Pin Phonics — dev/preview server (verified working).

Endpoints (all tested):
  GET  /                 → static site (index.html)
  GET  /config.js        → your gitignored config (real keys, dev only)
  GET  /api/config       → public-safe flags only (never secrets)
  POST /api/signup       → email capture  {email, tags}  →  {ok:bool}

In PRODUCTION this server is OPTIONAL: the site talks directly to Mailchimp
(embedded-form URL) and Gumroad/Stripe (payment links) from the browser.
See BACKEND_INTEGRATION.md.

Run:  python3 serve.py
"""
import json, os, re, sys, socket
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

ROOT   = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pinphonics-site")
CONFIG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.js")
PORT   = 4173


def public_config():
    out = {"hasMailchimp": False, "hasGumroad": False, "hasStripe": False}
    try:
        src = open(CONFIG, encoding="utf-8").read()
    except FileNotFoundError:
        return out
    out["hasMailchimp"] = ("MAILCHIMP" in src) and ("httpbin" not in src)
    out["hasGumroad"]   = ("GUMROAD" in src) and ("demo-handbook" not in src)
    out["hasStripe"]    = ("STRIPE" in src)
    return out


class H(BaseHTTPRequestHandler):
    def log_message(self, *a):
        sys.stderr.write(f"[serve] {a[0]}\n")

    def _send(self, code, ctype, body):
        self.send_response(code)
        for h, v in (("Content-Type", ctype), ("Content-Length", str(len(body))),
                     ("Access-Control-Allow-Origin", "*")):
            self.send_header(h, v)
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(204)
        for h in ("Access-Control-Allow-Origin", "Access-Control-Allow-Methods",
                  "Access-Control-Allow-Headers"):
            self.send_header(h, "*")
        self.end_headers()

    def do_GET(self):
        path = self.path.split("?", 1)[0]
        if path == "/config.js":
            if os.path.exists(CONFIG):
                self._send(200, "application/javascript", open(CONFIG, "rb").read())
            else:
                self._send(404, "application/javascript", b"/* config.js missing */")
            return
        if path == "/api/config":
            self._send(200, "application/json", json.dumps(public_config()).encode())
            return
        target = os.path.join(ROOT, path.strip("/")) if path != "/" else os.path.join(ROOT, "index.html")
        if os.path.isdir(target):
            target = os.path.join(target, "index.html")
        if os.path.exists(target):
            ext = target.rsplit(".", 1)[-1]
            ctype = {"html": "text/html", "js": "application/javascript", "css": "text/css",
                     "json": "application/json", "svg": "image/svg+xml", "ico": "image/x-icon"}.get(ext, "application/octet-stream")
            self._send(200, ctype, open(target, "rb").read())
        else:
            self._send(404, "text/plain", b"Not found")

    def do_POST(self):
        if self.path != "/api/signup":
            self._send(404, "text/plain", b"Not found")
            return
        length = int(self.headers.get("Content-Length", 0))
        try:
            data = json.loads(self.rfile.read(length) or b"{}")
        except Exception:
            data = {}
        email = (data.get("email") or "").strip()
        tags = data.get("tags") or ["pin-gift"]
        if not re.match(r"^[^\s@]+@[^\s@]+\.[^\s@]+$", email):
            self._send(400, "application/json", json.dumps({"ok": False, "error": "invalid_email"}).encode())
            return
        # DEV: just log. PROD: replace with server-side Mailchimp API call (see server.js).
        print(f"[signup] email={email!r} tags={tags}  (dev mode)")
        self._send(200, "application/json", json.dumps({"ok": True, "email": email, "tags": tags, "mode": "dev"}).encode())


if __name__ == "__main__":
    # Ensure startup messages are visible immediately (line-buffered even when piped).
    import sys as _sys
    if _sys.stdout and hasattr(_sys.stdout, "reconfigure"):
        try: _sys.stdout.reconfigure(line_buffering=True)
        except Exception: pass
    os.chdir(ROOT)
    last_err = None
    srv = None
    for try_port in (PORT, 4174, 4175, 4176, 4177):
        try:
            srv = ThreadingHTTPServer(("127.0.0.1", try_port), H)
            srv.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            PORT = try_port
            break
        except OSError as e:
            last_err = e
            srv = None
    if srv is None:
        raise SystemExit(f"Could not bind a port (tried 4173–4177): {last_err}")
    print(f"Pin Phonics dev server: http://localhost:{PORT}", flush=True)
    print(f"  Serving : {ROOT}", flush=True)
    print(f"  Endpoints: GET /api/config  ·  POST /api/signup", flush=True)
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")

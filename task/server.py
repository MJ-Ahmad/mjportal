#!/usr/bin/env python3
"""Web app server: login, JSON API and protected attachments. Standard library only.

Security: passwords are hashed, sessions are signed HttpOnly cookies, every API
write requires a custom header (blocks cross-site form posts), login is rate
limited, responses carry CSP and nosniff headers, and only whitelisted files
are served publicly. Run behind HTTPS (Caddy/Nginx) when reachable from outside.
"""

import os
import re
import sys
import json
import time
import threading
import traceback
from http import HTTPStatus
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlsplit, unquote

import _lib
import ops
import auth
from _lib import TaskError, read_database, ATTACH_DIR, BASE_DIR

STATIC = {
    "/": ("index.html", "text/html; charset=utf-8"),
    "/app.js": ("app.js", "text/javascript; charset=utf-8"),
    "/style.css": ("style.css", "text/css; charset=utf-8"),
    "/assets/logo.png": ("assets/logo.png", "image/png"),
}
CSP = ("default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
       "font-src https://fonts.gstatic.com; img-src 'self' data:; connect-src 'self'; "
       "frame-ancestors 'none'; base-uri 'none'; form-action 'self'")
MAX_BODY = 256 * 1024
SAFE_ATTACH = re.compile(r"^TASK-\d{6}-\d{2}\.[a-z0-9]{0,10}$|^TASK-\d{6}-\d{2}$")
limiter = auth.LoginLimiter()
write_lock = threading.Lock()


class Handler(BaseHTTPRequestHandler):
    server_version = "TaskApp"
    protocol_version = "HTTP/1.1"

    # ----- helpers
    def log_message(self, fmt, *args):
        sys.stderr.write("%s %s\n" % (self.address_string(), fmt % args))

    def _headers(self, status, ctype, length, extra=None, api=False):
        self.send_response(status)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(length))
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("X-Frame-Options", "DENY")
        self.send_header("Referrer-Policy", "same-origin")
        self.send_header("Content-Security-Policy", CSP)
        if api:
            self.send_header("Cache-Control", "no-store")
        for name, value in (extra or {}).items():
            self.send_header(name, value)
        self.end_headers()

    def _json(self, status, payload, extra=None):
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self._headers(status, "application/json; charset=utf-8", len(body), extra, api=True)
        self.wfile.write(body)

    def _session_ok(self):
        cookie = self.headers.get("Cookie", "")
        for part in cookie.split(";"):
            name, _, value = part.strip().partition("=")
            if name == "tsid":
                return auth.valid_session(value)
        return False

    def _read_json(self):
        length = int(self.headers.get("Content-Length") or 0)
        if length > MAX_BODY:
            raise TaskError("Request too large")
        raw = self.rfile.read(length) if length else b"{}"
        try:
            return json.loads(raw.decode("utf-8") or "{}")
        except ValueError:
            raise TaskError("Invalid JSON")

    def _client_ip(self):
        return self.client_address[0]

    # ----- routes
    def do_GET(self):
        path = urlsplit(self.path).path
        if path in STATIC:
            name, ctype = STATIC[path]
            with open(os.path.join(BASE_DIR, name), "rb") as f:
                body = f.read()
            self._headers(200, ctype, len(body), {"Cache-Control": "no-cache"})
            self.wfile.write(body)
            return
        if path == "/api/me":
            ok = self._session_ok()
            return self._json(200 if ok else 401, {"authenticated": ok})
        if path.startswith("/attachments/"):
            return self._serve_attachment(unquote(path[len("/attachments/"):]))
        if path == "/api/state":
            if not self._session_ok():
                return self._json(401, {"error": "Login required"})
            data, _ = read_database()
            return self._json(200, {"today": _lib.today_dhaka(), "lists": data["lists"],
                                    "tasks": data["tasks"]})
        self._json(404, {"error": "Not found"})

    def do_POST(self):
        path = urlsplit(self.path).path
        try:
            if path == "/api/login":
                return self._login()
            if path == "/api/logout":
                return self._json(200, {"ok": True}, {"Set-Cookie": "tsid=; Max-Age=0; Path=/; HttpOnly; SameSite=Strict"})
            if path == "/api/op":
                return self._op()
            self._json(404, {"error": "Not found"})
        except TaskError as exc:
            self._json(400, {"error": str(exc)})
        except Exception:  # never leak internals to the browser
            traceback.print_exc()
            self._json(500, {"error": "Internal error. Check the server log."})

    def _login(self):
        ip = self._client_ip()
        if not limiter.allowed(ip):
            return self._json(429, {"error": "Too many attempts. Try again in 15 minutes."})
        body = self._read_json()
        stored = auth.stored_hash()
        if not stored:
            raise TaskError("No password set. Run: ./run.sh passwd")
        if not auth.verify_password(str(body.get("password", "")), stored):
            limiter.record_failure(ip)
            time.sleep(0.5)
            return self._json(401, {"error": "Wrong password"})
        limiter.record_success(ip)
        cookie = (f"tsid={auth.make_session()}; Path=/; HttpOnly; SameSite=Strict; "
                  f"Max-Age={auth.SESSION_SECONDS}")
        if os.environ.get("HTTPS") == "1":
            cookie += "; Secure"
        self._json(200, {"ok": True}, {"Set-Cookie": cookie})

    def _op(self):
        if not self._session_ok():
            return self._json(401, {"error": "Login required"})
        if self.headers.get("X-Requested-With") != "taskapp":
            return self._json(403, {"error": "Missing request header"})
        body = self._read_json()
        op = body.get("op", "")
        if op not in ops.WEB_OPS:
            raise TaskError(f"Operation not allowed: {op}")
        args = body.get("args", {})
        if not isinstance(args, dict):
            raise TaskError("args must be an object")
        with write_lock:
            result = ops.run(op, **args)
        self._json(200, {"ok": True, "result": result})

    def _serve_attachment(self, name):
        if not self._session_ok():
            return self._json(401, {"error": "Login required"})
        if not SAFE_ATTACH.match(name):
            return self._json(404, {"error": "Not found"})
        path = os.path.join(ATTACH_DIR, name)
        if not os.path.isfile(path) or os.path.dirname(os.path.realpath(path)) != os.path.realpath(ATTACH_DIR):
            return self._json(404, {"error": "Not found"})
        with open(path, "rb") as f:
            body = f.read()
        import mimetypes
        ctype = mimetypes.guess_type(path)[0] or "application/octet-stream"
        self._headers(200, ctype, len(body), {"Content-Disposition": "attachment"})
        self.wfile.write(body)


def main(argv=None):
    argv = argv if argv is not None else sys.argv[1:]
    port = 8000
    if "--port" in argv:
        port = int(argv[argv.index("--port") + 1])
    bind = os.environ.get("BIND", "127.0.0.1")
    if not auth.stored_hash():
        print("No password is set. Run: ./run.sh passwd", file=sys.stderr)
        return 1
    _lib.ensure_structure()
    httpd = ThreadingHTTPServer((bind, port), Handler)
    print(f"Task app running at http://{bind}:{port}/  (Ctrl+C to stop)")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        httpd.server_close()
    return 0


if __name__ == "__main__":
    sys.exit(main())

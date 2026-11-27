"""Password and session handling for the web app. Standard library only.

Passwords are stored as PBKDF2-SHA256 hashes in config.json. Sessions are
HMAC-signed, expiring tokens in an HttpOnly cookie, so no session store is needed.
"""

import os
import json
import hmac
import time
import hashlib
import secrets
import base64
import tempfile

from _lib import CONFIG_FILE, SECRET_FILE

ITERATIONS = 310_000
SESSION_SECONDS = 30 * 24 * 3600


def hash_password(password, salt=None, iterations=ITERATIONS):
    salt = salt or secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations)
    return "pbkdf2_sha256${}${}${}".format(
        iterations, base64.b64encode(salt).decode(), base64.b64encode(digest).decode())


def verify_password(password, stored):
    try:
        _, iterations, salt_b64, digest_b64 = stored.split("$")
        expected = base64.b64decode(digest_b64)
        actual = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"),
                                     base64.b64decode(salt_b64), int(iterations))
    except (ValueError, TypeError):
        return False
    return hmac.compare_digest(actual, expected)


def write_password(password):
    config = {"password_hash": hash_password(password)}
    fd, tmp = tempfile.mkstemp(dir=os.path.dirname(CONFIG_FILE), suffix=".tmp")
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2)
    os.chmod(tmp, 0o600)
    os.replace(tmp, CONFIG_FILE)


def stored_hash():
    if not os.path.exists(CONFIG_FILE):
        return None
    with open(CONFIG_FILE, encoding="utf-8") as f:
        return json.load(f).get("password_hash")


def _secret():
    if not os.path.exists(SECRET_FILE):
        fd = os.open(SECRET_FILE, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(fd, "wb") as f:
            f.write(secrets.token_bytes(32))
    with open(SECRET_FILE, "rb") as f:
        return f.read()


def make_session(now=None):
    expires = int((now or time.time()) + SESSION_SECONDS)
    payload = f"{expires}.{secrets.token_urlsafe(12)}"
    signature = hmac.new(_secret(), payload.encode(), hashlib.sha256).hexdigest()
    return f"{payload}.{signature}"


def valid_session(token, now=None):
    if not token or token.count(".") != 2:
        return False
    expires_text, nonce, signature = token.split(".")
    expected = hmac.new(_secret(), f"{expires_text}.{nonce}".encode(), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(expected, signature):
        return False
    return int(expires_text) > (now or time.time())


class LoginLimiter:
    """Blocks an address for 15 minutes after 5 failed attempts in 10 minutes."""

    def __init__(self, max_failures=5, window=600, lockout=900):
        self.max_failures, self.window, self.lockout = max_failures, window, lockout
        self.failures = {}
        self.blocked_until = {}

    def allowed(self, ip, now=None):
        now = now or time.time()
        return self.blocked_until.get(ip, 0) <= now

    def record_failure(self, ip, now=None):
        now = now or time.time()
        recent = [t for t in self.failures.get(ip, []) if now - t < self.window] + [now]
        self.failures[ip] = recent
        if len(recent) >= self.max_failures:
            self.blocked_until[ip] = now + self.lockout
            self.failures[ip] = []

    def record_success(self, ip):
        self.failures.pop(ip, None)

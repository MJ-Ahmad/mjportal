#!/usr/bin/env python3
"""ব্যক্তিগত ভল্ট — zip থেকে ফটো, ভিডিও, অডিও, ডকুমেন্ট এনক্রিপ্ট করে সাজায়।

  python3 private_vault.py            private-inbox/ এর সব zip যোগ করে ভল্ট বানায়/আপডেট করে
  python3 private_vault.py status     ভল্টে কী আছে তার হিসাব দেখায় (পাসওয়ার্ড লাগবে)

ধাপগুলো:
  1. zip খোলা হয় একটি অস্থায়ী ফোল্ডারে; সেখান থেকে সাধারণ ফাইল কোথাও জমে না।
  2. প্রতিটি ফাইল ধরন অনুযায়ী photos / videos / audio / documents এ ভাগ হয়।
  3. প্রতিটি ফাইল AES-256-CTR + HMAC-SHA256 দিয়ে এনক্রিপ্ট হয়ে private/vault/files/ এ যায়।
  4. ফাইলের নাম ও তালিকা (manifest) আলাদাভাবে এনক্রিপ্ট হয় — তাই নামও গোপন থাকে।
  5. পাসওয়ার্ড কোথাও সংরক্ষিত হয় না। ভুল পাসওয়ার্ডে ভল্ট খোলে না।

কোনো pip ইন্সটল লাগে না — শুধু Python 3 দরকার।
"""

from __future__ import annotations

import argparse
import base64
import getpass
import hashlib
import hmac
import json
import mimetypes
import os
import secrets
import sys
import tempfile
import zipfile
from datetime import datetime, timezone
from pathlib import Path

try:  # cryptography থাকলে ফাইল এনক্রিপশন দ্রুত হয়; না থাকলেও এই স্ক্রিপ্ট নিজে চলে
    from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
    _FAST = True
except ImportError:
    _FAST = False

BASE = Path(__file__).resolve().parent
INBOX = BASE / "private-inbox"
VAULT = BASE / "private" / "vault"
FILES = VAULT / "files"
META_FILE = VAULT / "vault.json"
MANIFEST_FILE = VAULT / "manifest.bin"

ITERATIONS = 600_000   # ব্রাউজারেও একই সংখ্যা ব্যবহার হয় (private/app.js)
MIN_PASSWORD = 6
VERSION = 1

CATEGORY_EXTS = {
    "photos": {".jpg", ".jpeg", ".png", ".gif", ".webp", ".heic", ".bmp"},
    "videos": {".mp4", ".webm", ".mov", ".m4v"},
    "audio": {".mp3", ".m4a", ".aac", ".wav", ".ogg", ".opus", ".flac"},
    "documents": {".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx",
                  ".txt", ".md", ".csv", ".rtf", ".odt"},
}
CATEGORY_BN = {"photos": "ফটো", "videos": "ভিডিও", "audio": "অডিও", "documents": "ডকুমেন্ট"}


def now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def classify(filename: str) -> str | None:
    ext = Path(filename).suffix.lower()
    for category, exts in CATEGORY_EXTS.items():
        if ext in exts:
            return category
    return None


def ask_password(new_vault: bool) -> str:
    password = getpass.getpass("ভল্ট পাসওয়ার্ড (লেখা দেখাবে না): ")
    if len(password) < MIN_PASSWORD:
        sys.exit(f"✘ পাসওয়ার্ড কমপক্ষে {MIN_PASSWORD} অক্ষরের হতে হবে।")
    if new_vault and getpass.getpass("পাসওয়ার্ড আবার লিখুন: ") != password:
        sys.exit("✘ দুটো পাসওয়ার্ড মেলেনি। আবার চালান।")
    return password


class BadTag(Exception):
    """ভুল পাসওয়ার্ড বা নষ্ট ডেটা: HMAC মেলেনি।"""


# ---- AES-256 (শুধু এনক্রিপশন, CTR মোডে) — বাইরের লাইব্রেরি ছাড়া ----
def _xtime(a: int) -> int:
    a <<= 1
    return (a ^ 0x11B) & 0xFF if a & 0x100 else a


def _gmul(a: int, b: int) -> int:
    r = 0
    while b:
        if b & 1:
            r ^= a
        a = _xtime(a)
        b >>= 1
    return r


def _build_sbox() -> list:
    sbox = [0] * 256
    for x in range(256):
        inv = next((y for y in range(1, 256) if _gmul(x, y) == 1), 0) if x else 0
        b, s_ = inv, inv
        for _ in range(4):
            b = ((b << 1) | (b >> 7)) & 0xFF
            s_ ^= b
        sbox[x] = s_ ^ 0x63
    return sbox


SBOX = _build_sbox()
MUL2 = [_gmul(i, 2) for i in range(256)]
MUL3 = [_gmul(i, 3) for i in range(256)]
MASK128 = (1 << 128) - 1


def _expand_key(key: bytes) -> list:
    nk, nr = 8, 14  # AES-256
    w = [list(key[4 * i:4 * i + 4]) for i in range(nk)]
    rcon = 1
    for i in range(nk, 4 * (nr + 1)):
        t = list(w[i - 1])
        if i % nk == 0:
            t = [SBOX[b] for b in t[1:] + t[:1]]
            t[0] ^= rcon
            rcon = _xtime(rcon)
        elif i % nk == 4:
            t = [SBOX[b] for b in t]
        w.append([a ^ b for a, b in zip(w[i - nk], t)])
    return [sum(w[4 * r:4 * r + 4], []) for r in range(nr + 1)]


def _encrypt_block(rks: list, block: bytes) -> bytes:
    s = [b ^ k for b, k in zip(block, rks[0])]
    nr = len(rks) - 1
    for rnd in range(1, nr + 1):
        s = [SBOX[b] for b in s]
        s = [s[r + 4 * ((c + r) % 4)] for c in range(4) for r in range(4)]  # ShiftRows
        if rnd != nr:  # MixColumns
            out = []
            for c in range(4):
                a0, a1, a2, a3 = s[4 * c:4 * c + 4]
                out += [MUL2[a0] ^ MUL3[a1] ^ a2 ^ a3,
                        a0 ^ MUL2[a1] ^ MUL3[a2] ^ a3,
                        a0 ^ a1 ^ MUL2[a2] ^ MUL3[a3],
                        MUL3[a0] ^ a1 ^ a2 ^ MUL2[a3]]
            s = out
        s = [b ^ k for b, k in zip(s, rks[rnd])]
    return bytes(s)


def _ctr(key: bytes, iv: bytes, data: bytes) -> bytes:
    """AES-256-CTR: এনক্রিপ্ট ও ডিক্রিপ্ট একই কাজ। ব্রাউজারের WebCrypto AES-CTR (length 128) এর সাথে মেলে।"""
    if _FAST:
        c = Cipher(algorithms.AES(key), modes.CTR(iv)).encryptor()
        return c.update(data) + c.finalize()
    rks = _expand_key(key)
    counter = int.from_bytes(iv, "big")
    out = bytearray()
    for off in range(0, len(data), 16):
        chunk = data[off:off + 16]
        ks = _encrypt_block(rks, (counter & MASK128).to_bytes(16, "big"))[:len(chunk)]
        out += (int.from_bytes(chunk, "big") ^ int.from_bytes(ks, "big")).to_bytes(len(chunk), "big")
        counter += 1
    return bytes(out)


def derive_key(password: str, salt: bytes, iterations: int):
    """PBKDF2-SHA256 থেকে ৬৪ বাইট: প্রথম ৩২ = এনক্রিপ্ট কী, পরের ৩২ = HMAC কী।"""
    raw = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations, dklen=64)
    return raw[:32], raw[32:]


def seal(keys, data: bytes) -> bytes:
    """ফরম্যাট: 16 বাইট IV + ciphertext + 32 বাইট HMAC-SHA256(IV+ciphertext) — ব্রাউজারের সাথে মেলে।"""
    enc, mac = keys
    iv = secrets.token_bytes(16)
    body = iv + _ctr(enc, iv, data)
    return body + hmac.new(mac, body, hashlib.sha256).digest()


def open_blob(keys, blob: bytes) -> bytes:
    enc, mac = keys
    if len(blob) < 48:
        raise BadTag()
    body, tag = blob[:-32], blob[-32:]
    if not hmac.compare_digest(hmac.new(mac, body, hashlib.sha256).digest(), tag):
        raise BadTag()
    return _ctr(enc, body[:16], body[16:])


def write_atomic(path: Path, data: bytes) -> None:
    tmp = path.parent / (path.name + ".tmp")
    tmp.write_bytes(data)
    os.replace(tmp, path)


def load_manifest(key: bytes) -> dict:
    if not MANIFEST_FILE.exists():
        return {"version": VERSION, "items": []}
    blob = MANIFEST_FILE.read_bytes()
    try:
        return json.loads(open_blob(key, blob))
    except BadTag:
        sys.exit("✘ পাসওয়ার্ড ভুল — ভল্ট খোলা যায়নি।")


def safe_extract(zip_path: Path, dest: Path) -> None:
    """zip এর ভেতরের লুকানো ফাইল, __MACOSX এবং ../ পথ বাদ দেয়।"""
    with zipfile.ZipFile(zip_path) as zf:
        for info in zf.infolist():
            parts = [p for p in info.filename.replace("\\", "/").split("/") if p]
            if not parts or info.is_dir() or info.filename.startswith("/"):
                continue
            if any(p.startswith(".") or p == "__MACOSX" for p in parts):
                continue
            target = dest.joinpath(*parts)
            target.parent.mkdir(parents=True, exist_ok=True)
            with zf.open(info) as src, open(target, "wb") as out:
                while chunk := src.read(1 << 20):
                    out.write(chunk)


def build() -> None:
    INBOX.mkdir(exist_ok=True)
    zips = sorted(INBOX.glob("*.zip"))
    if not zips:
        print(f"ℹ '{INBOX.name}' ফোল্ডার খালি।")
        print("  এই ফোল্ডারে zip ফাইল রাখুন (যেমন photos.zip, videos.zip, audio.zip, documents.zip)")
        print("  তারপর আবার চালান:  python3 private_vault.py")
        return

    new_vault = not META_FILE.exists()
    password = ask_password(new_vault)
    if new_vault:
        salt = secrets.token_bytes(16)
        meta = {"format": "nijer-khata-vault", "version": VERSION, "kdf": "PBKDF2-SHA256",
                "iterations": ITERATIONS, "salt": base64.b64encode(salt).decode()}
    else:
        meta = json.loads(META_FILE.read_text(encoding="utf-8"))
    key = derive_key(password, base64.b64decode(meta["salt"]), meta["iterations"])
    manifest = load_manifest(key)
    index = {item["path"]: item for item in manifest["items"]}

    FILES.mkdir(parents=True, exist_ok=True)
    added = replaced = 0
    skipped: list[str] = []

    with tempfile.TemporaryDirectory(prefix="vault-") as tmp:
        for z in zips:
            print(f"▶ {z.name} খোলা ও সাজানো হচ্ছে...")
            dest = Path(tmp) / z.stem
            dest.mkdir(parents=True)
            safe_extract(z, dest)
            for f in sorted(p for p in dest.rglob("*") if p.is_file()):
                rel = f"{z.stem}/{f.relative_to(dest).as_posix()}"
                category = classify(f.name)
                if category is None:
                    skipped.append(rel)
                    continue
                data = f.read_bytes()
                old = index.get(rel)
                stored = secrets.token_hex(16) + ".bin"
                (FILES / stored).write_bytes(seal(key, data))
                if old:
                    (FILES / old["file"]).unlink(missing_ok=True)
                    replaced += 1
                else:
                    added += 1
                index[rel] = {
                    "id": old["id"] if old else secrets.token_hex(6),
                    "path": rel,
                    "name": f.name,
                    "category": category,
                    "mime": mimetypes.guess_type(f.name)[0] or "application/octet-stream",
                    "size": len(data),
                    "file": stored,
                    "added": old["added"] if old else now_iso(),
                }

    manifest["items"] = sorted(index.values(), key=lambda i: (i["category"], i["path"]))
    manifest["updated"] = now_iso()
    write_atomic(MANIFEST_FILE, seal(key, json.dumps(manifest, ensure_ascii=False).encode("utf-8")))
    if new_vault:
        META_FILE.write_text(json.dumps(meta, indent=2), encoding="utf-8")

    print()
    print(f"✔ নতুন যোগ: {added} · আপডেট: {replaced}")
    print_counts(manifest)
    if skipped:
        print(f"⚠ চেনা যায়নি বলে বাদ গেছে ({len(skipped)}টি):")
        for name in skipped[:20]:
            print(f"   - {name}")
        if len(skipped) > 20:
            print(f"   ... আরও {len(skipped) - 20}টি")
    print()
    print("পরবর্তী ধাপ: ভল্ট ঠিক আছে কিনা নিশ্চিত হলে private-inbox/ এর zip গুলো মুছে ফেলুন।")


def print_counts(manifest: dict) -> None:
    total_bytes = 0
    for cat, label in CATEGORY_BN.items():
        items = [i for i in manifest["items"] if i["category"] == cat]
        size = sum(i["size"] for i in items)
        total_bytes += size
        print(f"   {label:<8} {len(items):>5} টি   ({size / 1048576:.1f} MB)")
    print(f"   মোট      {len(manifest['items']):>5} টি   ({total_bytes / 1048576:.1f} MB)")


def status() -> None:
    if not META_FILE.exists():
        print("ℹ এখনো কোনো ভল্ট নেই। আগে zip রেখে  python3 private_vault.py  চালান।")
        return
    meta = json.loads(META_FILE.read_text(encoding="utf-8"))
    key = derive_key(ask_password(False), base64.b64decode(meta["salt"]), meta["iterations"])
    print_counts(load_manifest(key))


def main() -> None:
    parser = argparse.ArgumentParser(description="ব্যক্তিগত ভল্ট তৈরি করুন")
    parser.add_argument("command", nargs="?", default="build", choices=["build", "status"])
    args = parser.parse_args()
    if args.command == "status":
        status()
    else:
        build()


if __name__ == "__main__":
    main()

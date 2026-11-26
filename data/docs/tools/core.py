#!/usr/bin/env python3
"""Core library of the Registry docs store.

Layout (everything is static files — host anywhere, e.g. GitHub Pages):

  data.json              site settings + top menu (Dashboard / Docs / Registry)  — tiny, loaded by the home page
  docs/index.json        Docs folder tree + metadata of every file (NO file contents) — loaded when needed
  docs/files/<ID>.txt    the content of each file — loaded only when that file is opened
"""
import hashlib, json, os, re, shutil, sys, urllib.request
from datetime import datetime
from urllib.parse import urlparse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS = os.path.join(ROOT, "docs")
INDEX = os.path.join(DOCS, "index.json")
FILES = os.path.join(DOCS, "files")
SCHEMA = 2
PREFIX = "DOC"
MAX_BYTES = 2 * 1024 * 1024          # per-file limit
ID_RE = re.compile(rf"^{PREFIX}-(\d{{4}})-(\d{{4,}})$")

# extension -> (lang key, label)
EXT = {"html": ("html", "HTML"), "htm": ("html", "HTML"), "json": ("json", "JSON"), "py": ("python", "Python"),
       "js": ("node", "Node.js"), "mjs": ("node", "Node.js"), "cjs": ("node", "Node.js"), "ts": ("ts", "TypeScript"),
       "jsx": ("react", "React"), "tsx": ("react", "React"), "sh": ("shell", "Shell"), "bash": ("shell", "Shell"),
       "css": ("css", "CSS"), "scss": ("css", "CSS"), "md": ("markdown", "Markdown"), "yml": ("yaml", "YAML"),
       "yaml": ("yaml", "YAML"), "sql": ("sql", "SQL"), "xml": ("xml", "XML"), "php": ("php", "PHP"),
       "java": ("java", "Java"), "c": ("c", "C"), "h": ("c", "C"), "cpp": ("cpp", "C++"), "go": ("go", "Go"),
       "rs": ("rust", "Rust"), "cs": ("csharp", "C#"), "kt": ("kotlin", "Kotlin"), "rb": ("ruby", "Ruby"),
       "dart": ("dart", "Dart"), "vue": ("vue", "Vue"), "toml": ("toml", "TOML"), "csv": ("csv", "CSV"),
       "svg": ("svg", "SVG"), "txt": ("text", "Text")}
SHEBANG = {"python": ("python", "Python"), "node": ("node", "Node.js"), "bash": ("shell", "Shell"), "sh": ("shell", "Shell")}


# ---------------------------------------------------------------- basics
def now(): return datetime.now().astimezone().isoformat(timespec="seconds")
def sha(text): return hashlib.sha256(text.encode("utf-8")).hexdigest()
def die(msg): print("ERROR:", msg, file=sys.stderr); sys.exit(1)
def tags(s): return [t.strip() for t in (s or "").split(",") if t.strip()]
def count_lines(t): return t.count("\n") + (0 if t == "" or t.endswith("\n") else 1)
def prune(e): return {k: v for k, v in e.items() if v not in ("", None, [], {})}


def ask(label, default="", req=False):
    while True:
        v = input(f"{label}{' [' + default + ']' if default else ''}: ").strip() or default
        if req and not v: print("  required"); continue
        return v


def detect(name, text, force=""):
    if force:
        return next((v for v in EXT.values() if v[0] == force), (force, force.upper()))
    ext = name.rsplit(".", 1)[-1].lower() if "." in name else ""
    if ext in EXT: return EXT[ext]
    if text.startswith("#!"):
        first = text.split("\n", 1)[0]
        for k, v in SHEBANG.items():
            if k in first: return v
    return ("text", "Text")


# ---------------------------------------------------------------- store
def new_index(): return {"schema": SCHEMA, "updated_at": now(), "counters": {}, "tree": [], "files": []}


def load():
    if not os.path.exists(INDEX): return new_index()
    with open(INDEX, encoding="utf-8") as f: d = json.load(f)
    d.setdefault("counters", {}); d.setdefault("tree", []); d.setdefault("files", [])
    return d


def save(d):
    """Atomic write; keeps one backup (index.json.bak). Header (tree etc.) on one line, one file entry per line."""
    d["schema"] = SCHEMA; d["updated_at"] = now()
    os.makedirs(DOCS, exist_ok=True)
    if os.path.exists(INDEX): shutil.copy2(INDEX, INDEX + ".bak")
    dump = lambda o: json.dumps(o, ensure_ascii=False, separators=(",", ":"))
    head = dump({k: v for k, v in d.items() if k != "files"})
    out = head[:-1] + ',"files":[\n' + ",\n".join(dump(f) for f in d["files"]) + "\n]}\n"
    tmp = INDEX + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="\n") as f: f.write(out)
    os.replace(tmp, INDEX)


def content_path(i): return os.path.join(FILES, i + ".txt")


def read_content(i):
    with open(content_path(i), encoding="utf-8") as f: return f.read()


def next_id(d):
    """Never reuses an ID: DOC-YYYY-NNNN (counter per year)."""
    y = str(datetime.now().year)
    taken = {f["id"] for f in d["files"]}
    n = d["counters"].get(y, 0)
    while True:
        n += 1; i = f"{PREFIX}-{y}-{n:04d}"
        if i not in taken: break
    d["counters"][y] = n
    return i


def find_file(d, i): return next((f for f in d["files"] if f["id"] == i), None)


# ---------------------------------------------------------------- folder tree
def root_node(d): return {"id": "", "en": "Docs", "bn": "ডকস", "children": d["tree"]}


def walk(nodes, path=()):
    for n in nodes:
        p = path + (n["id"],)
        yield n, p
        yield from walk(n.get("children", []), p)


def find_node(d, ref):
    """ref = folder id, or a name path like 'Web/Portal' (EN/BN/id, case-insensitive). '' / 'docs' = root.
    Returns (node, [id path]) or (None, None)."""
    ref = (ref or "").strip()
    if ref.strip("/").lower() in ("", "docs", "root", "ডকস"): return root_node(d), []
    for n, p in walk(d["tree"]):
        if n["id"] == ref: return n, list(p)
    segs = [s.strip().lower() for s in ref.strip("/").split("/") if s.strip()]
    if segs and segs[0] in ("docs", "ডকস"): segs = segs[1:]
    if not segs: return root_node(d), []

    def go(ns, sg, path):
        for n in ns:
            if sg[0] in (n["id"].lower(), (n.get("en") or "").lower(), (n.get("bn") or "").lower()):
                if len(sg) == 1: return n, path + [n["id"]]
                r = go(n.get("children", []), sg[1:], path + [n["id"]])
                if r[0]: return r
        return None, None
    hit = go(d["tree"], segs, [])
    if hit[0]: return hit
    # fallback: the path may start anywhere in the tree ('Portal' or 'Web/Portal' under some parent) — accept if unambiguous
    byid = {n["id"]: n for n, _ in walk(d["tree"])}
    cands = []
    for n, p in walk(d["tree"]):
        if len(p) < len(segs): continue
        tail = p[-len(segs):]
        if all(sg in (i.lower(), (byid[i].get("en") or "").lower(), (byid[i].get("bn") or "").lower()) for sg, i in zip(segs, tail)):
            cands.append((n, list(p)))
    if len(cands) == 1: return cands[0]
    if len(cands) > 1: die(f"'{ref}' is ambiguous — use a longer path or an id: " + ", ".join(f"{label_path(d, p)} [{n['id']}]" for n, p in cands))
    return None, None


def slug(name):
    s = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    return s or "f-" + hashlib.sha1(name.encode("utf-8")).hexdigest()[:6]


def ensure_chain(d, parent, ppath, names, bns=()):
    """Create (or reuse, matched by name) nested folders under `parent`. -> (deepest node, id path)"""
    ids = {n["id"] for n, _ in walk(d["tree"])}
    for k, name in enumerate(names):
        sib = parent.setdefault("children", [])
        hit = next((c for c in sib if name.lower() in ((c.get("en") or "").lower(), (c.get("bn") or "").lower())), None)
        if not hit:
            bn = bns[k].strip() if k < len(bns) and bns[k].strip() else name
            base = slug(name); nid = base; i = 2
            while nid in ids: nid = f"{base}-{i}"; i += 1
            ids.add(nid)
            hit = {"id": nid, "bn": bn, "en": name}
            sib.append(hit)
        parent = hit; ppath = ppath + [hit["id"]]
    return parent, ppath


def detach(nodes, nid):
    for i, n in enumerate(nodes):
        if n["id"] == nid: return nodes.pop(i)
        r = detach(n.get("children", []), nid)
        if r is not None: return r
    return None


def label_path(d, ids):
    m = {n["id"]: n for n, _ in walk(d["tree"])}
    return " › ".join((m[i].get("en") or m[i].get("bn") or i) if i in m else i for i in ids) or "Docs"


# ---------------------------------------------------------------- reading sources
def read_source(src):
    """Local path or http(s) URL -> (name, text). Dies on binary/too large."""
    try:
        if src.startswith(("http://", "https://")):
            req = urllib.request.Request(src, headers={"User-Agent": "mj-registry"})
            with urllib.request.urlopen(req, timeout=20) as r: raw = r.read(MAX_BYTES + 1)
            name = os.path.basename(urlparse(src).path) or "index.html"
        else:
            p = os.path.abspath(os.path.expanduser(src))
            if not os.path.isfile(p): die(f"file not found: {src}")
            with open(p, "rb") as f: raw = f.read(MAX_BYTES + 1)
            name = os.path.basename(p)
    except SystemExit: raise
    except Exception as e: die(f"could not read {src}: {e}")
    if len(raw) > MAX_BYTES: die(f"file larger than {MAX_BYTES // 1048576} MB")
    try: text = raw.decode("utf-8-sig").replace("\r\n", "\n")
    except UnicodeDecodeError: die("not a UTF-8 text file (binary files are not supported)")
    return name, text


def hash_map(d): return {f["sha256"]: f for f in d["files"]}


def add_file(d, name, text, src, path, seen, *, title="", title_bn="", desc="", desc_bn="", category="",
             tags=(), lang="", force=False):
    """Append one file (content written to docs/files/). -> (new id, None) or (None, duplicate entry)."""
    lang_key, label = detect(name, text, lang)
    h = sha(text)
    if h in seen and not force: return None, seen[h]
    i = next_id(d)
    os.makedirs(FILES, exist_ok=True)
    with open(content_path(i), "w", encoding="utf-8", newline="\n") as f: f.write(text)
    ts = now()
    e = prune({"id": i, "title": title or name, "title_bn": title_bn, "desc": desc, "desc_bn": desc_bn,
               "filename": name, "lang": lang_key, "lang_label": label,
               "ext": name.rsplit(".", 1)[-1].lower() if "." in name else "",
               "lines": count_lines(text), "bytes": len(text.encode("utf-8")), "sha256": h,
               "menu_path": list(path), "category": category, "tags": list(tags), "source": src,
               "created_at": ts, "updated_at": ts})
    e["menu_path"] = list(path)           # keep even when empty (root)
    d["files"].append(e); seen[h] = e
    return i, None


# ---------------------------------------------------------------- validation
def check(d):
    """-> (errors, warnings)"""
    errs, warns, seen = [], [], set()
    req = ["id", "title", "filename", "lang", "sha256", "created_at"]
    node_ids = [n["id"] for n, _ in walk(d["tree"])]
    errs += [f"duplicate folder id {i}" for i in set(node_ids) if node_ids.count(i) > 1]
    for n, _ in walk(d["tree"]):
        if not (n.get("en") or n.get("bn")): errs.append(f"folder {n['id']}: needs a name (en or bn)")
    tree_children = {n["id"]: {c["id"] for c in n.get("children", [])} for n, _ in walk(d["tree"])}
    top = {n["id"] for n in d["tree"]}
    for f in d["files"]:
        i = f.get("id", "?")
        if i in seen: errs.append(f"duplicate ID {i}")
        seen.add(i)
        m = ID_RE.match(i)
        if not m: errs.append(f"bad ID format {i}"); continue
        errs += [f"{i}: missing '{k}'" for k in req if not f.get(k)]
        if d["counters"].get(m.group(1), 0) < int(m.group(2)): errs.append(f"{i}: counter behind")
        mp = f.get("menu_path", [])
        for k, x in enumerate(mp):
            ok = (x in top) if k == 0 else (x in tree_children.get(mp[k - 1], set()))
            if not ok: errs.append(f"{i}: menu_path broken at '{x}'"); break
        p = content_path(i)
        if not os.path.isfile(p): errs.append(f"{i}: content file missing"); continue
        with open(p, encoding="utf-8") as fh: t = fh.read()
        if sha(t) != f.get("sha256"): errs.append(f"{i}: content hash mismatch")
    if os.path.isdir(FILES):
        for fn in os.listdir(FILES):
            if fn.endswith(".txt") and fn[:-4] not in seen: warns.append(f"orphan content file {fn}")
    return errs, warns

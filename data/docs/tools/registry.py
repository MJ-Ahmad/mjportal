#!/usr/bin/env python3
"""Registry CLI — manage the Docs store.   (normally run through ./run.sh)

  ./run.sh add FILE_OR_URL ["Title"] ["Description"] [--bn "শিরোনাম" --bn "বর্ণনা"]
             [--menu "Web/Portal"] [--new-menu "UI/Forms" --new-menu-bn "ইউআই/ফর্ম"]
             [--category X] [--tags a,b] [--lang python] [--force]
  ./run.sh add-dir DIR [--menu "Web"] [--title "Portal v2"] [--exclude dist,coverage] [--force]
  ./run.sh menu                                      show the folder tree
  ./run.sh menu --new "Web/Portal" [--bn "ওয়েব/পোর্টাল"] [--under "Web"]
  ./run.sh menu --move DOC-2026-0001 --to "Web/Portal"          move one file
  ./run.sh menu --move-menu "Web/Portal" --to "Tools"           move a folder with everything inside
  ./run.sh menu --rename "Web" --en "Websites" [--bn "ওয়েবসাইট"]
  ./run.sh menu --rm "Web/Old"                                   delete an EMPTY folder
  ./run.sh rm DOC-2026-0001 [...]                                delete file(s)
  ./run.sh stats | check | migrate OLD.json [--replace]
Without --menu a file goes to  Docs › <file type>  (e.g. Docs › HTML).  Use --to root to move to the top level."""
import argparse, json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from core import *

SKIP = {".git", "node_modules", "__pycache__", ".venv", "venv", ".idea", ".vscode", "dist", "build", ".next", ".cache"}


def report(d):
    errs, warns = check(d)
    for w in warns: print("  ⚠", w)
    if errs:
        print("✘ Problems:"); [print("  -", e) for e in errs]; sys.exit(1)
    folders = sum(1 for _ in walk(d["tree"]))
    print(f"✔ OK — {len(d['files'])} files, {folders} folders")


def folder_label(d, ids): return label_path(d, ids)


# ------------------------------------------------------------------ add
def cmd_add(x):
    if not x.source:
        print("— New Docs entry (Enter to skip optional fields) —")
        x.source = ask("File path or URL *", req=True); x.title = ask("Title (EN)"); x.title_bn = ask("শিরোনাম (BN)")
        x.desc = ask("Description (EN)"); x.desc_bn = ask("বর্ণনা (BN)")
        x.menu = ask("Existing folder (id or path, Enter = by file type; ./run.sh menu shows the tree)")
        x.new_menu = ask("New subfolder name(s) e.g. UI/Forms (optional)")
        x.new_menu_bn = ask("নতুন সাবফোল্ডারের বাংলা নাম (optional)") if x.new_menu else ""
        x.category = ask("Category"); x.tags = ask("Tags a,b")
    tb = x.title_bn or (x.bn[0] if x.bn else ""); db = x.desc_bn or (x.bn[1] if len(x.bn) > 1 else "")
    name, text = read_source(x.source)
    d = load(); seen = hash_map(d)
    node, path = root_node(d), []
    if x.menu:
        node, path = find_node(d, x.menu)
        if not node: die(f"folder not found: {x.menu}  (see ./run.sh menu, or create it with --new-menu)")
    if x.new_menu:
        node, path = ensure_chain(d, node, path, [s.strip() for s in x.new_menu.split("/") if s.strip()], x.new_menu_bn.split("/"))
    elif not x.menu:
        _, label = detect(name, text, x.lang.lower())
        node, path = ensure_chain(d, node, path, [label])
    i, dup = add_file(d, name, text, x.source, path, seen, title=x.title, title_bn=tb, desc=x.desc, desc_bn=db,
                      category=x.category, tags=tags(x.tags), lang=x.lang.lower(), force=x.force)
    if dup: die(f"identical content already saved as {dup['id']} (use --force to add anyway)")
    save(d); print(f"✔ added {i}  {name}  →  {folder_label(d, path)}"); report(d)


def cmd_add_dir(x):
    root_path = os.path.abspath(os.path.expanduser(x.dir))
    if not os.path.isdir(root_path): die(f"not a directory: {x.dir}")
    excl = SKIP | {s.strip() for s in x.exclude.split(",") if s.strip()}
    d = load(); seen = hash_map(d)
    start, start_path = (find_node(d, x.menu) if x.menu else (root_node(d), []))
    if not start: die(f"folder not found: {x.menu}")
    base = x.title or os.path.basename(root_path.rstrip("/")) or "root"
    start, start_path = ensure_chain(d, start, start_path, [base])
    added = skipped = dup = 0
    for dirpath, dirnames, filenames in os.walk(root_path):
        dirnames[:] = sorted(dn for dn in dirnames if dn not in excl and not dn.startswith("."))
        rel = os.path.relpath(dirpath, root_path)
        segs = [] if rel == "." else rel.split(os.sep)
        node, path = ensure_chain(d, start, start_path, segs) if segs else (start, start_path)
        for fn in sorted(f for f in filenames if not f.startswith(".")):
            fp = os.path.join(dirpath, fn)
            try:
                with open(fp, "rb") as f: raw = f.read(MAX_BYTES + 1)
                if len(raw) > MAX_BYTES: raise ValueError
                text = raw.decode("utf-8-sig").replace("\r\n", "\n")
            except Exception: skipped += 1; continue
            i, dp = add_file(d, fn, text, fp, path, seen, category=x.category, force=x.force)
            if dp: dup += 1
            else: added += 1
    save(d)
    print(f"✔ imported {added} file(s) from {x.dir}  →  {folder_label(d, start_path)}")
    if skipped: print(f"  (skipped {skipped} binary / too-large / unreadable file(s))")
    if dup: print(f"  (skipped {dup} duplicate(s) already in Docs — use --force to add anyway)")
    report(d)


# ------------------------------------------------------------------ menu
def show_tree(d):
    cnt = {}
    for f in d["files"]:
        for m in f.get("menu_path", []): cnt[m] = cnt.get(m, 0) + 1
    loose = sum(1 for f in d["files"] if not f.get("menu_path"))

    def rec(ns, ind):
        for n in ns:
            print("  " * ind + f"{'└ ' if ind else ''}{n.get('en') or n.get('bn')} / {n.get('bn', '')}  [{n['id']}]  ({cnt.get(n['id'], 0)})")
            rec(n.get("children", []), ind + 1)
    print(f"Docs  ({len(d['files'])} files{f', {loose} at top level' if loose else ''})")
    rec(d["tree"], 1)


def cmd_menu(x):
    d = load(); changed = False
    if x.new:
        node, path = root_node(d), []
        if x.under:
            node, path = find_node(d, x.under)
            if not node: die(f"folder not found: {x.under}")
        node, path = ensure_chain(d, node, path, [s.strip() for s in x.new.split("/") if s.strip()], x.bn.split("/")); changed = True
        print("✔ folder ready:", folder_label(d, path))
    if x.move:
        f = find_file(d, x.move)
        if not f: die(f"file not found: {x.move}")
        node, path = find_node(d, x.to)
        if not node: die(f"folder not found: {x.to}")
        f["menu_path"] = path; f["updated_at"] = now(); changed = True
        print(f"✔ {x.move} → {folder_label(d, path)}")
    if x.move_menu:
        if not x.to and x.to != "": die("--to is required with --move-menu")
        src, sp = find_node(d, x.move_menu)
        if not src or not sp: die(f"folder not found: {x.move_menu}")
        dst, dp = find_node(d, x.to)
        if not dst: die(f"folder not found: {x.to}")
        if dp == sp: die("source and destination are the same folder")
        if dp[:len(sp)] == sp: die("cannot move a folder into itself or into its own subfolder")
        if any(c["id"] == src["id"] for c in dst.setdefault("children", [])): die("a folder with that id already exists at the destination")
        moved = detach(d["tree"], src["id"]); dst.setdefault("children", []).append(moved)
        # root_node() wraps d["tree"] by reference, so appending above already updated the tree when dst is root
        newp = dp + [src["id"]]; n = 0
        for f in d["files"]:
            mp = f.get("menu_path", [])
            if mp[:len(sp)] == sp: f["menu_path"] = newp + mp[len(sp):]; f["updated_at"] = now(); n += 1
        changed = True
        print(f"✔ folder moved: {folder_label(d, sp)} → {folder_label(d, newp)}  ({n} file(s) moved with it)")
    if x.rename:
        node, p = find_node(d, x.rename)
        if not node or not p: die(f"folder not found: {x.rename}")
        if not (x.en or x.bn): die("give --en and/or --bn")
        if x.en: node["en"] = x.en
        if x.bn: node["bn"] = x.bn
        changed = True; print("✔ renamed:", folder_label(d, p))
    if x.rm:
        node, p = find_node(d, x.rm)
        if not node or not p: die(f"folder not found: {x.rm}")
        if node.get("children") or any(p == f.get("menu_path", [])[:len(p)] for f in d["files"]):
            die("folder is not empty — move or delete its contents first")
        detach(d["tree"], node["id"]); changed = True; print("✔ folder deleted:", folder_label(d, p))
    if changed: save(d); report(d)
    else: show_tree(d)


def cmd_rm(x):
    d = load(); gone = 0
    for i in x.ids:
        f = find_file(d, i)
        if not f: print("  not found:", i); continue
        d["files"].remove(f); gone += 1
        try: os.remove(content_path(i))
        except OSError: pass
        print("✔ deleted", i, f["filename"])
    if gone: save(d); report(d)


def cmd_stats(x):
    d = load(); by = {}
    for f in d["files"]: by.setdefault(f.get("lang_label", f["lang"]), [0, 0, 0]); r = by[f.get("lang_label", f["lang"])]; r[0] += 1; r[1] += f.get("lines", 0); r[2] += f.get("bytes", 0)
    print(f"{len(d['files'])} files · {sum(r[1] for r in by.values()):,} lines · {sum(r[2] for r in by.values()) / 1048576:.2f} MB")
    for k, (n, l, b) in sorted(by.items(), key=lambda kv: -kv[1][0]): print(f"  {k:<12}{n:>6} files{l:>10,} lines{b / 1024:>10,.0f} KB")


# ------------------------------------------------------------------ migrate (one-time, from the old single-JSON "CodeCraft")
def cmd_migrate(x):
    with open(x.old, encoding="utf-8") as f: old = json.load(f)
    cur = load()
    if cur["files"] and not x.replace: die("Docs already has files — use --replace to overwrite it")
    d = new_index(); idmap, used = {}, set()
    root = next((n for n in old["menu"] if n["id"] == "codecraft"), None)

    def conv(n):
        base = re.sub(r"^c-", "", n["id"]) or slug(n.get("en", "f")); nid = base; k = 2
        while nid in used: nid = f"{base}-{k}"; k += 1
        used.add(nid); idmap[n["id"]] = nid
        out = {"id": nid, "bn": n.get("bn") or n.get("en", ""), "en": n.get("en") or n.get("bn", "")}
        kids = [conv(c) for c in n.get("children", [])]
        if kids: out["children"] = kids
        return out
    d["tree"] = [conv(c) for c in (root or {}).get("children", [])]
    if os.path.isdir(FILES):
        for fn in os.listdir(FILES):
            if fn.endswith(".txt"): os.remove(os.path.join(FILES, fn))
    os.makedirs(FILES, exist_ok=True); seen = {}
    for c in old.get("codes", []):
        path = [idmap[m] for m in c.get("menu_path", []) if m in idmap]
        if not path:
            _, path = ensure_chain(d, root_node(d), [], [c.get("lang_label") or c.get("lang", "Other")])
        m = re.match(r"^[A-Z]{3}-(\d{4})-(\d+)$", c["id"]); i = f"{PREFIX}-{m.group(1)}-{m.group(2)}" if m else next_id(d)
        if m: d["counters"][m.group(1)] = max(d["counters"].get(m.group(1), 0), int(m.group(2)))
        text = c["content"]; lang_key, label = detect(c["filename"], text, "")
        with open(content_path(i), "w", encoding="utf-8", newline="\n") as fh: fh.write(text)
        cat = c.get("category", "")
        e = prune({"id": i, "title": c.get("title") or c["filename"], "title_bn": c.get("title_bn", ""), "desc": c.get("desc", ""),
                   "desc_bn": c.get("desc_bn", ""), "filename": c["filename"], "lang": lang_key, "lang_label": label,
                   "ext": c.get("ext", ""), "lines": count_lines(text), "bytes": len(text.encode("utf-8")), "sha256": sha(text),
                   "menu_path": path, "category": "" if cat == "general" else cat, "tags": c.get("tags", []),
                   "source": c.get("source", ""), "created_at": c.get("created_at", now()), "updated_at": c.get("created_at", now())})
        e["menu_path"] = path; d["files"].append(e)
    save(d); print(f"✔ migrated {len(d['files'])} files, {len(idmap)} folders"); report(d)


# ------------------------------------------------------------------ main
def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = ap.add_subparsers(dest="cmd")
    a = sp.add_parser("add"); a.add_argument("source", nargs="?", default=""); a.add_argument("title", nargs="?", default=""); a.add_argument("desc", nargs="?", default="")
    a.add_argument("--bn", action="append", default=[]); a.add_argument("--title-bn", default=""); a.add_argument("--desc-bn", default="")
    a.add_argument("--menu", default=""); a.add_argument("--new-menu", default=""); a.add_argument("--new-menu-bn", default="")
    a.add_argument("--category", default=""); a.add_argument("--tags", default=""); a.add_argument("--lang", default=""); a.add_argument("--force", action="store_true")
    a = sp.add_parser("add-dir"); a.add_argument("dir"); a.add_argument("--menu", default=""); a.add_argument("--title", default="")
    a.add_argument("--category", default=""); a.add_argument("--exclude", default=""); a.add_argument("--force", action="store_true")
    a = sp.add_parser("menu"); a.add_argument("--new", default=""); a.add_argument("--bn", default=""); a.add_argument("--under", default="")
    a.add_argument("--move", default=""); a.add_argument("--move-menu", default="", dest="move_menu"); a.add_argument("--to", default=None)
    a.add_argument("--rename", default=""); a.add_argument("--en", default=""); a.add_argument("--rm", default="")
    a = sp.add_parser("rm"); a.add_argument("ids", nargs="+")
    sp.add_parser("stats"); sp.add_parser("check")
    a = sp.add_parser("migrate"); a.add_argument("old"); a.add_argument("--replace", action="store_true")
    x = ap.parse_args()
    if not x.cmd: ap.print_help(); return
    if x.cmd == "menu" and (x.move or x.move_menu) and x.to is None: die("--to is required")
    {"add": cmd_add, "add-dir": cmd_add_dir, "menu": cmd_menu, "rm": cmd_rm, "stats": cmd_stats, "migrate": cmd_migrate,
     "check": lambda _: report(load())}[x.cmd](x)


if __name__ == "__main__":
    main()

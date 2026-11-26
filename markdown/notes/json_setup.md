অবশ্যই। Markdown viewer-এর মতোই JSON-এর জন্য আলাদা responsive viewer তৈরি করা যায়—নোট/ফাইলের নাম, ফোল্ডার, ID এবং JSON-এর key/value দিয়ে সার্চ; JSON parse/validation; fold করা যায় এমন tree view; format, copy ও download—সবসহ।

এখানে JSON ফাইল রাখবেন `json/files/`-এ। Viewer হবে `json/`-এ, তাই viewer ও আপনার JSON নথি আলাদা থাকবে। **গোপন JSON ফাইল এখানে রাখবেন না**—`./run.sh serve` চালালে সার্ভারের ফাইলগুলো ব্রাউজারে পাওয়া যায়।

## ১. `scripts/json_setup.py` তৈরি করুন

এটি `json/files/` তৈরি করবে এবং JSON ফাইলগুলোর catalog বানাবে। আগের catalog থেকে ID ও প্রথম যুক্তের সময় ধরে রাখবে; JSON ফাইলগুলো পরিবর্তন করবে না।

```python name=scripts/json_setup.py
#!/usr/bin/env python3
"""Build a searchable index for JSON files in json/files/."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
JSON_ROOT = ROOT / "json"
FILES_ROOT = JSON_ROOT / "files"
CATALOG_PATH = JSON_ROOT / "catalog.json"

# Catalog-এ প্রতি ফাইলের searchable content সর্বোচ্চ এত অক্ষর রাখা হবে।
MAX_SEARCH_CHARS = 12_000


def local_iso(timestamp: float | None = None) -> str:
    value = datetime.now().astimezone() if timestamp is None else (
        datetime.fromtimestamp(timestamp).astimezone()
    )
    return value.isoformat(timespec="seconds")


def stable_id(relative_path: str) -> str:
    digest = hashlib.sha256(relative_path.encode("utf-8")).hexdigest()[:10].upper()
    return f"JSON-{digest}"


def previous_entries() -> dict[str, dict[str, Any]]:
    try:
        data = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}

    if not isinstance(data, dict) or not isinstance(data.get("files"), list):
        return {}

    return {
        item["path"]: item
        for item in data["files"]
        if isinstance(item, dict) and isinstance(item.get("path"), str)
    }


def flatten_for_search(value: Any, parts: list[str]) -> None:
    """Collect JSON keys and scalar values for catalog search."""
    if isinstance(value, dict):
        for key, child in value.items():
            parts.append(str(key))
            flatten_for_search(child, parts)
    elif isinstance(value, list):
        for child in value:
            flatten_for_search(child, parts)
    elif value is None:
        parts.append("null")
    elif isinstance(value, (str, int, float, bool)):
        parts.append(str(value))


def main() -> None:
    FILES_ROOT.mkdir(parents=True, exist_ok=True)
    (FILES_ROOT / ".gitkeep").touch(exist_ok=True)

    old = previous_entries()
    entries: list[dict[str, Any]] = []

    paths = sorted(
        path
        for path in FILES_ROOT.rglob("*")
        if path.is_file()
        and path.suffix.lower() == ".json"
        and not path.is_symlink()
    )

    for path in paths:
        relative_path = path.relative_to(FILES_ROOT).as_posix()
        old_entry = old.get(relative_path, {})
        stat = path.stat()

        search_parts = [path.name, relative_path]
        valid = True

        try:
            parsed = json.loads(path.read_text(encoding="utf-8-sig"))
            flatten_for_search(parsed, search_parts)
        except (UnicodeDecodeError, json.JSONDecodeError):
            # Invalid JSON-ও তালিকায় থাকবে, যাতে viewer-এ ত্রুটি দেখা যায়।
            valid = False

        folder = path.parent.relative_to(FILES_ROOT).as_posix()
        if folder == ".":
            folder = ""

        entries.append(
            {
                "id": old_entry.get("id") or stable_id(relative_path),
                "title": path.stem,
                "path": relative_path,
                "folder": folder,
                "bytes": stat.st_size,
                "valid": valid,
                "created_at": old_entry.get("created_at") or local_iso(),
                "updated_at": local_iso(stat.st_mtime),
                "search_text": " ".join(search_parts)[:MAX_SEARCH_CHARS],
            }
        )

    catalog = {
        "generated_at": local_iso(),
        "files": entries,
    }

    CATALOG_PATH.write_text(
        json.dumps(catalog, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"JSON catalog updated: {len(entries)} file(s).")


if __name__ == "__main__":
    main()
```

## ২. `json/index.html` তৈরি করুন

এই ফাইলটি JSON viewer-এর পূর্ণাঙ্গ পেজ। এতে root project-এর pine/brass রং, মোবাইল drawer ও bottom navigation, ফাইল সার্চ, JSON tree, validation এবং copy/download আছে।

```html name=json/index.html
<!doctype html>
<html lang="bn">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
  <meta name="color-scheme" content="light dark">
  <meta name="theme-color" content="#0f4c42">
  <title>JSON Viewer — MJ Ahmad</title>

  <style>
    :root {
      color-scheme: light dark;
      --bg: #f3f5f2;
      --panel: #fff;
      --ink: #17211d;
      --muted: #64716b;
      --line: #d9dfdb;
      --pine: #0f4c42;
      --pine-dark: #092f29;
      --brass: #b8862b;
      --selected: #e3eeea;
      --code: #101916;
      --code-ink: #d8e4df;
      --safe-bottom: env(safe-area-inset-bottom, 0px);
      font: 15px/1.6 "Hind Siliguri", "Noto Sans Bengali",
            "Kalpurush", "Nirmala UI", "Segoe UI", system-ui, sans-serif;
    }

    @media (prefers-color-scheme: dark) {
      :root {
        --bg: #0f1514;
        --panel: #161e1c;
        --ink: #e6ece9;
        --muted: #93a29c;
        --line: #26332f;
        --pine: #5fb59f;
        --pine-dark: #0b3a32;
        --brass: #d4a74a;
        --selected: #1e2d29;
        --code: #0c1210;
        --code-ink: #d8e4df;
      }
    }

    * { box-sizing: border-box; -webkit-tap-highlight-color: transparent; }
    html, body { width: 100%; height: 100%; }
    body { margin: 0; overflow: hidden; background: var(--bg); color: var(--ink); }
    button, input { font: inherit; }
    :focus-visible { outline: 2px solid var(--brass); outline-offset: 2px; }

    .topbar {
      position: relative;
      z-index: 50;
      height: 58px;
      display: flex;
      align-items: center;
      gap: 10px;
      padding: 7px 16px;
      background: var(--pine-dark);
      color: #f3f5f2;
    }

    .brand {
      display: flex;
      min-width: 178px;
      align-items: center;
      gap: 10px;
      color: inherit;
      text-decoration: none;
    }

    .brand-mark {
      width: 34px;
      height: 34px;
      display: grid;
      flex: none;
      place-items: center;
      border-radius: 9px;
      background: #0a3b33;
      color: var(--brass);
      font: 700 16px ui-monospace, monospace;
    }

    .brand-copy { min-width: 0; line-height: 1.2; }
    .brand-copy strong {
      display: block;
      overflow: hidden;
      font-size: 15px;
      text-overflow: ellipsis;
      white-space: nowrap;
    }
    .brand-copy small {
      display: block;
      margin-top: 3px;
      color: #ffffffbd;
      font-size: 11px;
    }

    .menu-toggle {
      display: none;
      width: 36px;
      height: 36px;
      flex: none;
      place-items: center;
      border: 0;
      border-radius: 8px;
      background: transparent;
      color: #fff;
      font-size: 21px;
      cursor: pointer;
    }

    #search {
      width: min(460px, 55vw);
      min-width: 150px;
      margin-left: auto;
      padding: 8px 12px;
      border: 1px solid #ffffff44;
      border-radius: 8px;
      outline: none;
      background: #ffffff1c;
      color: #fff;
      font: inherit;
      font-size: 14px;
    }

    #search::placeholder { color: #ffffffb3; }
    #search:focus { border-color: var(--brass); }

    .workspace {
      height: calc(100dvh - 58px);
      display: grid;
      grid-template-columns: 290px minmax(0, 1fr);
      min-height: 0;
    }

    .file-nav {
      min-height: 0;
      overflow: auto;
      padding: 12px 8px 24px;
      border-right: 1px solid var(--line);
      background: var(--panel);
      overscroll-behavior: contain;
    }

    .nav-heading {
      display: flex;
      align-items: center;
      justify-content: space-between;
      margin: 2px 8px 9px;
    }

    .nav-heading h2 {
      margin: 0;
      color: var(--muted);
      font-size: 12px;
      letter-spacing: .04em;
      text-transform: uppercase;
    }

    #result-count {
      margin: 0 8px 8px;
      color: var(--muted);
      font-size: 12px;
    }

    .note-list { display: grid; gap: 3px; }

    .file-item {
      display: block;
      width: 100%;
      min-width: 0;
      padding: 9px 10px;
      border: 0;
      border-radius: 8px;
      background: transparent;
      color: var(--ink);
      text-align: left;
      cursor: pointer;
    }

    .file-item:hover { background: var(--bg); }
    .file-item[aria-current="page"] {
      background: var(--selected);
      color: var(--pine);
      box-shadow: inset 3px 0 var(--brass);
    }

    .item-title {
      display: block;
      overflow: hidden;
      font-weight: 650;
      text-overflow: ellipsis;
      white-space: nowrap;
    }

    .item-meta {
      display: block;
      margin-top: 2px;
      overflow-wrap: anywhere;
      color: var(--muted);
      font-size: 11.5px;
      line-height: 1.45;
    }

    .content {
      min-width: 0;
      min-height: 0;
      overflow: auto;
      padding: 24px 28px calc(38px + var(--safe-bottom));
      overscroll-behavior: contain;
    }

    .content-inner { width: min(100%, 1100px); margin: 0 auto; }

    .welcome {
      padding: 54px 12px;
      color: var(--muted);
      text-align: center;
    }

    .welcome-mark {
      width: 56px;
      height: 56px;
      display: grid;
      margin: 0 auto 14px;
      place-items: center;
      border: 1px solid var(--line);
      border-radius: 16px;
      background: var(--panel);
      color: var(--pine);
      font-size: 25px;
    }

    .welcome h2 { margin: 0 0 5px; color: var(--ink); font-size: 21px; }
    .welcome p { max-width: 560px; margin: 0 auto; }

    .file-header {
      margin-bottom: 16px;
      padding-bottom: 15px;
      border-bottom: 1px solid var(--line);
    }

    .file-title {
      margin: 0;
      font-size: clamp(21px, 3vw, 30px);
      line-height: 1.35;
      overflow-wrap: anywhere;
    }

    .file-meta {
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      gap: 6px 12px;
      margin-top: 9px;
      color: var(--muted);
      font-size: 12px;
    }

    .file-id {
      padding: 1px 9px;
      border: 1px solid var(--line);
      border-radius: 20px;
      color: var(--pine);
      font: 11.5px ui-monospace, Menlo, Consolas, monospace;
    }

    .actions {
      display: flex;
      flex-wrap: wrap;
      gap: 7px;
      margin-top: 12px;
    }

    .action-button {
      min-height: 36px;
      padding: 6px 12px;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: var(--panel);
      color: var(--ink);
      cursor: pointer;
    }

    .action-button:hover { border-color: var(--pine); color: var(--pine); }

    .tree {
      padding: 14px;
      border: 1px solid var(--line);
      border-radius: 10px;
      background: var(--panel);
      overflow-wrap: anywhere;
    }

    .tree details { margin: 2px 0 2px 14px; }
    .tree > details { margin-left: 0; }

    .tree summary {
      width: fit-content;
      max-width: 100%;
      padding: 2px 5px;
      border-radius: 5px;
      cursor: pointer;
      overflow-wrap: anywhere;
    }

    .tree summary:hover { background: var(--selected); }
    .tree-line { margin: 3px 0 3px 18px; overflow-wrap: anywhere; }
    .tree-key { color: var(--pine); font-weight: 650; }
    .tree-string { color: #2e7d4f; overflow-wrap: anywhere; }
    .tree-number { color: #a45b18; }
    .tree-boolean { color: #7251a3; }
    .tree-null { color: var(--muted); font-style: italic; }
    .tree-punctuation { color: var(--muted); }
    .tree-empty { color: var(--muted); font-style: italic; }

    @media (prefers-color-scheme: dark) {
      .tree-string { color: #80c995; }
      .tree-number { color: #e6b66e; }
      .tree-boolean { color: #c4a4ef; }
    }

    .error-box {
      padding: 15px;
      border: 1px solid #b3412e66;
      border-radius: 9px;
      background: var(--panel);
      color: #b3412e;
      overflow-wrap: anywhere;
    }

    .message { margin: 15px 8px; color: var(--muted); text-align: center; }

    .mobile-nav { display: none; }

    @media (max-width: 820px) {
      .topbar { height: 52px; gap: 7px; padding: 6px 10px; }
      .brand { min-width: 0; gap: 7px; }
      .brand-mark { width: 32px; height: 32px; }
      .brand-copy strong { max-width: 130px; font-size: 14px; }
      .brand-copy small { display: none; }
      .menu-toggle { display: grid; }

      #search {
        width: auto;
        min-width: 0;
        flex: 1;
        margin-left: auto;
        padding: 7px 9px;
        font-size: 12.5px;
      }

      .workspace {
        height: calc(100dvh - 52px);
        display: block;
      }

      .file-nav {
        position: fixed;
        z-index: 45;
        top: 52px;
        bottom: calc(64px + var(--safe-bottom));
        left: 0;
        width: min(310px, 88vw);
        padding: 12px 9px;
        border-right: 1px solid var(--line);
        box-shadow: 5px 0 25px #0004;
        transform: translateX(-105%);
        transition: transform .2s ease;
      }

      .file-nav.on { transform: translateX(0); }

      .content {
        width: 100%;
        height: 100%;
        padding: 18px 13px calc(76px + var(--safe-bottom));
      }

      .tree { padding: 10px; }
      .tree details { margin-left: 8px; }
      .tree-line { margin-left: 10px; font-size: 13px; }

      .mobile-nav {
        position: fixed;
        z-index: 60;
        right: 0;
        bottom: 0;
        left: 0;
        height: calc(62px + var(--safe-bottom));
        display: grid;
        grid-template-columns: repeat(5, minmax(0, 1fr));
        align-items: start;
        padding: 5px 4px var(--safe-bottom);
        border-top: 1px solid var(--line);
        background: var(--panel);
        box-shadow: 0 -3px 16px #0000000d;
      }

      .mobile-nav a,
      .mobile-nav button {
        min-width: 0;
        height: 49px;
        display: flex;
        align-items: center;
        justify-content: center;
        flex-direction: column;
        gap: 1px;
        padding: 2px;
        border: 0;
        border-radius: 9px;
        background: transparent;
        color: var(--muted);
        font: inherit;
        font-size: 10.5px;
        line-height: 1.2;
        text-decoration: none;
        cursor: pointer;
      }

      .mobile-nav .active { color: var(--pine); font-weight: 650; }
      .mobile-nav .active .nav-icon { color: var(--brass); }
      .nav-icon { width: 23px; height: 23px; display: grid; place-items: center; font-size: 18px; }
    }

    @media (prefers-reduced-motion: reduce) {
      *, *::before, *::after {
        scroll-behavior: auto !important;
        transition-duration: .01ms !important;
      }
    }

    @media print {
      body { height: auto; overflow: visible; background: #fff; color: #111; }
      .topbar, .file-nav, .mobile-nav, .actions { display: none !important; }
      .workspace, .content { height: auto; display: block; overflow: visible; padding: 0; }
      .tree { border: 0; }
      .tree details:not([open]) > :not(summary) { display: block; }
    }
  </style>
</head>

<body>
  <header class="topbar">
    <button
      id="menu-toggle"
      class="menu-toggle"
      type="button"
      aria-label="JSON ফাইলের তালিকা খুলুন"
      aria-expanded="false"
      aria-controls="file-nav"
    >☰</button>

    <a class="brand" href="../" aria-label="মূল পাতা">
      <span class="brand-mark" aria-hidden="true">{ }</span>
      <span class="brand-copy">
        <strong>JSON Viewer</strong>
        <small>নিজের খাতা · MJ Ahmad</small>
      </span>
    </a>

    <input
      id="search"
      type="search"
      placeholder="ID, ফাইল, ফোল্ডার, key বা value…"
      aria-label="JSON ফাইল খুঁজুন"
      autocomplete="off"
      spellcheck="false"
    >
  </header>

  <main class="workspace">
    <nav id="file-nav" class="file-nav" aria-label="JSON ফাইলের তালিকা">
      <div class="nav-heading"><h2>JSON ফাইল</h2></div>
      <p id="result-count" aria-live="polite">তালিকা লোড হচ্ছে…</p>
      <div id="file-list" class="note-list"></div>
    </nav>

    <article id="content" class="content" tabindex="-1" aria-live="polite">
      <div class="content-inner">
        <div class="welcome">
          <div class="welcome-mark" aria-hidden="true">{ }</div>
          <h2>JSON নথি</h2>
          <p>ফাইল বাছুন অথবা ID, ফাইলের নাম, ফোল্ডার, key কিংবা value দিয়ে সার্চ করুন।</p>
        </div>
      </div>
    </article>
  </main>

  <nav class="mobile-nav" aria-label="প্রধান নেভিগেশন">
    <a href="../">
      <span class="nav-icon" aria-hidden="true">⌂</span>
      <span>মেইন সাইট</span>
    </a>
    <a href="../#/dash">
      <span class="nav-icon" aria-hidden="true">▦</span>
      <span>ড্যাশবোর্ড</span>
    </a>
    <a href="../learn/">
      <span class="nav-icon" aria-hidden="true">◆</span>
      <span>লার্নিং</span>
    </a>
    <a href="../terminal/">
      <span class="nav-icon" aria-hidden="true">&gt;_</span>
      <span>টার্মিনাল</span>
    </a>
    <button
      id="bottom-menu"
      class="active"
      type="button"
      aria-label="JSON ফাইলের মেনু"
      aria-expanded="false"
      aria-controls="file-nav"
    >
      <span class="nav-icon" aria-hidden="true">☰</span>
      <span>মেনু</span>
    </button>
  </nav>

  <script>
    (() => {
      "use strict";

      const fileNav = document.querySelector("#file-nav");
      const fileList = document.querySelector("#file-list");
      const resultCount = document.querySelector("#result-count");
      const content = document.querySelector("#content");
      const search = document.querySelector("#search");
      const menuToggle = document.querySelector("#menu-toggle");
      const bottomMenu = document.querySelector("#bottom-menu");

      let files = [];
      let selectedPath = "";
      let requestNumber = 0;

      const isMobile = () => window.matchMedia("(max-width: 820px)").matches;
      const normalize = value => String(value ?? "").toLocaleLowerCase().trim();

      function showMessage(parent, text, error = false) {
        const node = document.createElement("p");
        node.className = error ? "error-box" : "message";
        node.textContent = text;
        parent.replaceChildren(node);
      }

      function setMenuOpen(open) {
        fileNav.classList.toggle("on", open);
        menuToggle.setAttribute("aria-expanded", String(open));
        bottomMenu.setAttribute("aria-expanded", String(open));
      }

      function searchableText(file) {
        return [
          file.id,
          file.title,
          file.path,
          file.folder,
          file.search_text
        ].map(normalize).join(" ");
      }

      function renderList() {
        const terms = normalize(search.value).split(/\s+/).filter(Boolean);
        const matches = files.filter(file => {
          const text = searchableText(file);
          return terms.every(term => text.includes(term));
        });

        resultCount.textContent = `${matches.length}টি ফাইল`;
        fileList.replaceChildren();

        if (!matches.length) {
          showMessage(fileList, "মিল পাওয়া যায়নি। অন্য ID, নাম, key বা value দিয়ে খুঁজুন।");
          return;
        }

        for (const file of matches) {
          const button = document.createElement("button");
          button.className = "file-item";
          button.type = "button";
          button.setAttribute(
            "aria-current",
            file.path === selectedPath ? "page" : "false"
          );

          const title = document.createElement("span");
          title.className = "item-title";
          title.textContent = file.title || file.path;

          const meta = document.createElement("span");
          meta.className = "item-meta";
          meta.textContent = `${file.id} · ${file.path}`;

          button.append(title, meta);
          button.addEventListener("click", () => openFile(file));
          fileList.append(button);
        }
      }

      function dateText(value) {
        if (!value) return "—";
        const date = new Date(value);
        if (Number.isNaN(date.getTime())) return String(value);
        return new Intl.DateTimeFormat("bn-BD", {
          year: "numeric",
          month: "short",
          day: "numeric",
          hour: "2-digit",
          minute: "2-digit"
        }).format(date);
      }

      function safePath(path) {
        if (typeof path !== "string" || !path || path.startsWith("/")) {
          throw new Error("JSON ফাইলের path সঠিক নয়।");
        }
        const parts = path.split("/");
        if (parts.some(part => !part || part === "." || part === "..")) {
          throw new Error("JSON ফাইলের path নিরাপদ নয়।");
        }
        return parts.map(encodeURIComponent).join("/");
      }

      function appendText(parent, text, className) {
        const span = document.createElement("span");
        if (className) span.className = className;
        span.textContent = text;
        parent.append(span);
        return span;
      }

      function renderValue(parent, value, key, depth) {
        const prefix = document.createElement("span");
        prefix.className = "tree-line";

        if (key !== null) {
          appendText(prefix, `${JSON.stringify(String(key))}: `, "tree-key");
        }

        if (value !== null && typeof value === "object") {
          const isArray = Array.isArray(value);
          const entries = isArray
            ? value.map((child, index) => [String(index), child])
            : Object.entries(value);
          const label = isArray ? `Array(${entries.length})` : `Object(${entries.length})`;

          if (entries.length === 0) {
            appendText(prefix, isArray ? "[]" : "{}", "tree-empty");
            parent.append(prefix);
            return;
          }

          const details = document.createElement("details");
          details.open = depth < 1;

          const summary = document.createElement("summary");
          summary.append(prefix);
          appendText(summary, label, "tree-punctuation");
          details.append(summary);

          for (const [childKey, childValue] of entries) {
            renderValue(details, childValue, isArray ? null : childKey, depth + 1);
          }

          parent.append(details);
          return;
        }

        if (typeof value === "string") {
          appendText(prefix, JSON.stringify(value), "tree-string");
        } else if (typeof value === "number") {
          appendText(prefix, String(value), "tree-number");
        } else if (typeof value === "boolean") {
          appendText(prefix, String(value), "tree-boolean");
        } else {
          appendText(prefix, "null", "tree-null");
        }

        parent.append(prefix);
      }

      function showFile(data, file, prettyJson) {
        const inner = document.createElement("div");
        inner.className = "content-inner";

        const header = document.createElement("header");
        header.className = "file-header";

        const title = document.createElement("h1");
        title.className = "file-title";
        title.textContent = file.title || file.path;

        const meta = document.createElement("div");
        meta.className = "file-meta";

        const id = document.createElement("span");
        id.className = "file-id";
        id.textContent = file.id || "ID নেই";

        const path = document.createElement("span");
        path.textContent = `ফাইল: ${file.path}`;

        const created = document.createElement("span");
        created.textContent = `যুক্ত: ${dateText(file.created_at)}`;

        const updated = document.createElement("span");
        updated.textContent = `আপডেট: ${dateText(file.updated_at)}`;

        meta.append(id, path, created, updated);

        const actions = document.createElement("div");
        actions.className = "actions";

        const copyButton = document.createElement("button");
        copyButton.className = "action-button";
        copyButton.type = "button";
        copyButton.textContent = "Formatted JSON কপি";

        copyButton.addEventListener("click", async () => {
          try {
            await navigator.clipboard.writeText(prettyJson);
            copyButton.textContent = "কপি হয়েছে ✓";
          } catch {
            copyButton.textContent = "কপি করা যায়নি";
          }
          window.setTimeout(() => {
            copyButton.textContent = "Formatted JSON কপি";
          }, 1500);
        });

        const downloadButton = document.createElement("button");
        downloadButton.className = "action-button";
        downloadButton.type = "button";
        downloadButton.textContent = "ডাউনলোড";

        downloadButton.addEventListener("click", () => {
          const blob = new Blob([prettyJson], {
            type: "application/json;charset=utf-8"
          });
          const url = URL.createObjectURL(blob);
          const anchor = document.createElement("a");
          anchor.href = url;
          anchor.download = file.path.split("/").pop() || "data.json";
          anchor.click();
          window.setTimeout(() => URL.revokeObjectURL(url), 1000);
        });

        actions.append(copyButton, downloadButton);
        header.append(title, meta, actions);

        const tree = document.createElement("section");
        tree.className = "tree";
        tree.setAttribute("aria-label", "JSON tree");

        renderValue(tree, data, null, 0);
        inner.append(header, tree);
        content.replaceChildren(inner);
        document.title = `${file.title || "JSON"} — JSON Viewer`;
      }

      async function openFile(file) {
        const currentRequest = ++requestNumber;
        selectedPath = file.path;
        renderList();

        if (isMobile()) setMenuOpen(false);

        content.scrollTo({ top: 0, behavior: "smooth" });
        showMessage(content, "JSON ফাইল লোড হচ্ছে…");

        try {
          const path = safePath(file.path);
          const response = await fetch(`files/${path}`, { cache: "no-cache" });

          if (!response.ok) {
            throw new Error(`ফাইল লোড হয়নি (HTTP ${response.status})`);
          }

          const raw = await response.text();
          let data;

          try {
            data = JSON.parse(raw);
          } catch (error) {
            const detail = error instanceof Error ? error.message : String(error);
            throw new Error(`JSON parse error: ${detail}`);
          }

          if (currentRequest !== requestNumber) return;

          showFile(data, file, JSON.stringify(data, null, 2));
        } catch (error) {
          if (currentRequest !== requestNumber) return;
          showMessage(content, `ফাইল খোলা যায়নি: ${error.message || error}`, true);
        }
      }

      async function loadCatalog() {
        try {
          const response = await fetch("catalog.json", { cache: "no-cache" });
          if (!response.ok) {
            throw new Error(`catalog.json লোড হয়নি (HTTP ${response.status})`);
          }

          const catalog = await response.json();
          if (!catalog || !Array.isArray(catalog.files)) {
            throw new Error("catalog.json-এর format সঠিক নয়।");
          }

          files = catalog.files
            .filter(file =>
              file &&
              typeof file.path === "string" &&
              file.path.toLowerCase().endsWith(".json")
            )
            .sort((a, b) =>
              String(b.updated_at).localeCompare(String(a.updated_at)) ||
              String(a.title).localeCompare(String(b.title), "bn")
            );

          renderList();

          if (!files.length) {
            resultCount.textContent = "০টি JSON ফাইল";
            showMessage(
              fileList,
              "json/files/ ফোল্ডারে .json ফাইল রাখুন, তারপর catalog তৈরি করুন।"
            );
          }
        } catch (error) {
          resultCount.textContent = "তালিকা পাওয়া যায়নি";
          showMessage(
            fileList,
            `${error.message || error} — python3 scripts/json_setup.py --index-only চালান।`,
            true
          );
        }
      }

      search.addEventListener("input", renderList);

      menuToggle.addEventListener("click", () => {
        setMenuOpen(!fileNav.classList.contains("on"));
      });

      bottomMenu.addEventListener("click", () => {
        setMenuOpen(!fileNav.classList.contains("on"));
      });

      content.addEventListener("click", () => {
        if (isMobile() && fileNav.classList.contains("on")) {
          setMenuOpen(false);
        }
      });

      document.addEventListener("keydown", event => {
        if (event.key === "Escape" && fileNav.classList.contains("on")) {
          setMenuOpen(false);
          menuToggle.focus();
        }

        if (
          event.key === "/" &&
          !/INPUT|TEXTAREA/.test(event.target.tagName || "")
        ) {
          event.preventDefault();
          search.focus();
        }
      });

      window.addEventListener("resize", () => {
        if (!isMobile()) setMenuOpen(false);
      });

      loadCatalog();
    })();
  </script>
</body>
</html>
```

## ৩. JSON ফাইল রাখুন ও catalog তৈরি করুন

ফাইলের উদাহরণ কাঠামো:

```text
json/
├── index.html
├── catalog.json       # script তৈরি করবে
└── files/
    ├── profile.json
    └── projects/
        └── list.json
```

`json/files/`-এ আপনার `.json` ফাইল ও subfolder রাখুন। তারপর root directory থেকে চালান:

```bash
python3 scripts/json_setup.py
```

নতুন বা পরিবর্তিত JSON ফাইলের তালিকা হালনাগাদ করতে:

```bash
python3 scripts/json_setup.py --index-only
```

এটি JSON ফাইল পড়ে catalog বানাবে। JSON ভুল থাকলেও ফাইলটি তালিকায় থাকবে; viewer খুললে parse error দেখাবে।

## ৪. `./run.sh serve`-এর সাথে যুক্ত করুন

আপনার `run.sh`-এর `serve` branch-এ Markdown index তৈরির লাইনটি থাকলে তার পাশে JSON catalog তৈরির লাইন যোগ করুন:

```bash
python3 scripts/json_setup.py --index-only
```

ഉদാഹরণത്തിന്, `serve` branch-এর শুরুতে setup call-গুলো এমন হতে পারে:

```bash
python3 scripts/content_setup.py --index-only
python3 scripts/json_setup.py --index-only
```

বাকি `run.sh` অপরিবর্তিত রাখুন। এরপর:

```bash
./run.sh serve
```

ব্রাউজারে viewer খুলুন:

```text
http://127.0.0.1:8000/json/
```

**সার্চের নোট:** catalog-এ প্রতিটি JSON ফাইলের key/value থেকে সর্বোচ্চ ১২,০০০ অক্ষর search text রাখা হয়; বড় JSON ফাইলে তাই শেষের অংশের সব value search নাও হতে পারে। চাইলে `scripts/json_setup.py`-এর `MAX_SEARCH_CHARS` বাড়াতে পারেন।


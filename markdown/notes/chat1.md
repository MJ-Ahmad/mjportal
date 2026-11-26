এটি করতে `scripts/content_setup.py` এবং `markdown/index.html` আপডেট করুন। `run.sh`-এ আগে যোগ করা `python3 scripts/content_setup.py --index-only` অংশ থাকলে সেটি বদলানোর দরকার নেই—সার্ভার চালুর সময় সেটিই নোটের তালিকা আপডেট করবে।

নতুন index-এ প্রতিটি নোটের স্থায়ী ID, প্রথম তালিকাভুক্তির সময় এবং সর্বশেষ পরিবর্তনের সময় থাকবে। সার্চে ID, ফাইলের নাম, ফোল্ডার ও সম্পূর্ণ path মিলবে। কোড ব্লক প্রথমে কয়েক লাইন দেখাবে; বোতামে পুরোটা খোলা যাবে এবং কোড কপি করা যাবে।

### `scripts/content_setup.py` আপডেট করুন

আগের ফাইলটির সম্পূর্ণ কোডের বদলে এটি দিন। আগে থেকে থাকা extension-ভিত্তিক ফোল্ডার তৈরির কাজও এতে রাখা হয়েছে।

```python name=scripts/content_setup.py
#!/usr/bin/env python3
"""Create content folders and build a searchable Markdown notes index."""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

SECTIONS = (
    "All",
    "Health",
    "Learning",
    "Work",
    "Habits",
    "Relationships",
    "Faith",
    "Finance",
    "Reflection",
    "Other",
)

EXTENSIONS = (
    "md", "txt", "pdf", "docx", "html", "css", "js", "json", "csv",
    "py", "sh", "png", "jpg", "svg", "mp3", "mp4", "zip",
)


def now_iso() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def ensure_folder(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)
    (path / ".gitkeep").touch(exist_ok=True)


def learning_site_slugs() -> list[str]:
    learn_dir = ROOT / "learn"
    if not learn_dir.is_dir():
        return ["general"]

    slugs = sorted(
        p.name
        for p in learn_dir.iterdir()
        if p.is_dir() and not p.name.startswith(".") and p.name != "__pycache__"
    )
    return slugs or ["general"]


def create_content_folders() -> None:
    sections_root = ROOT / "content" / "sections"
    for section in SECTIONS:
        for extension in EXTENSIONS:
            ensure_folder(sections_root / section / extension)

    learning_root = ROOT / "content" / "learning-sites"
    for slug in learning_site_slugs():
        for extension in EXTENSIONS:
            ensure_folder(learning_root / slug / extension)


def stable_id(relative_path: str) -> str:
    digest = hashlib.sha256(relative_path.encode("utf-8")).hexdigest()[:10].upper()
    return f"NOTE-{digest}"


def load_previous_index(index_path: Path) -> dict[str, dict]:
    try:
        data = json.loads(index_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}

    if not isinstance(data, list):
        return {}

    return {
        item["path"]: item
        for item in data
        if isinstance(item, dict) and isinstance(item.get("path"), str)
    }


def refresh_markdown_index() -> None:
    markdown_root = ROOT / "markdown"
    notes_dir = markdown_root / "notes"
    index_path = markdown_root / "notes-index.json"
    notes_dir.mkdir(parents=True, exist_ok=True)

    starter = notes_dir / "README.md"
    if not starter.exists():
        starter.write_text(
            "# Markdown নোট\n\n"
            "এই ফোল্ডারে `.md` ফাইল রাখুন। "
            "`./run.sh serve` চালিয়ে `/markdown/` ঠিকানায় দেখুন।\n",
            encoding="utf-8",
        )

    previous = load_previous_index(index_path)
    files = []

    # .md এবং .MD—দুই ধরনের extension-ই খুঁজে পায়।
    note_paths = sorted(
        p for p in notes_dir.rglob("*")
        if p.is_file() and p.suffix.lower() == ".md"
    )

    for path in note_paths:
        relative_path = path.relative_to(notes_dir).as_posix()
        old_entry = previous.get(relative_path, {})
        stat = path.stat()

        try:
            modified_at = datetime.fromtimestamp(stat.st_mtime).astimezone().isoformat(
                timespec="seconds"
            )
        except (OSError, OverflowError, ValueError):
            modified_at = now_iso()

        files.append(
            {
                "id": old_entry.get("id") or stable_id(relative_path),
                "title": path.stem,
                "path": relative_path,
                "folder": path.parent.relative_to(notes_dir).as_posix()
                if path.parent != notes_dir
                else "",
                "created_at": old_entry.get("created_at") or now_iso(),
                "updated_at": modified_at,
            }
        )

    index_path.write_text(
        json.dumps(files, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Markdown index updated: {len(files)} note(s).")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Create content folders and refresh the Markdown notes index."
    )
    parser.add_argument(
        "--index-only",
        action="store_true",
        help="refresh the Markdown index without creating content extension folders",
    )
    args = parser.parse_args()

    if not args.index_only:
        create_content_folders()

    refresh_markdown_index()


if __name__ == "__main__":
    main()
```

### `markdown/index.html` আপডেট করুন

আগের viewer ফাইলটির সম্পূর্ণ কোডের বদলে এটি দিন। সার্চ ফলাফলে ID, ফাইলের নাম, ফোল্ডার ও path দেখা যাবে। কোনো ফল বাছলে নোটের metadata-সহ কনটেন্ট খুলবে।

```html name=markdown/index.html
<!doctype html>
<html lang="bn">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="color-scheme" content="light dark">
  <title>Markdown নোট</title>
  <style>
    :root {
      color-scheme: light dark;
      font: 16px/1.65 system-ui, sans-serif;
      --bg: #f3f6f4;
      --panel: #fff;
      --ink: #17211d;
      --muted: #64716b;
      --line: #d9e0db;
      --accent: #12604f;
      --code: #101916;
      --code-ink: #e4eee8;
    }

    @media (prefers-color-scheme: dark) {
      :root {
        --bg: #111715;
        --panel: #19211e;
        --ink: #e7eee9;
        --muted: #a0ada6;
        --line: #303b35;
        --accent: #79c7ae;
        --code: #0c1210;
        --code-ink: #e4eee8;
      }
    }

    * { box-sizing: border-box; }
    body { margin: 0; background: var(--bg); color: var(--ink); }

    header {
      position: sticky;
      top: 0;
      z-index: 2;
      padding: 16px 20px;
      background: var(--accent);
      color: #fff;
      box-shadow: 0 2px 12px #0002;
    }

    header h1 { margin: 0 0 8px; font-size: 1.35rem; }
    #search {
      display: block;
      width: min(100%, 680px);
      padding: 10px 12px;
      border: 0;
      border-radius: 9px;
      font: inherit;
    }

    main {
      display: grid;
      grid-template-columns: minmax(230px, 320px) minmax(0, 1fr);
      min-height: calc(100dvh - 112px);
    }

    nav {
      position: sticky;
      top: 112px;
      align-self: start;
      max-height: calc(100dvh - 112px);
      overflow: auto;
      padding: 14px;
      border-right: 1px solid var(--line);
    }

    #result-count { margin: 0 0 8px; color: var(--muted); font-size: .9rem; }

    nav button {
      display: block;
      width: 100%;
      margin: 6px 0;
      padding: 10px;
      border: 1px solid var(--line);
      border-radius: 9px;
      background: var(--panel);
      color: var(--ink);
      text-align: left;
      cursor: pointer;
      overflow-wrap: anywhere;
    }

    nav button:hover,
    nav button[aria-current="page"] {
      border-color: var(--accent);
      box-shadow: inset 3px 0 var(--accent);
    }

    .item-title { display: block; font-weight: 650; }
    .item-meta {
      display: block;
      margin-top: 3px;
      color: var(--muted);
      font-size: .78rem;
      line-height: 1.45;
    }

    article {
      width: min(100%, 1000px);
      margin: 0 auto;
      padding: clamp(16px, 4vw, 36px);
      overflow-wrap: anywhere;
    }

    article img { max-width: 100%; height: auto; }
    article table { display: block; max-width: 100%; overflow-x: auto; border-collapse: collapse; }
    article th, article td { padding: 7px 10px; border: 1px solid var(--line); }
    article a { color: var(--accent); }

    .note-meta {
      display: flex;
      flex-wrap: wrap;
      gap: 6px 14px;
      margin: 10px 0 22px;
      color: var(--muted);
      font-size: .88rem;
    }

    .note-id {
      padding: 1px 8px;
      border: 1px solid var(--line);
      border-radius: 20px;
      font-family: ui-monospace, monospace;
    }

    .code-card {
      position: relative;
      margin: 16px 0;
      border: 1px solid #ffffff20;
      border-radius: 10px;
      overflow: hidden;
      background: var(--code);
      color: var(--code-ink);
    }

    .code-tools {
      display: flex;
      justify-content: flex-end;
      gap: 8px;
      padding: 7px 9px;
      border-bottom: 1px solid #ffffff1a;
    }

    .code-tools button {
      padding: 4px 10px;
      border: 1px solid #ffffff35;
      border-radius: 7px;
      background: #ffffff10;
      color: inherit;
      font: inherit;
      font-size: .82rem;
      cursor: pointer;
    }

    .code-card pre {
      max-height: 5.4em;
      margin: 0;
      padding: 12px 14px;
      overflow: hidden;
      tab-size: 2;
      white-space: pre;
      font: .88rem/1.55 ui-monospace, SFMono-Regular, Consolas, monospace;
    }

    .code-card.expanded pre {
      max-height: min(70vh, 900px);
      overflow: auto;
    }

    .code-card code { font: inherit; }

    .message { color: var(--muted); padding: 12px 4px; }

    @media (max-width: 700px) {
      header { padding: 12px; }
      main { display: flex; flex-direction: column; min-height: auto; }
      nav {
        position: static;
        max-height: 32dvh;
        border-right: 0;
        border-bottom: 1px solid var(--line);
        padding: 10px 12px;
      }
      article { padding: 18px 14px 32px; }
      .code-card pre { font-size: .8rem; }
    }
  </style>
</head>
<body>
  <header>
    <h1>Markdown নোট</h1>
    <input
      id="search"
      type="search"
      placeholder="ID, ফাইল, ফোল্ডার বা path দিয়ে খুঁজুন…"
      aria-label="নোট খুঁজুন"
      autocomplete="off"
    >
  </header>

  <main>
    <nav id="file-list" aria-label="Markdown নোটের তালিকা">
      <p class="message">তালিকা লোড হচ্ছে…</p>
    </nav>
    <article id="content" aria-live="polite">
      <p class="message">তালিকা থেকে একটি নোট বাছুন।</p>
    </article>
  </main>

  <script src="https://cdn.jsdelivr.net/npm/marked@15.0.7/marked.min.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/dompurify@3.2.6/dist/purify.min.js"></script>
  <script>
    (() => {
      "use strict";

      const list = document.querySelector("#file-list");
      const content = document.querySelector("#content");
      const search = document.querySelector("#search");
      let files = [];
      let selectedPath = "";

      const normalize = value => String(value || "").toLocaleLowerCase();

      function showMessage(parent, text) {
        const p = document.createElement("p");
        p.className = "message";
        p.textContent = text;
        parent.replaceChildren(p);
      }

      function renderList() {
        const query = normalize(search.value.trim());
        const matches = files.filter(file => {
          const searchable = [
            file.id,
            file.title,
            file.path,
            file.folder,
            file.path.split("/").pop()
          ].map(normalize).join(" ");
          return !query || searchable.includes(query);
        });

        const count = document.createElement("p");
        count.id = "result-count";
        count.textContent = `${matches.length}টি নোট`;
        list.replaceChildren(count);

        if (!matches.length) {
          const empty = document.createElement("p");
          empty.className = "message";
          empty.textContent = "মিল পাওয়া যায়নি। অন্য ID, নাম বা ফোল্ডার দিয়ে খুঁজুন।";
          list.append(empty);
          return;
        }

        for (const file of matches) {
          const button = document.createElement("button");
          button.type = "button";
          button.setAttribute("aria-current", file.path === selectedPath ? "page" : "false");

          const title = document.createElement("span");
          title.className = "item-title";
          title.textContent = file.title;

          const meta = document.createElement("span");
          meta.className = "item-meta";
          meta.textContent = `${file.id} · ${file.path}`;

          button.append(title, meta);
          button.addEventListener("click", () => openNote(file));
          list.append(button);
        }
      }

      function formatDate(value) {
        if (!value) return "—";
        const date = new Date(value);
        return Number.isNaN(date.getTime()) ? value : date.toLocaleString();
      }

      function addCodeControls(root) {
        root.querySelectorAll("pre").forEach(pre => {
          const card = document.createElement("div");
          card.className = "code-card";

          const tools = document.createElement("div");
          tools.className = "code-tools";

          const code = pre.querySelector("code");
          const codeText = code ? code.textContent : pre.textContent;
          const lineCount = codeText.replace(/\n$/, "").split("\n").length;

          const toggle = document.createElement("button");
          toggle.type = "button";
          toggle.textContent = lineCount > 3
            ? `আরও দেখুন · ${lineCount} লাইন`
            : "কোড";

          toggle.addEventListener("click", () => {
            const expanded = card.classList.toggle("expanded");
            toggle.textContent = expanded ? "সংকুচিত করুন" : `আরও দেখুন · ${lineCount} লাইন`;
          });

          const copy = document.createElement("button");
          copy.type = "button";
          copy.textContent = "কপি";

          copy.addEventListener("click", async () => {
            try {
              await navigator.clipboard.writeText(codeText);
              copy.textContent = "কপি হয়েছে ✓";
            } catch {
              const textarea = document.createElement("textarea");
              textarea.value = codeText;
              textarea.style.position = "fixed";
              textarea.style.opacity = "0";
              document.body.append(textarea);
              textarea.select();
              document.execCommand("copy");
              textarea.remove();
              copy.textContent = "কপি হয়েছে ✓";
            }
            setTimeout(() => { copy.textContent = "কপি"; }, 1400);
          });

          tools.append(toggle, copy);
          pre.replaceWith(card);
          card.append(tools, pre);
        });
      }

      async function openNote(file) {
        selectedPath = file.path;
        renderList();

        try {
          const encodedPath = file.path.split("/").map(encodeURIComponent).join("/");
          const response = await fetch(`notes/${encodedPath}`, { cache: "no-cache" });
          if (!response.ok) throw new Error(`HTTP ${response.status}`);

          const markdown = await response.text();
          if (!window.marked || !window.DOMPurify) {
            throw new Error("Markdown renderer লোড হয়নি। ইন্টারনেট সংযোগ পরীক্ষা করুন।");
          }

          const rendered = DOMPurify.sanitize(marked.parse(markdown));
          content.innerHTML = `
            <h1></h1>
            <div class="note-meta">
              <span class="note-id"></span>
              <span class="note-path"></span>
              <span class="note-created"></span>
              <span class="note-updated"></span>
            </div>
            <div class="markdown-body"></div>
          `;

          content.querySelector("h1").textContent = file.title;
          content.querySelector(".note-id").textContent = file.id;
          content.querySelector(".note-path").textContent = file.path;
          content.querySelector(".note-created").textContent =
            `যুক্ত: ${formatDate(file.created_at)}`;
          content.querySelector(".note-updated").textContent =
            `আপডেট: ${formatDate(file.updated_at)}`;
          content.querySelector(".markdown-body").innerHTML = rendered;

          addCodeControls(content);
          document.title = `${file.title} — Markdown নোট`;
        } catch (error) {
          showMessage(content, `নোট খোলা যায়নি: ${error.message}`);
        }
      }

      search.addEventListener("input", renderList);

      fetch("notes-index.json", { cache: "no-cache" })
        .then(response => {
          if (!response.ok) throw new Error(`HTTP ${response.status}`);
          return response.json();
        })
        .then(data => {
          files = Array.isArray(data) ? data : [];
          renderList();

          if (!files.length) {
            showMessage(content, "markdown/notes/ ফোল্ডারে .md ফাইল রাখুন।");
          }
        })
        .catch(error => {
          showMessage(list, `তালিকা লোড হয়নি: ${error.message}`);
        });
    })();
  </script>
</body>
</html>
```

### চালিয়ে দেখুন

রিপোর মূল ফোল্ডার থেকে সার্ভার বন্ধ করে আবার চালান:

```bash
python3 scripts/content_setup.py --index-only
./run.sh serve
```

তারপর মোবাইল বা কম্পিউটারের ব্রাউজারে খুলুন:

```text
http://127.0.0.1:8000/markdown/
```

`markdown/notes/`-এ নতুন নোট যোগ করলে index হালনাগাদ করতে সার্ভার পুনরায় চালান, অথবা সার্ভার চালু রেখেই `python3 scripts/content_setup.py --index-only` চালিয়ে পেজ রিফ্রেশ করুন। কোডের “আরও দেখুন” বোতাম পুরো code block খোলে; “কপি” পুরো কোড কপি করে।

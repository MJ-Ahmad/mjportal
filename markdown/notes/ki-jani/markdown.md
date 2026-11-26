নিচের সংযোজনগুলো বর্তমান ড্যাশবোর্ডের ফাইল বা ডেটা বদলাবে না। `./run.sh` আগের মতোই চলবে; নতুন `./run.sh serve` কমান্ড দিলে Markdown viewer চালু হবে। viewer থাকবে `http://127.0.0.1:8000/markdown/` ঠিকানায়।

> **দ্রষ্টব্য:** `content/`-এর extension ফোল্ডারগুলো ফাইল সাজিয়ে রাখার কাঠামো। এগুলো বর্তমান ড্যাশবোর্ডে স্বয়ংক্রিয়ভাবে এন্ট্রি তৈরি করবে না। `markdown/notes/`-এ রাখা `.md` ফাইলগুলো viewer-এ দেখা যাবে। `http.server` চালালে সার্ভারের সব ফাইল প্রকাশিত হয়—ব্যক্তিগত বা গোপন ফাইল ওই ডিরেক্টরিগুলোতে রাখবেন না।

### ১. ফোল্ডার তৈরির Python স্ক্রিপ্ট

নতুন `scripts/content_setup.py` ফাইল তৈরি করে এই কোড দিন। স্ক্রিপ্টটি আগে থেকে থাকা ফাইল মুছবে বা বদলাবে না; দরকারি ফোল্ডার ও `.gitkeep` ফাইল না থাকলেই তৈরি করবে।

```python name=scripts/content_setup.py
#!/usr/bin/env python3
"""Create content folders and refresh the Markdown viewer index without overwriting notes."""

from __future__ import annotations

import argparse
import json
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

# Folder names are extensions without the leading dot.
EXTENSIONS = (
    "md",
    "txt",
    "pdf",
    "docx",
    "html",
    "css",
    "js",
    "json",
    "csv",
    "py",
    "sh",
    "png",
    "jpg",
    "svg",
    "mp3",
    "mp4",
    "zip",
)


def ensure_folder(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)
    (path / ".gitkeep").touch(exist_ok=True)


def learning_site_slugs() -> list[str]:
    learn_dir = ROOT / "learn"
    if not learn_dir.is_dir():
        return ["general"]

    # Use existing learning-site folders as slugs; do not modify learn/.
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


def refresh_markdown_index() -> None:
    notes_dir = ROOT / "markdown" / "notes"
    notes_dir.mkdir(parents=True, exist_ok=True)

    # Add a starter note only when it does not already exist.
    starter = notes_dir / "README.md"
    if not starter.exists():
        starter.write_text(
            "# Markdown নোট\n\n"
            "এই ফোল্ডারে `.md` ফাইল রাখুন। "
            "`./run.sh serve` চালিয়ে `/markdown/` ঠিকানায় দেখুন।\n",
            encoding="utf-8",
        )

    files = []
    for path in sorted(notes_dir.rglob("*.md")):
        if path.is_file():
            files.append(
                {
                    "title": path.stem,
                    "path": path.relative_to(notes_dir).as_posix(),
                }
            )

    index_path = ROOT / "markdown" / "notes-index.json"
    index_path.write_text(
        json.dumps(files, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Create section/learning folders and index Markdown notes."
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
    print("Content folders and Markdown index are ready.")


if __name__ == "__main__":
    main()
```

### ২. Markdown viewer

নতুন `markdown/index.html` ফাইল তৈরি করুন। এটি `markdown/notes/`-এর `.md` ফাইলগুলো তালিকাভুক্ত করবে, সার্চ করতে দেবে এবং Markdown হিসেবে দেখাবে। Markdown rendering-এর জন্য CDN থেকে `marked` ও `DOMPurify` লোড হয়; তাই প্রথমবার viewer খোলার সময় ইন্টারনেট সংযোগ থাকা দরকার।

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
      --bg: #f4f6f4;
      --panel: #fff;
      --ink: #17211d;
      --muted: #64716b;
      --line: #d9e0db;
      --accent: #12604f;
    }
    @media (prefers-color-scheme: dark) {
      :root {
        --bg: #111715;
        --panel: #19211e;
        --ink: #e7eee9;
        --muted: #a0ada6;
        --line: #303b35;
        --accent: #79c7ae;
      }
    }
    * { box-sizing: border-box; }
    body { margin: 0; background: var(--bg); color: var(--ink); }
    header { padding: 18px 22px; background: var(--accent); color: white; }
    header h1 { margin: 0 0 8px; font-size: 1.4rem; }
    header input {
      width: min(100%, 520px); padding: 10px 12px; border: 0;
      border-radius: 8px; font: inherit;
    }
    main {
      display: grid; grid-template-columns: minmax(210px, 300px) minmax(0, 1fr);
      min-height: calc(100vh - 105px);
    }
    nav { padding: 16px; border-right: 1px solid var(--line); }
    nav button {
      display: block; width: 100%; margin: 4px 0; padding: 9px 10px;
      border: 1px solid var(--line); border-radius: 7px;
      background: var(--panel); color: var(--ink); text-align: left;
      cursor: pointer; overflow-wrap: anywhere;
    }
    nav button:hover, nav button[aria-current="page"] {
      border-color: var(--accent); color: var(--accent);
    }
    article {
      width: min(100%, 1000px); margin: auto; padding: 26px;
      overflow-wrap: anywhere;
    }
    article img { max-width: 100%; height: auto; }
    article pre { padding: 14px; overflow: auto; border-radius: 8px; background: var(--bg); }
    article code { font-family: ui-monospace, monospace; }
    article table { display: block; max-width: 100%; overflow-x: auto; border-collapse: collapse; }
    article th, article td { padding: 7px 10px; border: 1px solid var(--line); }
    a { color: var(--accent); }
    .message { color: var(--muted); padding: 12px 4px; }
    @media (max-width: 700px) {
      main { grid-template-columns: 1fr; }
      nav { border-right: 0; border-bottom: 1px solid var(--line); }
      article { padding: 18px; }
    }
  </style>
</head>
<body>
  <header>
    <h1>Markdown নোট</h1>
    <input id="search" type="search" placeholder="নোট খুঁজুন…" aria-label="নোট খুঁজুন">
  </header>

  <main>
    <nav id="file-list" aria-label="Markdown ফাইল">
      <p class="message">নোটের তালিকা লোড হচ্ছে…</p>
    </nav>
    <article id="content">
      <p class="message">একটি নোট নির্বাচন করুন।</p>
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

      function showMessage(parent, text) {
        const p = document.createElement("p");
        p.className = "message";
        p.textContent = text;
        parent.replaceChildren(p);
      }

      function renderList() {
        const query = search.value.trim().toLocaleLowerCase();
        const matches = files.filter(file =>
          file.title.toLocaleLowerCase().includes(query) ||
          file.path.toLocaleLowerCase().includes(query)
        );

        list.replaceChildren();
        if (!matches.length) {
          showMessage(list, "কোনো Markdown ফাইল পাওয়া যায়নি।");
          return;
        }

        for (const file of matches) {
          const button = document.createElement("button");
          button.type = "button";
          button.textContent = file.title;
          button.title = file.path;
          button.addEventListener("click", () => openNote(file, button));
          list.append(button);
        }
      }

      async function openNote(file, button) {
        try {
          const encodedPath = file.path
            .split("/")
            .map(encodeURIComponent)
            .join("/");
          const response = await fetch(`notes/${encodedPath}`, { cache: "no-cache" });
          if (!response.ok) throw new Error(`HTTP ${response.status}`);

          const markdown = await response.text();
          if (!window.marked || !window.DOMPurify) {
            throw new Error("Markdown renderer লোড হয়নি; ইন্টারনেট সংযোগ পরীক্ষা করুন।");
          }

          document.querySelectorAll("#file-list button")
            .forEach(item => item.removeAttribute("aria-current"));
          button.setAttribute("aria-current", "page");
          content.innerHTML = DOMPurify.sanitize(marked.parse(markdown));
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
          if (!files.length) showMessage(content, "markdown/notes/ ফোল্ডারে .md ফাইল রাখুন।");
        })
        .catch(error => showMessage(list, `তালিকা লোড হয়নি: ${error.message}`));
    })();
  </script>
</body>
</html>
```

### ৩. `run.sh`-এ নতুন `serve` কমান্ড যোগ

বর্তমান `run.sh`-এর `cd "$(dirname "$0")"` লাইনের **ঠিক পরে** এই অংশটি যোগ করুন। বাকি বর্তমান কোড অপরিবর্তিত রাখুন:

```bash name=run.sh
# New optional Markdown viewer command.
# Existing ./run.sh and ./run.sh PORT behavior remains unchanged.
if [[ "${1:-}" == "serve" ]]; then
  shift
  PORT="${1:-8000}"
  BIND="${KHATA_BIND:-127.0.0.1}"

  python3 scripts/content_setup.py --index-only

  if ! python3 life.py validate; then
    echo "Fix the errors above before starting the dashboard."
    exit 1
  fi

  echo ""
  echo "Dashboard        : http://127.0.0.1:${PORT}"
  echo "Markdown viewer  : http://127.0.0.1:${PORT}/markdown/"
  echo "Stop             : Ctrl+C"
  echo ""
  exec python3 -m http.server "$PORT" --bind "$BIND"
fi
```

### চালানোর নিয়ম

প্রথমবার extension ফোল্ডারগুলো তৈরি করুন:

```bash
python3 scripts/content_setup.py
```

Markdown ফাইলগুলো এখানে রাখুন:

```text
markdown/notes/
```

উদাহরণ:

```text
markdown/notes/reading/book-notes.md
markdown/notes/projects/plan.md
```

তারপর সার্ভার চালিয়ে ব্রাউজারে viewer-এর URL খুলুন:

```bash
./run.sh serve
# http://127.0.0.1:8000/markdown/
```

অন্য পোর্টে চালাতে পারেন:

```bash
./run.sh serve 8080
# http://127.0.0.1:8080/markdown/
```

নতুন Markdown ফাইল যোগ করার পর `./run.sh serve` আবার চালালে তালিকা পুনরায় তৈরি হবে। পুরোনো `./run.sh` বা `./run.sh 8080` ব্যবহারের আচরণ আগের মতোই থাকবে।

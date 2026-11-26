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

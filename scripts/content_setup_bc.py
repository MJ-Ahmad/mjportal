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

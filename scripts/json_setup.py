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

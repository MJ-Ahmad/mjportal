#!/usr/bin/env python3
"""Local event documentation manager and static viewer index builder."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
EVENTS_DIR = ROOT / "events"
AUDIT_FILE = EVENTS_DIR / "audit.jsonl"
INDEX_FILE = EVENTS_DIR / "data.json"


def now_iso() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    temporary.replace(path)


def safe_slug(value: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", value.strip().lower()).strip("-")
    if not slug:
        slug = f"event-{datetime.now():%Y%m%d-%H%M%S}"
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]{0,69}", slug):
        raise ValueError("Slug-এ শুধু ইংরেজি অক্ষর, সংখ্যা ও hyphen ব্যবহার করুন।")
    return slug


def event_file(slug: str) -> Path:
    slug = safe_slug(slug)
    path = (EVENTS_DIR / slug / "event.json").resolve()
    if not path.is_relative_to(EVENTS_DIR.resolve()):
        raise ValueError("Invalid event path.")
    if not path.is_file():
        raise FileNotFoundError(f"ইভেন্ট পাওয়া যায়নি: {slug}")
    return path


def load_event(slug: str) -> tuple[Path, dict[str, Any]]:
    path = event_file(slug)
    data = json.loads(path.read_text(encoding="utf-8"))
    return path, data


def save_event(path: Path, data: dict[str, Any]) -> None:
    data["updated_at"] = now_iso()
    write_json(path, data)


def log_event(event_id: str, action: str, details: dict[str, Any]) -> None:
    EVENTS_DIR.mkdir(parents=True, exist_ok=True)
    record = {
        "audit_id": f"AUD-{uuid.uuid4().hex[:12].upper()}",
        "event_id": event_id,
        "timestamp": now_iso(),
        "actor": "local-user",
        "action": action,
        "details": details,
    }
    with AUDIT_FILE.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=False) + "\n")


def default_requirements() -> list[dict[str, Any]]:
    titles = [
        ("প্রয়োজন ও উদ্দেশ্য", "planning"),
        ("অংশগ্রহণকারী ও যোগাযোগ", "people"),
        ("তারিখ, সময় ও স্থান", "logistics"),
        ("এজেন্ডা ও সময়সূচি", "planning"),
        ("প্রয়োজনীয় উপকরণ ও নথি", "materials"),
        ("খরচ ও অনুমোদন", "finance"),
        ("জরুরি পরিকল্পনা ও ঝুঁকি", "risk"),
    ]
    return [
        {
            "id": f"REQ-{index:03d}",
            "title": title,
            "category": category,
            "required": True,
            "status": "pending",
            "notes": "",
            "evidence_file_ids": [],
        }
        for index, (title, category) in enumerate(titles, start=1)
    ]


def new_event(args: argparse.Namespace) -> None:
    slug = safe_slug(args.slug or args.title)
    folder = EVENTS_DIR / slug
    if folder.exists():
        raise FileExistsError(f"এই event folder আগে থেকেই আছে: events/{slug}")

    event_id = f"EVT-{datetime.now():%Y%m%d}-{uuid.uuid4().hex[:6].upper()}"
    created = now_iso()

    data = {
        "schema": "mj-event/v1",
        "id": event_id,
        "slug": slug,
        "title": args.title,
        "event_type": args.type or "general",
        "status": "planning",
        "date": args.date or "",
        "start_time": "",
        "end_time": "",
        "timezone": "Asia/Dhaka",
        "venue": "",
        "owner": "",
        "purpose": "",
        "description": "",
        "agenda": [
            {
                "id": "AG-001",
                "title": "উদ্দেশ্য ও প্রত্যাশিত ফলাফল",
                "start_time": "",
                "duration_minutes": 10,
                "owner": "",
                "status": "planned",
                "notes": "",
            }
        ],
        "requirements": default_requirements(),
        "files": [],
        "notes": [],
        "created_at": created,
        "updated_at": created,
    }

    (folder / "files").mkdir(parents=True)
    write_json(folder / "event.json", data)
    log_event(event_id, "event_created", {"slug": slug, "title": args.title})
    build_index()
    print(f"ইভেন্ট তৈরি হয়েছে: events/{slug}/event.json")
    print(f"ID: {event_id}")


def add_agenda(args: argparse.Namespace) -> None:
    path, data = load_event(args.slug)
    agenda = data.setdefault("agenda", [])
    item_id = f"AG-{len(agenda) + 1:03d}"

    item = {
        "id": item_id,
        "title": args.title,
        "start_time": args.time or "",
        "duration_minutes": args.duration,
        "owner": args.owner or "",
        "status": "planned",
        "notes": args.notes or "",
    }
    agenda.append(item)
    save_event(path, data)
    log_event(data["id"], "agenda_added", item)
    build_index()
    print(f"Agenda যোগ হয়েছে: {item_id}")


def add_requirement(args: argparse.Namespace) -> None:
    path, data = load_event(args.slug)
    requirements = data.setdefault("requirements", [])
    item_id = f"REQ-{len(requirements) + 1:03d}"

    item = {
        "id": item_id,
        "title": args.title,
        "category": args.category or "general",
        "required": not args.optional,
        "status": "pending",
        "notes": "",
        "evidence_file_ids": [],
    }
    requirements.append(item)
    save_event(path, data)
    log_event(data["id"], "requirement_added", item)
    build_index()
    print(f"Requirement যোগ হয়েছে: {item_id}")


def set_requirement(args: argparse.Namespace) -> None:
    path, data = load_event(args.slug)
    requirement = next(
        (item for item in data.get("requirements", []) if item.get("id") == args.id),
        None,
    )
    if requirement is None:
        raise ValueError(f"Requirement ID পাওয়া যায়নি: {args.id}")

    previous = requirement.get("status", "pending")
    requirement["status"] = args.status
    if args.note:
        requirement["notes"] = args.note

    save_event(path, data)
    log_event(
        data["id"],
        "requirement_status_changed",
        {
            "requirement_id": args.id,
            "from": previous,
            "to": args.status,
            "note": args.note or "",
        },
    )
    build_index()
    print(f"{args.id}: {previous} → {args.status}")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def add_file(args: argparse.Namespace) -> None:
    source = Path(args.file).expanduser().resolve()
    if not source.is_file():
        raise FileNotFoundError(f"সোর্স ফাইল পাওয়া যায়নি: {source}")

    path, data = load_event(args.slug)
    requirement = None

    if args.requirement:
        requirement = next(
            (
                item for item in data.get("requirements", [])
                if item.get("id") == args.requirement
            ),
            None,
        )
        if requirement is None:
            raise ValueError(f"Requirement ID পাওয়া যায়নি: {args.requirement}")

    target_dir = path.parent / "files"
    target_dir.mkdir(parents=True, exist_ok=True)
    target = target_dir / source.name
    if target.exists():
        raise FileExistsError(
            f"এই নামের ফাইল আগে থেকেই আছে: {target}. "
            "মূল ফাইলের নাম বদলে আবার যোগ করুন।"
        )

    shutil.copy2(source, target)
    relative_to_event = target.relative_to(path.parent).as_posix()
    file_id = f"FILE-{uuid.uuid4().hex[:10].upper()}"

    record = {
        "id": file_id,
        "original_name": source.name,
        "stored_path": relative_to_event,
        "extension": source.suffix.lower() or "(no extension)",
        "bytes": target.stat().st_size,
        "sha256": sha256_file(target),
        "requirement_id": args.requirement or "",
        "agenda_id": args.agenda or "",
        "description": args.description or "",
        "added_at": now_iso(),
    }

    data.setdefault("files", []).append(record)

    if requirement is not None:
        requirement.setdefault("evidence_file_ids", []).append(file_id)

    save_event(path, data)
    log_event(data["id"], "file_added", record)
    build_index()
    print(f"ফাইল যোগ হয়েছে: events/{args.slug}/{relative_to_event}")
    print(f"File ID: {file_id}")


def add_note(args: argparse.Namespace) -> None:
    path, data = load_event(args.slug)
    note = {
        "id": f"NOTE-{uuid.uuid4().hex[:8].upper()}",
        "text": args.text,
        "created_at": now_iso(),
        "actor": "local-user",
    }
    data.setdefault("notes", []).append(note)
    save_event(path, data)
    log_event(data["id"], "note_added", note)
    build_index()
    print(f"নোট যোগ হয়েছে: {note['id']}")


def event_summary(data: dict[str, Any], slug: str) -> dict[str, Any]:
    requirements = data.get("requirements", [])
    required = [
        item for item in requirements
        if item.get("required", True) and item.get("status") != "waived"
    ]
    verified = [item for item in required if item.get("status") == "verified"]
    percent = round(100 * len(verified) / len(required)) if required else 100

    files = []
    for item in data.get("files", []):
        stored = Path(item.get("stored_path", ""))
        if stored.is_absolute() or ".." in stored.parts:
            continue

        files.append(
            {
                **item,
                "url": f"{slug}/{stored.as_posix()}",
            }
        )

    return {
        **data,
        "slug": slug,
        "files": files,
        "readiness": {
            "percent": percent,
            "verified_required": len(verified),
            "required_total": len(required),
            "label": "আবশ্যক নথি verified হওয়ার অগ্রগতি",
        },
    }


def build_index() -> None:
    EVENTS_DIR.mkdir(parents=True, exist_ok=True)
    summaries = []

    for folder in sorted(EVENTS_DIR.iterdir()):
        event_path = folder / "event.json"
        if not folder.is_dir() or not event_path.is_file():
            continue

        try:
            data = json.loads(event_path.read_text(encoding="utf-8"))
            if not isinstance(data, dict) or not data.get("id"):
                print(f"এড়িয়ে যাওয়া হয়েছে (event ID নেই): {event_path}")
                continue
            summaries.append(event_summary(data, folder.name))
        except (OSError, json.JSONDecodeError, ValueError) as error:
            print(f"ইভেন্ট পড়া যায়নি {event_path}: {error}")

    summaries.sort(key=lambda item: (item.get("date") or "9999", item["title"].lower()))
    write_json(
        INDEX_FILE,
        {
            "schema": "mj-events-index/v1",
            "generated_at": now_iso(),
            "events": summaries,
        },
    )
    print(f"Events index updated: {len(summaries)} event(s).")


def show_audit(args: argparse.Namespace) -> None:
    if not AUDIT_FILE.exists():
        print("এখনও audit entry নেই।")
        return

    rows = []
    for line in AUDIT_FILE.read_text(encoding="utf-8").splitlines():
        try:
            item = json.loads(line)
            if not args.slug or item.get("event_id") == args.slug:
                rows.append(item)
        except json.JSONDecodeError:
            continue

    for item in rows[-args.limit:]:
        print(json.dumps(item, ensure_ascii=False))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="ইভেন্ট ডকুমেন্টেশন তৈরি ও পরিচালনা করুন।"
    )
    commands = parser.add_subparsers(dest="command", required=True)

    new = commands.add_parser("new", help="নতুন event তৈরি করুন")
    new.add_argument("--title", required=True)
    new.add_argument("--date", default="", help="YYYY-MM-DD")
    new.add_argument("--type", default="general")
    new.add_argument("--slug", help="ঐচ্ছিক, ইংরেজি অক্ষর/সংখ্যা/hyphen")
    new.set_defaults(func=new_event)

    agenda = commands.add_parser("agenda-add", help="Agenda item যোগ করুন")
    agenda.add_argument("slug")
    agenda.add_argument("--title", required=True)
    agenda.add_argument("--time", default="")
    agenda.add_argument("--duration", type=int, default=15)
    agenda.add_argument("--owner", default="")
    agenda.add_argument("--notes", default="")
    agenda.set_defaults(func=add_agenda)

    requirement = commands.add_parser(
        "requirement-add", help="Requirement যোগ করুন"
    )
    requirement.add_argument("slug")
    requirement.add_argument("--title", required=True)
    requirement.add_argument("--category", default="general")
    requirement.add_argument("--optional", action="store_true")
    requirement.set_defaults(func=add_requirement)

    status = commands.add_parser(
        "requirement-status", help="Requirement status বদলান"
    )
    status.add_argument("slug")
    status.add_argument("id")
    status.add_argument(
        "status",
        choices=("pending", "collected", "verified", "waived"),
    )
    status.add_argument("--note", default="")
    status.set_defaults(func=set_requirement)

    add = commands.add_parser("add-file", help="ইভেন্টে যেকোনো ফাইল যোগ করুন")
    add.add_argument("slug")
    add.add_argument("file", help="সোর্স ফাইলের path")
    add.add_argument("--requirement", default="")
    add.add_argument("--agenda", default="")
    add.add_argument("--description", default="")
    add.set_defaults(func=add_file)

    note = commands.add_parser("note", help="ইভেন্টের audit করা note যোগ করুন")
    note.add_argument("slug")
    note.add_argument("--text", required=True)
    note.set_defaults(func=add_note)

    build = commands.add_parser("build-index", help="Viewer data.json তৈরি করুন")
    build.set_defaults(func=lambda _args: build_index())

    audit = commands.add_parser("audit", help="Audit log দেখুন")
    audit.add_argument("--slug", default="", help="event ID দিয়ে filter")
    audit.add_argument("--limit", type=int, default=30)
    audit.set_defaults(func=show_audit)

    return parser


def main() -> None:
    args = build_parser().parse_args()
    try:
        args.func(args)
    except (OSError, ValueError, json.JSONDecodeError) as error:
        raise SystemExit(f"Error: {error}") from error


if __name__ == "__main__":
    main()

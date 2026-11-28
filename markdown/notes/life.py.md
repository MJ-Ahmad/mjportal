`life.py`-এর পূর্ণাঙ্গ সংস্করণ নিচে দিলাম। তবে root `index.html`-এর সম্পূর্ণ বর্তমান কোড আমি নির্ভরযোগ্যভাবে পড়তে পারিনি—রিপোর একই নামের `docs/index.html` ফেরত এসেছে। অনুমান করে পুরো homepage বদলে দিলে আপনার splash, heatmap, category filter, theme ও language-এর মতো বর্তমান feature হারাতে পারে। তাই `index.html`-এর **সম্পূর্ণ content এখানে paste করুন**; তখন Markdown rendering ও original-source copy যুক্ত করে পুরো ফাইলটি নিরাপদে লিখে দেব।

নিচের `life.py`-এ `.md` `--body-file`-এর content হুবহু রাখা হয় এবং entry-তে `description_format: "markdown"` যোগ হয়। পুরোনো entry-র format বদলাবে না। আগে `data.json`, `registry.json` ও `attachments/` backup নিন।

```python name=life.py
#!/usr/bin/env python3
"""Self / Life Tracker — command line and storage library.

Commands:
  python3 life.py log "one line of progress or a thought" [options]
  python3 life.py add "Heading" ["Description"] [--body-file notes.md] [options]
  python3 life.py list [--limit N]
  python3 life.py validate

Markdown body-file entries store the exact source in description and add
description_format="markdown". Rendering is handled by the browser UI; the
original description remains the source of truth for copy operations.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import mimetypes
import os
import re
import shutil
import sys
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

BASE = Path(__file__).resolve().parent
DATA_FILE = BASE / "data.json"
REGISTRY_FILE = BASE / "registry.json"
ATTACH_DIR = BASE / "attachments"

DHAKA = timezone(timedelta(hours=6))  # Asia/Dhaka is UTC+06:00, no DST.
TS_FMT = "%Y-%m-%d %H:%M:%S.%f"
TS_RE = re.compile(r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{3}$")
TRACK_RE = re.compile(r"^LIFE-\d{6}$")
REG_RE = re.compile(r"^REG-\d{6}$")
LINK_RE = re.compile(r"^[A-Z]+-\d{6}$")

CATEGORIES = [
    "health",
    "learning",
    "work",
    "habits",
    "relationships",
    "faith",
    "finance",
    "reflection",
    "other",
]
HEADING_MAX = 80


def fail(message: str, exit_code: int = 1) -> None:
    print(f"Error: {message}", file=sys.stderr)
    raise SystemExit(exit_code)


def now_stamps() -> tuple[str, str]:
    """Return Dhaka and UTC timestamps with millisecond precision."""
    utc_now = datetime.now(timezone.utc)
    dhaka = utc_now.astimezone(DHAKA).strftime(TS_FMT)[:-3]
    utc = utc_now.strftime(TS_FMT)[:-3]
    return dhaka, utc


def load(path: Path, default: Any) -> Any:
    """Load JSON, returning default only when the file does not exist."""
    if not path.exists():
        return default

    try:
        with path.open("r", encoding="utf-8") as handle:
            return json.load(handle)
    except (OSError, json.JSONDecodeError) as exc:
        fail(f"cannot read {path.name}: {exc}")


def save_atomic(path: Path, data: Any) -> None:
    """Write JSON atomically so an interrupted write does not corrupt it."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(
        dir=str(path.parent),
        prefix=f".{path.name}.",
        suffix=".tmp",
    )

    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            json.dump(data, handle, indent=4, ensure_ascii=False)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())

        os.replace(temporary, path)
    except BaseException:
        try:
            os.remove(temporary)
        except FileNotFoundError:
            pass
        raise


def ensure_structure() -> None:
    """Create the attachment directory and initial data files if absent."""
    ATTACH_DIR.mkdir(parents=True, exist_ok=True)

    if not DATA_FILE.exists():
        save_atomic(DATA_FILE, {"entries": []})

    if not REGISTRY_FILE.exists():
        save_atomic(
            REGISTRY_FILE,
            {"last_registry": 0, "last_tracking": 0},
        )


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def allocate_ids() -> tuple[str, str]:
    """Advance both counters and return (LIFE-id, REG-id)."""
    registry = load(
        REGISTRY_FILE,
        {"last_registry": 0, "last_tracking": 0},
    )
    if not isinstance(registry, dict):
        fail("registry.json must contain a JSON object")

    try:
        last_registry = int(registry.get("last_registry", 0))
        last_tracking = int(registry.get("last_tracking", 0))
    except (TypeError, ValueError):
        fail("registry counters must be integers")

    if last_registry < 0 or last_tracking < 0:
        fail("registry counters cannot be negative")

    registry["last_registry"] = last_registry + 1
    registry["last_tracking"] = last_tracking + 1
    save_atomic(REGISTRY_FILE, registry)

    return (
        f"LIFE-{registry['last_tracking']:06d}",
        f"REG-{registry['last_registry']:06d}",
    )


def store_attachment(reg_id: str, source: Path) -> dict[str, Any]:
    """Copy an attachment into attachments/ and return its metadata."""
    if not source.is_file():
        fail(f"attachment file not found: {source}")

    ATTACH_DIR.mkdir(parents=True, exist_ok=True)
    original = source.name
    extension = source.suffix.lower()
    stem = f"{reg_id}"
    filename = f"{stem}{extension}"
    destination = ATTACH_DIR / filename

    # Avoid overwriting if an unusual existing record already uses that name.
    counter = 2
    while destination.exists():
        filename = f"{stem}-{counter}{extension}"
        destination = ATTACH_DIR / filename
        counter += 1

    try:
        shutil.copy2(source, destination)
    except OSError as exc:
        fail(f"could not copy attachment {source}: {exc}")

    return {
        "file": f"attachments/{filename}",
        "original": original,
        "size": destination.stat().st_size,
        "type": mimetypes.guess_type(str(destination))[0]
        or "application/octet-stream",
        "sha256": sha256(destination),
    }


def split_list(text: str | None) -> list[str]:
    """Convert comma-separated items to lowercase, de-duplicated values."""
    result: list[str] = []
    for item in (text or "").split(","):
        value = item.strip().lower()
        if value and value not in result:
            result.append(value)
    return result


def derive_heading(text: str) -> str:
    heading = " ".join(text.split()[:8])
    if len(heading) > HEADING_MAX:
        heading = heading[:HEADING_MAX].rsplit(" ", 1)[0] + "…"
    return heading


def create_entry(
    heading: str,
    description: str,
    args: argparse.Namespace,
    *,
    description_format: str = "plain",
    description_source: str | None = None,
) -> dict[str, Any]:
    """Validate input, allocate IDs, and append one entry to data.json."""
    heading = " ".join(heading.split())

    # Preserve Markdown source exactly. Plain text keeps the old trimming behavior.
    if description_format == "markdown":
        stored_description = description
        has_description = bool(description.strip())
    else:
        stored_description = description.strip()
        has_description = bool(stored_description)

    if not heading:
        fail("heading must not be empty")
    if len(heading) > HEADING_MAX:
        fail(f"heading must be {HEADING_MAX} characters or fewer")
    if not has_description:
        fail("description must not be empty (or use --body-file)")
    if args.category not in CATEGORIES:
        fail(f"unknown category {args.category!r}")
    if args.mood is not None and not 1 <= args.mood <= 5:
        fail("mood must be between 1 and 5")

    links = [item.upper() for item in split_list(args.link)]
    for link in links:
        if not LINK_RE.fullmatch(link):
            fail(f"bad link reference {link!r} (expected e.g. TASK-000001)")

    attachment_source: Path | None = None
    if args.add_file:
        attachment_source = Path(args.add_file).expanduser().resolve()
        if not attachment_source.is_file():
            fail(f"attachment file not found: {attachment_source}")

    # Confirm the existing database is readable before allocating an ID.
    data = load(DATA_FILE, {"entries": []})
    if not isinstance(data, dict) or not isinstance(data.get("entries"), list):
        fail("data.json must contain an object with an 'entries' list")

    tracking_id, reg_id = allocate_ids()
    dhaka, utc = now_stamps()

    entry: dict[str, Any] = {
        "tracking_id": tracking_id,
        "registry": reg_id,
        "dhaka_time": dhaka,
        "utc_time": utc,
        "category": args.category,
        "mood": args.mood,
        "heading": heading,
        "description": stored_description,
        "tags": split_list(args.tag),
        "links": links,
    }

    if description_format == "markdown":
        entry["description_format"] = "markdown"
        if description_source:
            entry["description_source"] = description_source

    if attachment_source is not None:
        entry["attachment"] = store_attachment(reg_id, attachment_source)

    data["entries"].insert(0, entry)
    save_atomic(DATA_FILE, data)
    return entry


def cmd_log(args: argparse.Namespace) -> None:
    entry = create_entry(
        derive_heading(args.text),
        args.text,
        args,
    )
    report(entry)


def cmd_add(args: argparse.Namespace) -> None:
    description = args.description or ""
    description_format = "plain"
    description_source: str | None = None

    if args.body_file:
        source = Path(args.body_file).expanduser().resolve()
        if not source.is_file():
            fail(f"body file not found: {source}")

        try:
            # newline="" prevents universal-newline conversion so Markdown source
            # remains unchanged when read and copied later.
            with source.open("r", encoding="utf-8", newline="") as handle:
                description = handle.read()
        except (OSError, UnicodeDecodeError) as exc:
            fail(f"could not read body file {source}: {exc}")

        if source.suffix.lower() == ".md":
            description_format = "markdown"
            description_source = source.name

    entry = create_entry(
        args.heading,
        description,
        args,
        description_format=description_format,
        description_source=description_source,
    )
    report(entry)


def cmd_list(args: argparse.Namespace) -> None:
    data = load(DATA_FILE, {"entries": []})
    if not isinstance(data, dict) or not isinstance(data.get("entries"), list):
        fail("data.json must contain an object with an 'entries' list")

    for entry in data["entries"][: args.limit]:
        print(
            f"{entry.get('tracking_id', '—')}  "
            f"{entry.get('registry', '—')}  "
            f"{entry.get('dhaka_time', '—')}  "
            f"{entry.get('heading', '')}"
        )


def report(entry: dict[str, Any]) -> None:
    print("\nEntry added")
    print(f"  Tracking : {entry['tracking_id']}")
    print(f"  Registry : {entry['registry']}")
    print(f"  Dhaka    : {entry['dhaka_time']}")
    print(f"  UTC      : {entry['utc_time']}")

    if entry.get("description_format") == "markdown":
        print(f"  Body     : Markdown ({entry.get('description_source', 'body file')})")

    if "attachment" in entry:
        print(f"  File     : {entry['attachment']['original']}")

    print()


def validate() -> tuple[list[str], list[str]]:
    """Return (errors, warnings). Empty errors means the database is sound."""
    errors: list[str] = []
    warnings: list[str] = []

    data = load(DATA_FILE, None)
    registry = load(REGISTRY_FILE, None)

    if data is None or registry is None:
        return ["data.json or registry.json is missing"], warnings

    if not isinstance(data, dict):
        return ["data.json must contain a JSON object"], warnings
    if not isinstance(registry, dict):
        return ["registry.json must contain a JSON object"], warnings

    entries = data.get("entries")
    if not isinstance(entries, list):
        return ["'entries' must be a list"], warnings

    seen_tracking: set[str] = set()
    seen_registry: set[str] = set()
    max_tracking = 0
    max_registry = 0

    for entry in entries:
        if not isinstance(entry, dict):
            errors.append("entry record must be a JSON object")
            continue

        tracking_id = str(entry.get("tracking_id", "<missing>"))
        registry_id = str(entry.get("registry", "<missing>"))

        if not TRACK_RE.fullmatch(tracking_id):
            errors.append(f"{tracking_id}: bad tracking_id")
        elif tracking_id in seen_tracking:
            errors.append(f"{tracking_id}: duplicate tracking_id")
        else:
            seen_tracking.add(tracking_id)
            max_tracking = max(max_tracking, int(tracking_id[5:]))

        if not REG_RE.fullmatch(registry_id):
            errors.append(f"{tracking_id}: bad registry id ({registry_id})")
        elif registry_id in seen_registry:
            errors.append(f"{tracking_id}: duplicate registry id")
        else:
            seen_registry.add(registry_id)
            max_registry = max(max_registry, int(registry_id[4:]))

        for key in ("dhaka_time", "utc_time"):
            value = str(entry.get(key, ""))
            if not TS_RE.fullmatch(value):
                errors.append(f"{tracking_id}: invalid {key}")
            else:
                try:
                    datetime.strptime(value, TS_FMT[:-3])
                except ValueError:
                    errors.append(f"{tracking_id}: impossible {key} value")

        if not str(entry.get("heading", "")).strip():
            errors.append(f"{tracking_id}: empty heading")
        elif len(str(entry.get("heading", ""))) > HEADING_MAX:
            errors.append(f"{tracking_id}: heading exceeds {HEADING_MAX} characters")

        description = entry.get("description", "")
        if not isinstance(description, str) or not description.strip():
            errors.append(f"{tracking_id}: empty or invalid description")

        description_format = entry.get("description_format", "plain")
        if description_format not in ("plain", "markdown"):
            errors.append(
                f"{tracking_id}: unsupported description_format "
                f"{description_format!r}"
            )

        if entry.get("category", "other") not in CATEGORIES:
            errors.append(f"{tracking_id}: unknown category")

        mood = entry.get("mood")
        if mood is not None and (
            not isinstance(mood, int) or isinstance(mood, bool) or not 1 <= mood <= 5
        ):
            errors.append(f"{tracking_id}: mood must be 1-5")

        for link in entry.get("links", []):
            if not LINK_RE.fullmatch(str(link)):
                errors.append(f"{tracking_id}: bad link {link!r}")

        attachment = entry.get("attachment")
        if attachment:
            if not isinstance(attachment, dict):
                errors.append(f"{tracking_id}: attachment must be a JSON object")
                continue

            relative = str(attachment.get("file", ""))
            normalized = os.path.normpath(relative)
            expected_prefix = "attachments" + os.sep

            if (
                os.path.isabs(relative)
                or normalized in ("..", ".")
                or normalized.startswith(".." + os.sep)
                or not normalized.startswith(expected_prefix)
            ):
                errors.append(f"{tracking_id}: unsafe attachment path ({relative})")
                continue

            full_path = (BASE / normalized).resolve()
            attachments_root = ATTACH_DIR.resolve()

            try:
                if os.path.commonpath([str(full_path), str(attachments_root)]) != str(attachments_root):
                    errors.append(f"{tracking_id}: unsafe attachment path ({relative})")
                    continue
            except ValueError:
                errors.append(f"{tracking_id}: unsafe attachment path ({relative})")
                continue

            if attachment.get("missing"):
                warnings.append(
                    f"{tracking_id}: file not in this copy "
                    f"({attachment.get('original', relative)})"
                )
            elif not full_path.is_file():
                errors.append(f"{tracking_id}: attachment missing ({relative})")
            elif attachment.get("sha256") and sha256(full_path) != attachment["sha256"]:
                errors.append(f"{tracking_id}: checksum mismatch ({relative})")

    try:
        last_tracking = int(registry.get("last_tracking", 0))
        last_registry = int(registry.get("last_registry", 0))
    except (TypeError, ValueError):
        return errors + ["registry counters must be integers"], warnings

    if last_tracking < max_tracking:
        errors.append("registry.last_tracking is behind the highest LIFE ID")
    if last_registry < max_registry:
        errors.append("registry.last_registry is behind the highest REG ID")

    return errors, warnings


def cmd_validate(_args: argparse.Namespace) -> None:
    errors, warnings = validate()

    for warning in warnings:
        print(f"  warning: {warning}")

    if errors:
        for error in errors:
            print(f"  ERROR: {error}")
        print(f"\nValidation failed with {len(errors)} error(s).")
        raise SystemExit(1)

    data = load(DATA_FILE, {"entries": []})
    print(f"Database valid · entries: {len(data['entries'])}")


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="life.py",
        description="Self / Life Tracker",
    )
    subcommands = parser.add_subparsers(dest="cmd", required=True)

    def add_shared_options(command: argparse.ArgumentParser) -> None:
        command.add_argument(
            "--category",
            default="other",
            choices=CATEGORIES,
        )
        command.add_argument("--mood", type=int)
        command.add_argument("--tag", default="", help="comma-separated tags")
        command.add_argument(
            "--link",
            default="",
            help="comma-separated IDs, e.g. TASK-000001",
        )
        command.add_argument(
            "--add-file",
            metavar="PATH",
            help="attach a file (copied and checksummed)",
        )

    log_command = subcommands.add_parser("log", help="quick one-line entry")
    log_command.add_argument("text")
    add_shared_options(log_command)
    log_command.set_defaults(func=cmd_log)

    add_command = subcommands.add_parser("add", help="full entry with heading and description")
    add_command.add_argument("heading")
    add_command.add_argument("description", nargs="?", default="")
    add_command.add_argument(
        "--body-file",
        help="read description from a file; .md files render as Markdown",
    )
    add_shared_options(add_command)
    add_command.set_defaults(func=cmd_add)

    list_command = subcommands.add_parser("list", help="show latest entries")
    list_command.add_argument("--limit", type=int, default=10)
    list_command.set_defaults(func=cmd_list)

    validate_command = subcommands.add_parser("validate", help="check data integrity")
    validate_command.set_defaults(func=cmd_validate)

    args = parser.parse_args()
    ensure_structure()
    args.func(args)


if __name__ == "__main__":
    main()
```

## `index.html` সম্পর্কে

`life.py`-এর পূর্ণ কোড দেওয়া সম্ভব হয়েছে, কিন্তু root-এর **বর্তমান সম্পূর্ণ `index.html` আমি tool দিয়ে উদ্ধার করতে পারিনি**—`index.html` চাওয়ায় ভুল করে `docs/index.html` ফেরত এসেছে। আপনার homepage-এ splash, timeline, category filter, theme ও language-এর মতো feature আছে; তাই অজানা source ধরে পূর্ণ ফাইল লিখে দিলে সেগুলো হারানোর ঝুঁকি থাকবে।

`index.html`-এর পুরো content এখানে paste করুন। তখন আমি সেটির পূর্ণ বিকল্পে Markdown rendering, sanitization, responsive styles এবং **original Markdown copy** যোগ করে দেব। আপাতত না দেখে পুরো root `index.html` replace করবেন না।



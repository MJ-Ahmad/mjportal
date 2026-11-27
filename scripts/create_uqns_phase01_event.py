#!/usr/bin/env python3
"""Create UQNS Phase-01's first 48-hour documentation event.

Creates:
  events/uqns-phase-01-foundation/event.json
  events/uqns-phase-01-foundation/files/*.md
  events/audit.jsonl
  events/data.json

Uses only the Python standard library. Existing event files are never overwritten.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
EVENTS_DIR = ROOT / "events"
SLUG = "uqns-phase-01-foundation"
EVENT_DIR = EVENTS_DIR / SLUG
FILES_DIR = EVENT_DIR / "files"
EVENT_JSON = EVENT_DIR / "event.json"
INDEX_JSON = EVENTS_DIR / "data.json"
AUDIT_JSONL = EVENTS_DIR / "audit.jsonl"
DHAKA = ZoneInfo("Asia/Dhaka")

EVENT_TITLE = "UQNS Phase 01 — Foundation ও প্রাথমিক কাঠামো চূড়ান্তকরণ"


def timestamp(value: datetime | None = None) -> str:
    value = value or datetime.now(DHAKA)
    return value.astimezone(DHAKA).isoformat(timespec="seconds")


def write_json(path: Path, data: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    temporary.replace(path)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def add_artifact(
    files: list[dict],
    *,
    filename: str,
    content: str | None = None,
    source: Path | None = None,
    requirement_id: str = "",
    description: str = "",
) -> None:
    destination = FILES_DIR / filename

    if destination.exists():
        raise FileExistsError(f"Artifact আগে থেকেই আছে: {destination}")

    if source is not None:
        shutil.copy2(source, destination)
    else:
        destination.write_text(content or "", encoding="utf-8")

    stat = destination.stat()
    files.append(
        {
            "id": f"FILE-{uuid.uuid4().hex[:10].upper()}",
            "original_name": destination.name,
            "stored_path": f"files/{destination.name}",
            "extension": destination.suffix.lower() or "(no extension)",
            "bytes": stat.st_size,
            "sha256": sha256_file(destination),
            "requirement_id": requirement_id,
            "agenda_id": "",
            "description": description,
            "added_at": timestamp(),
        }
    )


def append_audit(event_id: str, action: str, details: dict) -> None:
    EVENTS_DIR.mkdir(parents=True, exist_ok=True)
    row = {
        "audit_id": f"AUD-{uuid.uuid4().hex[:12].upper()}",
        "event_id": event_id,
        "timestamp": timestamp(),
        "actor": "local-user",
        "action": action,
        "details": details,
    }
    with AUDIT_JSONL.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def readiness(event: dict) -> dict:
    requirements = event.get("requirements", [])
    required = [
        item for item in requirements
        if item.get("required", True) and item.get("status") != "waived"
    ]
    verified = [item for item in required if item.get("status") == "verified"]
    percent = round(100 * len(verified) / len(required)) if required else 100
    return {
        "percent": percent,
        "verified_required": len(verified),
        "required_total": len(required),
        "label": "আবশ্যক requirement verified হওয়ার অগ্রগতি",
    }


def event_for_index(event: dict) -> dict:
    result = dict(event)
    result["readiness"] = readiness(event)
    result["files"] = [
        {
            **item,
            "url": f"{event['slug']}/{item['stored_path']}",
        }
        for item in event.get("files", [])
    ]
    return result


def build_index() -> int:
    events: list[dict] = []

    if EVENTS_DIR.is_dir():
        for folder in sorted(EVENTS_DIR.iterdir()):
            path = folder / "event.json"
            if not folder.is_dir() or not path.is_file():
                continue
            try:
                event = json.loads(path.read_text(encoding="utf-8"))
                if isinstance(event, dict) and event.get("id"):
                    events.append(event_for_index(event))
            except (OSError, json.JSONDecodeError) as error:
                print(f"সতর্কতা: {path} পড়া যায়নি: {error}", file=sys.stderr)

    events.sort(key=lambda item: (item.get("date") or "9999", item.get("title", "").lower()))

    write_json(
        INDEX_JSON,
        {
            "schema": "mj-events-index/v1",
            "generated_at": timestamp(),
            "events": events,
        },
    )
    return len(events)


def make_agenda(start: datetime, deadline: datetime) -> list[dict]:
    blocks = [
        (
            "AG-001",
            "README ও scope গ্রহণযোগ্যতা যাচাই",
            0,
            60,
            "UQNS উদ্দেশ্য, দুইটি প্রাথমিক অংশ ও README-র Phase-01 scope আলাদা করে চিহ্নিত করা।",
        ),
        (
            "AG-002",
            "Qur'an Navigation Platform-এর boundary নির্ধারণ",
            3,
            90,
            "Navigation Platform-এর প্রাথমিক scope, input, output ও পরবর্তী ধাপ লিখে রাখা।",
        ),
        (
            "AG-003",
            "Quran Memorize Ecosystem-এর boundary নির্ধারণ",
            7,
            90,
            "Student, Teacher, Supervisor ও Principal অংশের প্রাথমিক boundary ও dependency লিখে রাখা।",
        ),
        (
            "AG-004",
            "Foundation folder tree draft",
            14,
            120,
            "README-তে থাকা foundation ও layer-গুলো মিলিয়ে draft tree এবং naming convention তৈরি করা।",
        ),
        (
            "AG-005",
            "ফাইল, data, localization ও content-এর dependency review",
            22,
            90,
            "JSON schema, content source, language expansion, assets এবং documentation-এর dependency তালিকাভুক্ত করা।",
        ),
        (
            "AG-006",
            "Tree ও দুই অংশের scope review",
            32,
            90,
            "অসম্পূর্ণ, duplicate বা scope-এর বাইরে থাকা directory চিহ্নিত করে সংশোধন করা।",
        ),
        (
            "AG-007",
            "চূড়ান্ত structure ও সিদ্ধান্ত নথিভুক্ত",
            42,
            90,
            "Approved tree, সিদ্ধান্ত, unresolved item এবং পরবর্তী কাজ README/decision note-এ সংরক্ষণ করা।",
        ),
        (
            "AG-008",
            "48-hour handover ও evidence check",
            47,
            45,
            "Deliverable, checklist evidence ও audit trail পরীক্ষা করে event status হালনাগাদ করা।",
        ),
    ]

    agenda = []
    for item_id, title, offset, duration, notes in blocks:
        scheduled = start + timedelta(hours=offset)
        if scheduled > deadline:
            scheduled = deadline
        agenda.append(
            {
                "id": item_id,
                "title": title,
                "start_time": timestamp(scheduled),
                "duration_minutes": duration,
                "owner": "MJ Ahmad",
                "status": "planned",
                "notes": notes,
            }
        )
    return agenda


def make_requirements() -> list[dict]:
    rows = [
        ("REQ-001", "পূর্ণ UQNS README ও বর্তমান vision", "source", "collected"),
        ("REQ-002", "Qur'an Navigation Platform-এর feature ও boundary", "scope", "collected"),
        ("REQ-003", "Quran Memorize Ecosystem-এর component ও boundary", "scope", "collected"),
        ("REQ-004", "Phase-01 root folder tree-এর অনুমোদিত তালিকা", "architecture", "pending"),
        ("REQ-005", "দুই প্রাথমিক অংশের directory mapping", "architecture", "pending"),
        ("REQ-006", "Folder ও filename naming convention", "standards", "pending"),
        ("REQ-007", "Content/data format, source ও provenance-এর সিদ্ধান্ত", "data-governance", "pending"),
        ("REQ-008", "Arabic, English ও Bangla localization-এর প্রাথমিক কাঠামো", "localization", "pending"),
        ("REQ-009", "Brand assets ও license/source-এর যাচাই তালিকা", "assets", "pending"),
        ("REQ-010", "Structure tree review ও final approval record", "approval", "pending"),
        ("REQ-011", "README/decision note-এ final tree ও unresolved item", "documentation", "pending"),
        ("REQ-012", "Backup/version-control-এ final deliverable সংরক্ষণের প্রমাণ", "handover", "pending"),
    ]

    return [
        {
            "id": item_id,
            "title": title,
            "category": category,
            "required": True,
            "status": status,
            "notes": "",
            "evidence_file_ids": [],
        }
        for item_id, title, category, status in rows
    ]


def main() -> None:
    parser = argparse.ArgumentParser(
        description="UQNS-এর প্রথম 48-hour foundation event তৈরি করুন।"
    )
    parser.add_argument(
        "--readme",
        help="লোকাল UQNS README path; দিলে ইভেন্টের files/ ফোল্ডারে কপি হবে",
    )
    args = parser.parse_args()

    if EVENT_JSON.exists():
        raise SystemExit(
            f"ইভেন্ট আগে থেকেই আছে: {EVENT_JSON}\n"
            "কোনো ফাইল overwrite করা হয়নি। বিদ্যমান ইভেন্টটি ব্যবহার করুন।"
        )

    source_readme: Path | None = None
    if args.readme:
        source_readme = Path(args.readme).expanduser().resolve()
        if not source_readme.is_file():
            raise SystemExit(f"README ফাইল পাওয়া যায়নি: {source_readme}")

    created = datetime.now(DHAKA)
    deadline = created + timedelta(hours=48)
    event_id = f"EVT-{created:%Y%m%d}-UQNS-P1"

    FILES_DIR.mkdir(parents=True, exist_ok=False)
    files: list[dict] = []

    add_artifact(
        files,
        filename="01-event-brief.md",
        requirement_id="REQ-004",
        description="প্রথম ইভেন্টের উদ্দেশ্য, সময়সীমা, scope ও acceptance criteria",
        content=f"""# UQNS Phase-01 Event Brief

- Event ID: `{event_id}`
- শুরু: `{timestamp(created)}`
- নির্ধারিত সময়সীমা: `{timestamp(deadline)}`
- সময় অঞ্চল: `Asia/Dhaka`

## উদ্দেশ্য

এই ইভেন্টে UQNS README-এর ভিত্তিতে Foundation Layer-এর প্রাথমিক folder tree
এবং নিচের দুইটি অংশের boundary ও directory mapping চূড়ান্ত করার পরিকল্পনা হবে:

1. Qur'an Navigation Platform
2. Quran Memorize Ecosystem

## এই 48 ঘণ্টার deliverable

- README-তে নির্ধারিত scope-এর সাথে সামঞ্জস্যপূর্ণ root folder tree
- দুইটি অংশের কোন folder কোন layer-এর অধীনে থাকবে তার mapping
- naming convention ও প্রাথমিক ownership/responsibility note
- final tree README বা architecture decision note-এ নথিভুক্ত
- unresolved decision ও পরবর্তী phase-এর task তালিকা
- final structure version control/backup-এ সংরক্ষণের record

## Scope boundary

এই ইভেন্ট folder structure ও documentation planning-এর জন্য।
এই ইভেন্টে Quran text, translation, tafsir, audio বা অন্য copyrighted content
সংগ্রহ/প্রকাশ করা হবে না। সেসবের source, license, attribution ও accuracy
review আলাদা requirement হিসেবে পরিকল্পনা করতে হবে।

## Acceptance criteria

- README-এর 16টি layer ও Foundation-এর root তালিকার পার্থক্যগুলো review করা
- প্রয়োজনীয় directory-র একটিও বাদ না পড়া এবং duplicate directory না থাকা
- Qur'an Navigation Platform ও Memorize Ecosystem-এর scope আলাদা করে নথিভুক্ত
- `data/`, `content/`, `localization/`, `navigation/`, `reader/`, `search/`,
  `audio/`, `study/`, `profiles/`, `analytics/`, `api/`, `apps/`,
  `documentation/`, `governance/`-এর placement review করা
- Final tree ও সিদ্ধান্ত README-তে সংরক্ষিত এবং review করা
- Checklist status কেবল evidence দেখার পর `verified` করা

## Completion সতর্কতা

Checklist-এর 100% মানে সব আবশ্যক item-এ evidence দেখে `verified` status দেওয়া।
এটি কোনো বাহ্যিক নির্ভুলতা, Qur'anic content accuracy, legal review বা
সম্পূর্ণ project delivery-র নিশ্চয়তা নয়।
""",
    )

    add_artifact(
        files,
        filename="02-quran-navigation-platform-scope.md",
        requirement_id="REQ-002",
        description="Qur'an Navigation Platform-এর প্রাথমিক feature ও scope note",
        content="""# Qur'an Navigation Platform — Initial Scope

## README-তে উল্লেখিত capabilities

- Vector Mushaf
- Ayah, Surah, Juz, Hizb ও Ruku navigation
- Semantic search ও root-word search
- Cross references
- Audio synchronization
- Multilingual translation
- Research workspace

## এই ইভেন্টে নির্ধারণ করতে হবে

- কোন capabilities প্রথম foundation tree-তে শুধু directory placeholder হবে
- navigation, search, reader, content ও data layer-এর ownership boundary
- প্রতিটি feature-এর সম্ভাব্য input/output এবং interdependency
- Arabic text, translation, audio ও reference data-এর provenance/license যাচাই কীভাবে হবে
- কোন capability Phase-01-এর বাইরে থাকবে

## প্রাথমিক mapping — অনুমোদনের অপেক্ষায়

- `content/` — language/source অনুযায়ী content organization
- `data/quran/` — structural metadata ও machine-readable records
- `navigation/` — page/surah/juz/hizb/ruku/ayah navigation
- `search/` — text, root-word ও semantic search
- `reader/` — Mushaf, ayah, translation ও comparison views
- `audio/` — reciter, stream ও synchronization metadata
- `study/` — notes, bookmarks, highlights ও research workspace
- `api/` — Quran/navigation/search/translation/audio interfaces
- `apps/` — web, PWA, Android, iOS, desktop ও kiosk app boundaries

এই mapping একটি draft; event review ও approval-এর আগে এটিকে final ধরা যাবে না।
""",
    )

    add_artifact(
        files,
        filename="03-quran-memorize-ecosystem-scope.md",
        requirement_id="REQ-003",
        description="Quran Memorize Ecosystem-এর component ও প্রাথমিক mapping",
        content="""# Quran Memorize Ecosystem — Initial Scope

## README-তে উল্লেখিত components

- Student Portal
- Teacher Portal
- Supervisor Dashboard
- Principal Dashboard
- Analytics Engine
- Reporting System
- Attendance System
- Academic Tracking
- Governance Framework

## এই ইভেন্টে নির্ধারণ করতে হবে

- এই ecosystem UQNS repository-র কোন অংশে থাকবে
- এটি `apps/`, `profiles/`, `analytics/`, `api/` ও `governance/`-এর সাথে কীভাবে যুক্ত হবে
- student, teacher, supervisor ও principal role-এর প্রাথমিক responsibility
- ব্যক্তিগত শিক্ষার্থী তথ্য কীভাবে গোপন ও access-controlled থাকবে
- attendance, analytics ও reporting-এর জন্য কোন data governance দরকার
- Quran content/navigation platform-এর সাথে integration boundary কী হবে

## প্রাথমিক mapping — অনুমোদনের অপেক্ষায়

- `apps/` — সংশ্লিষ্ট portal ও dashboard app boundary
- `profiles/` — students, teachers, admins ও guests-এর profile model
- `analytics/` — progress, habits, completion ও reporting-related modules
- `api/` — অনুমোদিত data exchange boundary
- `governance/` — privacy, access, ethics, retention ও stewardship policy
- `documentation/` — onboarding, architecture ও operating procedures

Student data ও access policy review না করে বাস্তব ব্যক্তিগত তথ্য repository-তে
রাখা যাবে না। Mapping final approval-এর আগে draft হিসেবেই বিবেচ্য।
""",
    )

    add_artifact(
        files,
        filename="04-folder-tree-acceptance-checklist.md",
        requirement_id="REQ-004",
        description="Final folder tree review-এর checklist",
        content="""# Folder Tree Acceptance Checklist

প্রতিটি item review ও evidence পাওয়ার আগে completed/verified হিসেবে চিহ্নিত করবেন না।

- [ ] README-এর Foundation root directory list মিলিয়ে দেখা
- [ ] README-এর Layer 01 directory list মিলিয়ে দেখা
- [ ] দুই তালিকার অমিলের জন্য সিদ্ধান্ত/ব্যাখ্যা লেখা
- [ ] Qur'an Navigation Platform-এর directory mapping approve করা
- [ ] Quran Memorize Ecosystem-এর directory mapping approve করা
- [ ] `content/` ও `data/`-এর পার্থক্য ও data ownership লেখা
- [ ] `navigation/`, `reader/` ও `search/`-এর boundary লেখা
- [ ] `audio/` ও media metadata-এর boundary লেখা
- [ ] `study/` ও user-specific data-এর boundary লেখা
- [ ] `profiles/`, `analytics/` ও privacy consideration review করা
- [ ] `api/` ও `apps/` placement review করা
- [ ] `documentation/` ও `governance/` ownership review করা
- [ ] Naming convention এবং lowercase/kebab-case policy লেখা
- [ ] Copyright/license/provenance review ছাড়া content যোগ না করার সিদ্ধান্ত লেখা
- [ ] Final tree README বা architecture decision note-এ commit করা
- [ ] Final commit/backup evidence সংরক্ষণ করা
- [ ] Deferred item ও Phase-02 task তালিকাভুক্ত করা

## Final tree draft — approval pending

```text
quran-navigation/
├── assets/
├── content/
├── data/
├── localization/
├── navigation/
├── search/
├── reader/
├── audio/
├── study/
├── analytics/
├── api/
├── apps/
├── profiles/
├── documentation/
└── governance/

README-র tree-তে কোনো directory অতিরিক্ত, অনুপস্থিত বা আলাদা অবস্থানে থাকলে review decision নথিভুক্ত করে final version তৈরি করুন। """, )


if source_readme is not None:
    add_artifact(
        files,
        filename="00-UQNS-README.md",
        source=source_readme,
        requirement_id="REQ-001",
        description="ব্যবহারকারীর দেওয়া UQNS README-এর event evidence copy",
    )

agenda = make_agenda(created, deadline)

event = {
    "schema": "mj-event/v1",
    "id": event_id,
    "slug": SLUG,
    "title": EVENT_TITLE,
    "event_type": "project-milestone",
    "status": "planning",
    "date": created.date().isoformat(),
    "start_time": timestamp(created),
    "end_time": timestamp(deadline),
    "deadline_at": timestamp(deadline),
    "timezone": "Asia/Dhaka",
    "venue": "UQNS repository / local workspace",
    "owner": "MJ Ahmad",
    "purpose": (
        "প্রদত্ত UQNS README অনুযায়ী Qur'an Navigation Platform ও "
        "Quran Memorize Ecosystem-এর প্রাথমিক scope এবং Foundation folder "
        "tree 48 ঘণ্টার মধ্যে review, document ও finalize করা।"
    ),
    "description": (
        "এই ইভেন্টটি planning/documentation milestone। Project implementation "
        "বা Qur'anic content validation সম্পন্ন হয়েছে—এমন দাবি করে না।"
    ),
    "scope": {
        "in_scope": [
            "README requirements review",
            "দুইটি প্রাথমিক অংশের scope boundary",
            "Foundation directory tree draft ও review",
            "Naming convention ও architecture decision documentation",
            "Final tree review evidence ও handover",
        ],
        "out_of_scope": [
            "পূর্ণ Quran content/translation/tafsir/audio সংগ্রহ",
            "Production application implementation",
            "শিক্ষার্থী/ক্লায়েন্টের ব্যক্তিগত তথ্য repository-তে যোগ",
            "বাহ্যিক license বা religious content accuracy-এর স্বয়ংক্রিয় নিশ্চয়তা",
        ],
    },
    "agenda": agenda,
    "requirements": make_requirements(),
    "files": files,
    "notes": [
        {
            "id": "NOTE-UQNS-001",
            "text": (
                "প্রস্তুতির percentage আবশ্যক checklist item-এর verified status "
                "থেকে হিসাব হবে; এটি 100% বাস্তব নিশ্চয়তার দাবি নয়।"
            ),
            "created_at": timestamp(created),
            "actor": "local-user",
        }
    ],
    "created_at": timestamp(created),
    "updated_at": timestamp(created),
}

write_json(EVENT_JSON, event)

append_audit(
    event_id,
    "event_created",
    {
        "slug": SLUG,
        "title": EVENT_TITLE,
        "deadline_at": event["deadline_at"],
        "artifact_count": len(files),
        "readme_attached": source_readme is not None,
    },
)

append_audit(
    event_id,
    "initial_agenda_and_requirements_created",
    {
        "agenda_count": len(agenda),
        "requirement_count": len(event["requirements"]),
        "initially_collected": [
            item["id"]
            for item in event["requirements"]
            if item["status"] == "collected"
        ],
    },
)

count = build_index()

print("UQNS-এর প্রথম event তৈরি হয়েছে।")
print(f"Event ID : {event_id}")
print(f"Folder   : {EVENT_DIR.relative_to(ROOT)}")
print(f"Deadline : {event['deadline_at']} (Asia/Dhaka)")
print(f"Artifacts: {len(files)}")
print(f"Index    : {INDEX_JSON.relative_to(ROOT)}")
print(f"Events in viewer index: {count}")
print()
print("পরবর্তী ধাপ:")
print("  ./run.sh serve")
print("  তারপর খুলুন: http://127.0.0.1:8000/events/")

if name == "main": main()

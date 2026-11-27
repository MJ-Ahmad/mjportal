#!/usr/bin/env python3
"""
Create MJ-AI's first 48-hour architecture and foundation event.

This script is documentation/planning oriented.
It does not create or modify the MJ-AI source tree.
It does not install dependencies or download AI models.
"""

from __future__ import annotations

import hashlib
import json
import sys
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
EVENTS_DIR = ROOT / "events"
SLUG = "mj-ai-foundation-48h"
EVENT_DIR = EVENTS_DIR / SLUG
FILES_DIR = EVENT_DIR / "files"
EVENT_JSON = EVENT_DIR / "event.json"
INDEX_JSON = EVENTS_DIR / "data.json"
AUDIT_JSONL = EVENTS_DIR / "audit.jsonl"
DHAKA = ZoneInfo("Asia/Dhaka")


def now_iso(value: datetime | None = None) -> str:
    value = value or datetime.now(DHAKA)
    return value.astimezone(DHAKA).isoformat(timespec="seconds")


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    temporary.replace(path)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def append_audit(event_id: str, action: str, details: dict[str, Any]) -> None:
    EVENTS_DIR.mkdir(parents=True, exist_ok=True)
    row = {
        "audit_id": f"AUD-{uuid.uuid4().hex[:12].upper()}",
        "event_id": event_id,
        "timestamp": now_iso(),
        "actor": "local-user",
        "action": action,
        "details": details,
    }
    with AUDIT_JSONL.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def add_artifact(
    files: list[dict[str, Any]],
    filename: str,
    content: str,
    requirement_id: str,
    description: str,
) -> None:
    destination = FILES_DIR / filename
    if destination.exists():
        raise FileExistsError(f"Artifact আগে থেকেই আছে: {destination}")

    destination.write_text(content, encoding="utf-8")
    stat = destination.stat()

    files.append(
        {
            "id": f"FILE-{uuid.uuid4().hex[:10].upper()}",
            "original_name": destination.name,
            "stored_path": f"files/{destination.name}",
            "extension": destination.suffix.lower(),
            "bytes": stat.st_size,
            "sha256": sha256_file(destination),
            "requirement_id": requirement_id,
            "agenda_id": "",
            "description": description,
            "added_at": now_iso(),
        }
    )


def event_requirements() -> list[dict[str, Any]]:
    entries = [
        ("REQ-001", "MJ-AI-এর উদ্দেশ্য ও MVP সীমারেখা", "product", "collected"),
        ("REQ-002", "Local-first architecture boundary", "architecture", "collected"),
        ("REQ-003", "UI, API, core ও AI layer-এর dependency map", "architecture", "pending"),
        ("REQ-004", "Master agent ও specialist agent responsibilities", "agents", "pending"),
        ("REQ-005", "Conversation, task, context ও session lifecycle", "core", "pending"),
        ("REQ-006", "Short-term, long-term ও vector memory boundary", "memory", "pending"),
        ("REQ-007", "SQLite, ChromaDB, FAISS ও backup strategy", "storage", "pending"),
        ("REQ-008", "LLM model selection ও local/offline fallback", "ai", "pending"),
        ("REQ-009", "Tool permission ও human approval policy", "security", "pending"),
        ("REQ-010", "Terminal sandbox ও file operation policy", "security", "pending"),
        ("REQ-011", "Authentication, encryption ও secret management", "security", "pending"),
        ("REQ-012", "Audit log schema ও tamper-awareness", "governance", "pending"),
        ("REQ-013", "MVP folder tree ও implementation acceptance criteria", "architecture", "pending"),
        ("REQ-014", "Final 48-hour review ও handover record", "handover", "pending"),
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
        for item_id, title, category, status in entries
    ]


def agenda(start: datetime, deadline: datetime) -> list[dict[str, Any]]:
    items = [
        ("AG-001", "MJ-AI vision, users ও MVP scope", 0, 45,
         "Local-first, private, modular এবং multi-agent ব্যবস্থার MVP সীমা ঠিক করা।"),
        ("AG-002", "UI/API/Core/AI layer map", 3, 90,
         "UI থেকে model execution পর্যন্ত request ও response flow চিহ্নিত করা।"),
        ("AG-003", "Agent responsibility map", 8, 90,
         "Master এবং specialist agent-দের অনুমতি ও escalation rule সংজ্ঞায়িত করা।"),
        ("AG-004", "Memory & knowledge architecture", 14, 90,
         "STM, LTM, vector, knowledge graph ও retention policy-এর boundary নির্ধারণ।"),
        ("AG-005", "Security & sandbox baseline", 22, 90,
         "File, terminal, web ও database operations-এর permission policy লেখা।"),
        ("AG-006", "LLM and model strategy", 28, 75,
         "Qwen, Phi, Llama, Gemma-এর MVP selection ও fallback criteria লেখা।"),
        ("AG-007", "MVP folder tree review", 34, 90,
         "প্রস্তাবিত folder tree-কে implementation-ready হালকা কাঠামোতে নেমে নিয়ে আলাদা করা।"),
        ("AG-008", "Tests, observability ও backup", 40, 75,
         "Unit, integration, security, audit এবং backup acceptance criteria লেখা।"),
        ("AG-009", "48-hour handover", 46, 60,
         "Decisions, unresolved items এবং Phase-02 implementation backlog নথিভুক্ত করা।"),
    ]

    result = []
    for item_id, title, offset, duration, notes in items:
        scheduled = start + timedelta(hours=offset)
        if scheduled > deadline:
            scheduled = deadline
        result.append(
            {
                "id": item_id,
                "title": title,
                "start_time": now_iso(scheduled),
                "duration_minutes": duration,
                "owner": "MJ Ahmad",
                "status": "planned",
                "notes": notes,
            }
        )
    return result


def readiness(event: dict[str, Any]) -> dict[str, Any]:
    requirements = event["requirements"]
    required = [
        item for item in requirements
        if item["required"] and item["status"] != "waived"
    ]
    verified = [item for item in required if item["status"] == "verified"]
    percent = round(100 * len(verified) / len(required)) if required else 100

    return {
        "percent": percent,
        "verified_required": len(verified),
        "required_total": len(required),
        "label": "Architecture ও security requirements-এর verified অগ্রগতি",
    }


def event_for_index(event: dict[str, Any]) -> dict[str, Any]:
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
    events: list[dict[str, Any]] = []

    for folder in sorted(EVENTS_DIR.iterdir()) if EVENTS_DIR.exists() else []:
        event_path = folder / "event.json"
        if not folder.is_dir() or not event_path.is_file():
            continue
        try:
            event = json.loads(event_path.read_text(encoding="utf-8"))
            if isinstance(event, dict) and event.get("id"):
                events.append(event_for_index(event))
        except (OSError, json.JSONDecodeError) as error:
            print(f"সতর্কতা: {event_path} পড়া যায়নি: {error}", file=sys.stderr)

    events.sort(
        key=lambda item: (
            item.get("date") or "9999",
            item.get("title", "").lower(),
        )
    )

    write_json(
        INDEX_JSON,
        {
            "schema": "mj-events-index/v1",
            "generated_at": now_iso(),
            "events": events,
        },
    )
    return len(events)


def main() -> None:
    if EVENT_JSON.exists():
        raise SystemExit(
            f"ইভেন্ট আগে থেকেই আছে: {EVENT_JSON}\n"
            "কোনো existing event বা artifact overwrite করা হয়নি।"
        )

    FILES_DIR.mkdir(parents=True, exist_ok=False)

    created = datetime.now(DHAKA)
    deadline = created + timedelta(hours=48)
    event_id = f"EVT-{created:%Y%m%d}-MJ-AI-P1"

    files: list[dict[str, Any]] = []

    add_artifact(
        files,
        "01-event-brief.md",
        f"""# MJ-AI — First Foundation Event

- Event ID: `{event_id}`
- Project: `MJ-AI`
- শুরু: `{now_iso(created)}`
- Deadline: `{now_iso(deadline)}`
- Timezone: `Asia/Dhaka`
- Status: `planning`

## লক্ষ্য

MJ-AI হবে একটি Local-First, Modular, Multi-Agent AI Assistant।
প্রথম 48 ঘণ্টার উদ্দেশ্য হলো implementation না করে:

- architecture boundary স্থির করা
- MVP scope নির্ধারণ করা
- agent ও memory responsibility নির্ধারণ করা
- security এবং sandbox policy সংজ্ঞায়িত করা
- implementation-ready folder structure approve করা

## 48-hour deliverables

- Folder tree ও module responsibility
- UI, API, core ও model execution flow
- Agent contract ও permission matrix
- Memory/data lifecycle
- Security baseline
- LLM selection ও fallback policy
- Test এবং handover checklist

## Scope guardrails

প্রথম ইভেন্টে বাস্তব agent/terminal execution চালু হবে না।
এর মধ্যে থাকবে না:

- destructive terminal capability
- arbitrary file deletion
- external action without approval
- secrets বা passwords repository-তে রাখা
- production deployment
- autonomous long-running actions
- external agent communication
- trained model data publication
""",
        "REQ-001",
        "MJ-AI-এর প্রথম 48-hour planning event brief",
    )

    add_artifact(
        files,
        "02-folder-tree.md",
        """# MJ-AI MVP Folder Tree

## MVP proposal

```text
MJ-AI/
├── README.md
├── pyproject.toml
├── requirements.txt
├── requirements-dev.txt
├── .env.example
├── .gitignore
├── config/
├── core/
├── llm/
├── memory/
├── agents/
├── tools/
├── rag/
├── knowledge/
├── database/
├── api/
├── ui/
├── auth/
├── security/
├── monitoring/
├── logs/
├── tests/
├── docs/
├── deployment/
└── scripts/
```

## MVP Phase-01 priority

### প্রথম পর্যায়

```text
config/
core/
llm/
memory/
agents/master_agent/
agents/coding_agent/
agents/file_agent/
tools/filesystem/
tools/notes/
security/
database/sqlite/
api/
ui/web/
tests/
docs/
scripts/
```

### দ্বিতীয় পর্যায়

```text
agents/research_agent/
agents/vision_agent/
agents/voice_agent/
agents/automation_agent/
agents/security_agent/
rag/
knowledge/
database/chroma/
database/faiss/
api/websocket/
ui/mobile/
ui/desktop/
deployment/
monitoring/
```

## Folder ownership rule

- `core/`: system orchestration—model logic নয়
- `llm/`: model loading, prompt ও inference
- `agents/`: specialist behavior ও agent contracts
- `tools/`: single-purpose, permission-aware operations
- `memory/`: state storage এবং retrieval
- `rag/`: document indexing ও retrieval
- `security/`: authorization এবং threat boundary
- `api/`: external interface
- `ui/`: presentation only
- `logs/`: runtime evidence; secrets নয়
- `deployment/`: environment and packaging
- `tests/`: acceptance evidence
""",
        "REQ-013",
        "MJ-AI-এর MVP ও implementation-ready folder structure",
    )

    add_artifact(
        files,
        "03-layer-map.md",
        """# MJ-AI Layer Map

```text
UI Layer
├── Web UI
├── Mobile UI
└── Desktop UI

API Layer
├── REST API
└── WebSocket

Core Layer
├── Conversation Manager
├── Session Manager
├── Context Manager
├── Task Manager
├── Planner
├── Executor
└── Orchestrator

Agent Layer
├── Master Agent
├── Research Agent
├── Coding Agent
├── File Agent
├── Vision Agent
├── Voice Agent
├── Automation Agent
└── Security Agent

AI/LLM Layer
├── Qwen
├── Phi
├── Llama
└── Gemma

Memory Layer
├── Short-Term Memory
├── Long-Term Memory
├── Vector Store
└── Knowledge Graph

Storage Layer
├── SQLite
├── ChromaDB
├── FAISS
└── Backups

Security Layer
├── Authentication
├── Encryption
├── Audit
├── Sandbox
└── Permissions
```

## Request flow

```text
User
  -> UI
  -> API
  -> Session/Context
  -> Planner
  -> Security permission check
  -> Master Agent
  -> Specialist Agent or Tool
  -> Memory/RAG
  -> LLM
  -> Executor
  -> Audit log
  -> UI response
```

## Dependency rule

- UI layer কখনো সরাসরি database বা model file access করবে না।
- Specialist Agent কখনো implicit permission নেবে না।
- Tool execution-এ permission context বাধ্যতামূলক।
- Core layer UI framework-এর ওপর নির্ভর করবে না।
- LLM layer agent behavior-এ সরাসরি hard-code হবে না।
""",
        "REQ-003",
        "MJ-AI-এর UI/API/Core/Agent/LLM/Memory/Security layer dependency",
    )

    add_artifact(
        files,
        "04-security-baseline.md",
        """# MJ-AI Security Baseline

## Sensitive data policy

- `.env` repository-তে commit করা যাবে না।
- API key, password এবং private token শুধুমাত্র environment/secret manager।
- Logs-এ prompt, secret, credential বা personal raw data রাখা যাবে না।
- Memory record-এ source, timestamp এবং sensitivity level রাখা হবে।

## Permission model

প্রতিটি tool action-এ:

- action
- resource
- agent
- user
- scope
- approval state
- timestamp
- audit ID

## Default permissions

- read: limited and explicit
- write: require scope + confirmation
- move: require confirmation
- delete: explicit human confirmation
- terminal: sandbox and allowlist
- web: deny-by-default unless explicitly enabled
- database: schema-scoped permission
- memory: read/write classification

## Human approval

নিচের operations-এর আগে human confirmation বাধ্যতামূলক:

- Delete
- System-wide package installation
- Source outside workspace access
- Secret access
- Public web publication
- Credential change
- Destructive shell command
- Bulk file operations
- Long-running automation
- External financial or legal actions

## Sandbox

- workspace allowlist
- command allowlist
- timeout
- CPU/RAM limit
- network policy
- process isolation
- artifact quarantine

## Audit

Audit log-কে append-only হিসেবে গণ্য করা যেতে পারে, কিন্তু এটি
single host-এর local log; tamper-proof নয়।
Signed export, backup এবং version-control trail পরে যুক্ত করতে হবে।
""",
        "REQ-009",
        "MJ-AI-এর destructive action, permission ও sandbox guardrail",
    )

    add_artifact(
        files,
        "05-implementation-roadmap.md",
        """# MJ-AI Implementation Roadmap

## Phase 0 — Foundation planning

- scope freeze
- architecture decision
- threat model
- folder structure
- security contract
- test strategy

## Phase 1 — Local conversation MVP

- UI
- FastAPI/REST API
- SQLite
- session/context manager
- local LLM loader
- master agent
- basic chat
- audit logging

## Phase 2 — Memory MVP

- short-term memory
- profile memory
- project memory
- preference memory
- embedding and vector store
- memory router

## Phase 3 — Coding/file agents

- read/write tools
- scoped workspace
- approval flow
- code reviewer
- debugger
- file organizer

## Phase 4 — RAG

- chunker
- embedder
- retriever
- reranker
- source attribution
- data refresh policy

## Phase 5 — Voice & vision

- STT
- TTS
- image OCR
- object analysis
- permission and data retention

## Phase 6 — Automation

- approved workflows
- scheduler
- workflow recovery
- timeout/cancellation
- audit/replay

## Phase 7 — UI expansion

- PWA
- desktop
- mobile
- accessibility
- offline behavior
- notification policy

## Exit criteria for Phase 1

- user can chat locally
- local model can be loaded
- user session persists
- context remains bounded
- tool calls require permission
- audit log records actions
- model failure has fallback
- tests run locally
- backup/restore works
""",
        "REQ-014",
        "48-hour event থেকে implementation পর্যন্ত roadmap",
    )

    add_artifact(
        files,
        "06-acceptance-checklist.md",
        """# MJ-AI 48-hour Acceptance Checklist

- [ ] MVP scope approved
- [ ] Local-first definition approved
- [ ] UI/API/Core boundaries documented
- [ ] Agent responsibilities separated
- [ ] Tool permission contract documented
- [ ] File operation delete rules documented
- [ ] Terminal sandbox allowlist documented
- [ ] Secret management policy documented
- [ ] Memory retention policy documented
- [ ] SQLite/Chroma/FAISS ownership documented
- [ ] Model selection criteria documented
- [ ] Offline/fallback behavior documented
- [ ] Audit schema and retention documented
- [ ] MVP folder tree approved
- [ ] Architecture decision record created
- [ ] Phase 1 implementation tasks listed
- [ ] Security risks and unresolved items listed
- [ ] 48-hour handover file created
- [ ] Final review evidence backup/version controlled

## Do not mark verified

নিচের item কেবল review evidence পাওয়ার পর verified করবেন:

- destructive file operations
- terminal sandbox
- secret handling
- model fallback
- memory privacy
- agent permission
- audit integrity
- restore/backup
""",
        "REQ-014",
        "MJ-AI 48-hour architecture ও security acceptance checklist",
    )

    requirements = event_requirements()
    event = {
        "schema": "mj-event/v1",
        "id": event_id,
        "slug": SLUG,
        "title": "MJ-AI 48-hour Foundation & Architecture Event",
        "event_type": "project-foundation",
        "status": "planning",
        "date": created.date().isoformat(),
        "start_time": now_iso(created),
        "end_time": now_iso(deadline),
        "deadline_at": now_iso(deadline),
        "timezone": "Asia/Dhaka",
        "venue": "MJ-AI repository / local workspace",
        "owner": "MJ Ahmad",
        "purpose": (
            "MJ-AI-এর MVP scope, architecture, memory, agent, security, "
            "LLM fallback, folder structure এবং 48-hour handover "
            "documentation প্রস্তুত করা।"
        ),
        "description": (
            "এটি planning/documentation milestone। Source code, model "
            "download, package installation বা autonomous agent execution "
            "এই ইভেন্টে চালু হয় না।"
        ),
        "scope": {
            "in_scope": [
                "architecture boundaries",
                "MVP folder structure",
                "agent responsibility",
                "local-first model strategy",
                "memory and storage strategy",
                "tool and terminal permissions",
                "secret handling",
                "audit and backup decisions",
                "Phase 1 implementation backlog",
            ],
            "out_of_scope": [
                "production deployment",
                "download or execution of AI models",
                "autonomous external actions",
                "destructive terminal operations",
                "credential or personal secret creation",
                "fully implemented UI/agent system",
            ],
        },
        "agenda": agenda(created, deadline),
        "requirements": requirements,
        "files": files,
        "notes": [
            {
                "id": "NOTE-MJAI-001",
                "text": (
                    "এই ইভেন্ট implementation শুরু করা বা LLM model চালু হওয়ার "
                    "নিশ্চয়তা দেয় না। Readiness percentage শুধু verified "
                    "checklist requirement-এর অবস্থা দেখায়।"
                ),
                "created_at": now_iso(created),
                "actor": "local-user",
            }
        ],
        "created_at": now_iso(created),
        "updated_at": now_iso(created),
    }

    write_json(EVENT_JSON, event)

    append_audit(
        event_id,
        "mj_ai_event_created",
        {
            "slug": SLUG,
            "title": event["title"],
            "deadline_at": event["deadline_at"],
            "artifact_count": len(files),
            "scope": "architecture-and-foundation",
        },
    )

    append_audit(
        event_id,
        "initial_agenda_requirements_created",
        {
            "agenda_count": len(event["agenda"]),
            "requirement_count": len(requirements),
            "initially_collected": [
                item["id"]
                for item in requirements
                if item["status"] == "collected"
            ],
        },
    )

    count = build_index()

    print("MJ-AI foundation event তৈরি হয়েছে।")
    print(f"Event ID : {event_id}")
    print(f"Folder   : {EVENT_DIR.relative_to(ROOT)}")
    print(f"Deadline : {event['deadline_at']} (Asia/Dhaka)")
    print(f"Artifacts: {len(files)}")
    print(f"Events in viewer index: {count}")
    print()
    print("Viewer:")
    print("  ./run.sh serve")
    print("  http://127.0.0.1:8000/events/")


if __name__ == "__main__":
    main()

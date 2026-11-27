#!/usr/bin/env python3
"""
Create a 48-hour cyber-defense training project event.

This event is defensive and educational.
It excludes unauthorized scanning, exploitation, phishing,
malware distribution, credential capture, persistence, and data exfiltration.
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
SLUG = "cyber-defense-training-lab"
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

    record = {
        "audit_id": f"AUD-{uuid.uuid4().hex[:12].upper()}",
        "event_id": event_id,
        "timestamp": now_iso(),
        "actor": "local-user",
        "action": action,
        "details": details,
    }

    with AUDIT_JSONL.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=False) + "\n")


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


def make_requirements() -> list[dict[str, Any]]:
    entries = [
        ("REQ-001", "ইভেন্টের শিক্ষাগত উদ্দেশ্য ও সীমারেখা", "scope", "collected"),
        ("REQ-002", "Authorized lab/environment owner ও অনুমতি", "authorization", "pending"),
        ("REQ-003", "Network, host ও dataset inventory", "scope", "pending"),
        ("REQ-004", "Threat model ও abuse-case list", "risk", "pending"),
        ("REQ-005", "Detection rule ও baseline", "detection", "pending"),
        ("REQ-006", "Alert validation ও false-positive handling", "detection", "pending"),
        ("REQ-007", "Incident severity ও escalation policy", "incident-response", "pending"),
        ("REQ-008", "Containment, eradication ও recovery plan", "incident-response", "pending"),
        ("REQ-009", "Evidence preservation ও chain-of-custody", "forensics", "pending"),
        ("REQ-010", "Backup, snapshot ও restore test", "resilience", "pending"),
        ("REQ-011", "Central logging ও audit retention", "monitoring", "pending"),
        ("REQ-012", "Secrets, PII ও sensitive log handling", "privacy", "pending"),
        ("REQ-013", "Safety drill ও rollback mechanism", "testing", "pending"),
        ("REQ-014", "Tabletop/lab exercise report", "training", "pending"),
        ("REQ-015", "Final review, acceptance ও handover", "handover", "pending"),
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


def make_agenda(start: datetime, deadline: datetime) -> list[dict[str, Any]]:
    blocks = [
        ("AG-001", "Scope ও authorization review", 0, 60,
         "Laboratory-এর owner, অনুমোদিত system ও out-of-scope target লিখে নিন।"),
        ("AG-002", "Asset inventory ও trust boundary", 3, 90,
         "Host, network, account, service, dataset এবং trust boundary নথিভুক্ত করুন।"),
        ("AG-003", "Threat modeling", 7, 90,
         "STRIDE বা অন্য approved method দিয়ে threat ও abuse scenario তৈরি করুন।"),
        ("AG-004", "Logging ও detection baseline", 12, 120,
         "Authentication, endpoint, DNS, network এবং application telemetry map করুন।"),
        ("AG-005", "Detection rules ও validation", 20, 120,
         "Benign lab scenario দিয়ে rule এবং false-positive behavior test করুন।"),
        ("AG-006", "Incident response tabletop", 27, 90,
         "Role, escalation, containment এবং communication exercise পরিচালনা করুন।"),
        ("AG-007", "Backup ও recovery exercise", 34, 120,
         "Snapshot বা backup থেকে isolated restore test করুন।"),
        ("AG-008", "Evidence handling ও audit review", 40, 75,
         "Hash, timestamp, chain of custody এবং audit trail পরীক্ষা করুন।"),
        ("AG-009", "Final lesson report ও handover", 46, 90,
         "Lesson learned, unresolved risk, rollback এবং পরবর্তী drill নির্ধারণ করুন।"),
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
                "start_time": now_iso(scheduled),
                "duration_minutes": duration,
                "owner": "MJ Ahmad",
                "status": "planned",
                "notes": notes,
            }
        )

    return agenda


def readiness(event: dict[str, Any]) -> dict[str, Any]:
    requirements = event["requirements"]
    required = [
        item
        for item in requirements
        if item["required"] and item["status"] != "waived"
    ]
    verified = [
        item
        for item in required
        if item["status"] == "verified"
    ]

    percent = round(100 * len(verified) / len(required)) if required else 100

    return {
        "percent": percent,
        "verified_required": len(verified),
        "required_total": len(required),
        "label": "Defensive preparation ও verified requirements",
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
    event_id = f"EVT-{created:%Y%m%d}-CYBER-DEFENSE-P1"

    files: list[dict[str, Any]] = []

    add_artifact(
        files,
        "01-event-brief.md",
        f"""# Cyber Defense Training Lab — Event Brief

- Event ID: `{event_id}`
- শুরু: `{now_iso(created)}`
- Deadline: `{now_iso(deadline)}`
- Timezone: `Asia/Dhaka`
- Focus: defensive cybersecurity education

## উদ্দেশ্য

এই 48-hour event-এর লক্ষ্য হলো একটি isolated training lab তৈরি করে:

- threat modeling শিখতে
- attack indicator ও signal চিনতে
- log ও telemetry বিশ্লেষণ করতে
- incident response drill করতে
- evidence preservation শিখতে
- backup এবং recovery যাচাই করতে
- false positive ও risk reduce করতে

## প্রবৃত্তি

এই lab:

- authorized system এবং isolated environment-এ চলবে
- real public serviceকে target করবে না
- credential harvesting ব্যবহার করবে না
- malware বা exploitকে external channel-এ ছাড়বে না
- unauthorized person বা third-party data নিয়ে কাজ করবে না
- destructive command চালাবে না

## 48-hour deliverables

- authorization record
- asset and network inventory
- threat model
- detection baseline
- incident response plan
- recovery plan
- audit and evidence log
- tabletop exercise report
- accepted risk and handover record
""",
        "REQ-001",
        "Cyber defense training event-এর উদ্দেশ্য ও সীমারেখা",
    )

    add_artifact(
        files,
        "02-lab-boundaries.md",
        """# Authorized Training Lab Boundaries

## Allowed

- isolated virtual machines
- localhost or private lab network
- synthetic identities and fake accounts
- benign test files
- defensive SIEM/EDR-style simulation
- tabletop incident exercises
- approved open-source defensive tools
- snapshot and restore testing
- log collection and analysis
- MITRE ATT&CK-like mapping for learning

## Forbidden

- unauthorized host scan
- public internet exploitation
- credential theft
- real phishing
- malware distribution
- persistence backdoor
- lateral movement outside lab
- data exfiltration
- denial-of-service against a third party
- covert monitoring
- exposing personal or sensitive data

## Rule before every drill

- [ ] Asset owner confirmed
- [ ] Lab isolation confirmed
- [ ] Test window documented
- [ ] Rollback tested
- [ ] Data sanitized
- [ ] Observers/participants identified
- [ ] Stop condition defined
- [ ] Emergency contact identified
""",
        "REQ-002",
        "Authorized lab, safe boundary ও stop conditions",
    )

    add_artifact(
        files,
        "03-threat-model.md",
        """# Defensive Threat Model

## Example analysis method

STRIDE:

- Spoofing
- Tampering
- Repudiation
- Information disclosure
- Denial of service
- Elevation of privilege

## Initial assets

- user accounts
- application configuration
- database
- backup snapshots
- local logs
- source code
- secrets
- network configuration
- API keys
- training datasets
- monitoring infrastructure

## Example scenarios

- unauthorized account login
- suspicious privileged action
- unexpected configuration change
- unusual outbound request
- suspicious file modification
- log deletion attempt
- repeated authentication failure
- backup integrity mismatch
- unsafe package or dependency update
- service unavailable due to misconfiguration

## Required evidence

প্রতিটি scenario-এর জন্য নথিভুক্ত করুন:

- asset
- threat
- precondition
- attack indicator
- telemetry source
- detection
- containment
- recovery
- residual risk
""",
        "REQ-004",
        "Threat model ও defensive scenario inventory",
    )

    add_artifact(
        files,
        "04-detection-plan.md",
        """# Detection Plan

## Recommended telemetry

- authentication logs
- endpoint process logs
- DNS or proxy logs
- firewall summaries
- application logs
- database audit logs
- file integrity monitoring
- backup verification logs
- container logs
- configuration changes

## Detection categories

- account misuse
- privilege misuse
- suspicious process behavior
- unexpected file modification
- configuration drift
- service disruption
- abnormal network communication
- unsafe package installation
- repeated login failures
- audit log gaps

## Rule lifecycle

1. Define baseline
2. Define benign test
3. Create detection
4. Validate in isolated lab
5. Review false positives
6. Approve threshold
7. Record owner
8. Schedule review

Never connect an untested destructive action directly to production.
""",
        "REQ-005",
        "Logging source, detection rule ও validation plan",
    )

    add_artifact(
        files,
        "05-incident-response.md",
        """# Incident Response Plan

## Response phases

1. Detect
2. Triage
3. Contain
4. Preserve evidence
5. Eradicate
6. Recover
7. Review

## Severity example

### SEV-1

- active compromise
- broad data exposure
- production service unavailable
- security boundary failure

### SEV-2

- suspicious but contained activity
- limited account or host impact
- partial service degradation

### SEV-3

- low-risk anomaly
- false positive or weak signal
- no observed harm

## Roles

- Incident lead
- Technical responder
- Evidence custodian
- Communications owner
- Recovery owner
- Training observer

## Immediate stop conditions

- real user data appears
- lab isolation fails
- unauthorized network route appears
- destructive behavior escapes approval
- monitoring becomes unreliable
- backup integrity is uncertain
""",
        "REQ-007",
        "Incident severity, containment ও escalation procedure",
    )

    add_artifact(
        files,
        "06-recovery-backup.md",
        """# Backup & Recovery Exercise

## Backup target

- configuration
- source code
- database schema and safe training data
- monitoring configuration
- detection rules
- event documentation
- audit logs
- infrastructure-as-code

## Recovery test

1. Record source checksums
2. Create isolated snapshot
3. Remove or isolate affected lab copy
4. Restore from snapshot or backup
5. Verify integrity
6. Verify service health
7. Verify logs
8. Record recovery time
9. Record unresolved loss
10. Restore safety controls

## Do not restore

- live secrets
- real customer data
- unknown malware
- unverified database dumps
- credentials outside lab boundary
""",
        "REQ-010",
        "Backup, restore ও recovery acceptance test",
    )

    add_artifact(
        files,
        "07-logging-audit.md",
        """# Logging & Evidence Handling

## Audit fields

- audit_id
- timestamp
- actor
- action
- resource
- event_id
- source host
- result
- approval state
- evidence reference

## Evidence handling

- calculate SHA-256 for exported evidence
- preserve original and working copies separately
- record collection time
- record collector
- record transfer destination
- maintain access log
- redact passwords, keys and personal data
- establish retention period
- define deletion approval

## Limit

Local append-only JSON/text log is not cryptographically tamper-proof.
Sign exports, use version control or secured audit storage when stronger
integrity is required.
""",
        "REQ-011",
        "Audit schema, evidence handling ও chain-of-custody",
    )

    add_artifact(
        files,
        "08-acceptance-checklist.md",
        """# Cyber Defense Training Acceptance Checklist

- [ ] Authorization record exists
- [ ] Lab is isolated
- [ ] Real targets are excluded
- [ ] Asset inventory complete
- [ ] Threat model reviewed
- [ ] Logging sources identified
- [ ] Detection baseline established
- [ ] False-positive validation complete
- [ ] Incident severity policy approved
- [ ] Containment stop conditions approved
- [ ] Evidence handling procedure tested
- [ ] Backup integrity verified
- [ ] Restore test successful
- [ ] Secrets and PII excluded from logs
- [ ] Tabletop exercise completed
- [ ] Recovery time documented
- [ ] Lessons learned recorded
- [ ] Residual risk approved
- [ ] 48-hour handover evidence stored

## Verification rule

Verified status কেবল corresponding evidence দেখে এবং reviewer acceptance
রেকর্ড করা হলে দিন। Readiness 100% মানেই:
- attack safe
- system fully secure
- compliance complete
- production-ready
এমন বলা যাবে না।
""",
        "REQ-015",
        "Cyber defense 48-hour event-এর final acceptance criteria",
    )

    event = {
        "schema": "mj-event/v1",
        "id": event_id,
        "slug": SLUG,
        "title": "Cyber Defense Training Lab — 48 Hour Event",
        "event_type": "cybersecurity-training",
        "status": "planning",
        "date": created.date().isoformat(),
        "start_time": now_iso(created),
        "end_time": now_iso(deadline),
        "deadline_at": now_iso(deadline),
        "timezone": "Asia/Dhaka",
        "venue": "Isolated local training lab",
        "owner": "MJ Ahmad",
        "purpose": (
            "Authorized, isolated এবং educational cyber-defense lab planning "
            "through threat modeling, detection, incident response, evidence "
            "handling and recovery."
        ),
        "description": (
            "এই event offensive security test নয়। এটি defensive education, "
            "authorized tabletop exercise এবং safe lab preparation-এর জন্য।"
        ),
        "scope": {
            "in_scope": [
                "authorized lab inventory",
                "threat modeling",
                "detection planning",
                "incident response tabletop",
                "backup and recovery test",
                "evidence handling",
                "audit logging",
                "residual risk review",
            ],
            "out_of_scope": [
                "unauthorized scanning",
                "public exploitation",
                "real credential harvesting",
                "malware distribution",
                "denial-of-service",
                "real user data collection",
                "production deployment",
                "offensive cyber-attack operation",
            ],
        },
        "agenda": make_agenda(created, deadline),
        "requirements": make_requirements(),
        "files": files,
        "notes": [
            {
                "id": "NOTE-CYBER-001",
                "text": (
                    "এই ইভেন্ট defensive training-এর প্রস্তুতি নথিভুক্ত করে। "
                    "কোনও system attack বা incident test চালানোর আগে explicit "
                    "authorization এবং isolated environment নিশ্চিত করতে হবে।"
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
        "cyber_defense_event_created",
        {
            "slug": SLUG,
            "title": event["title"],
            "deadline_at": event["deadline_at"],
            "artifact_count": len(files),
            "scope": "defensive-training-only",
        },
    )

    append_audit(
        event_id,
        "initial_agenda_requirements_created",
        {
            "agenda_count": len(event["agenda"]),
            "requirement_count": len(event["requirements"]),
            "initially_collected": [
                item["id"]
                for item in event["requirements"]
                if item["status"] == "collected"
            ],
        },
    )

    count = build_index()

    print("Cyber-defense training event তৈরি হয়েছে।")
    print(f"Event ID : {event_id}")
    print(f"Folder   : {EVENT_DIR.relative_to(ROOT)}")
    print(f"Deadline : {event['deadline_at']} (Asia/Dhaka)")
    print(f"Artifacts: {len(files)}")
    print(f"Events in viewer: {count}")
    print()
    print("পরবর্তীতে চালান:")
    print("  python3 scripts/event_manager.py build-index")
    print("  ./run.sh serve")
    print("  http://127.0.0.1:8000/events/")


if __name__ == "__main__":
    main()

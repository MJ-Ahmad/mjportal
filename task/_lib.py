#!/usr/bin/env python3
"""Storage core: locked, atomic, audited and migrated access to data.json.

Every write runs inside transaction(). It holds an exclusive file lock, loads
the database through migrate_database(), lets the caller mutate it, writes
atomically and appends one line to audit.jsonl.
"""

import os
import re
import json
import fcntl
import shutil
import hashlib
import tempfile
from contextlib import contextmanager
from datetime import datetime, timezone, timedelta, date

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, "data.json")
REGISTRY_FILE = os.path.join(BASE_DIR, "registry.json")
LOCK_FILE = os.path.join(BASE_DIR, ".tasks.lock")
AUDIT_FILE = os.path.join(BASE_DIR, "audit.jsonl")
CONFIG_FILE = os.path.join(BASE_DIR, "config.json")
SECRET_FILE = os.path.join(BASE_DIR, ".secret")
ATTACH_DIR = os.path.join(BASE_DIR, "attachments")
BACKUP_DIR = os.path.join(BASE_DIR, "backups")
ASSETS_DIR = os.path.join(BASE_DIR, "assets")

SCHEMA_VERSION = 3
FMT = "%Y-%m-%d %H:%M:%S.%f"
DHAKA_TZ = timezone(timedelta(hours=6))
PRIORITIES = ("none", "low", "medium", "high")
REPEATS = ("none", "daily", "weekly", "monthly")
TASK_ID_RE = re.compile(r"^TASK-\d{6}$")
REG_ID_RE = re.compile(r"^REG-\d{6}$")
LIST_ID_RE = re.compile(r"^[a-z0-9][a-z0-9-]{0,19}$")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
TIME_RE = re.compile(r"^([01]\d|2[0-3]):[0-5]\d$")
DEFAULT_LIST = {"id": "inbox", "name": "Inbox", "color": "#2b6cb0"}


class TaskError(Exception):
    """A user-facing error. Shown as a message, never as a stack trace."""


# ---------------------------------------------------------------- time

def now_stamps():
    utc = datetime.now(timezone.utc)
    return {"dhaka": utc.astimezone(DHAKA_TZ).strftime(FMT)[:-3],
            "utc": utc.strftime(FMT)[:-3]}


def today_dhaka():
    return datetime.now(DHAKA_TZ).date().isoformat()


# ---------------------------------------------------------------- files

def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path, data):
    """Atomic write: temp file, fsync, then rename. A crash never leaves half a file."""
    fd, tmp = tempfile.mkstemp(dir=os.path.dirname(path), suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)
    except BaseException:
        if os.path.exists(tmp):
            os.remove(tmp)
        raise


def _ensure_dirs():
    for folder in (ATTACH_DIR, ASSETS_DIR, BACKUP_DIR):
        os.makedirs(folder, exist_ok=True)


@contextmanager
def _locked():
    with open(LOCK_FILE, "w") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        yield


def _create_missing_files():
    """Runs under the lock so two first-time commands cannot overwrite each other."""
    if not os.path.exists(DATA_FILE):
        save_json(DATA_FILE, {"schema_version": SCHEMA_VERSION,
                              "lists": [dict(DEFAULT_LIST)], "tasks": []})
    if not os.path.exists(REGISTRY_FILE):
        save_json(REGISTRY_FILE, {"last_registry": 0, "last_task": 0})


def ensure_structure():
    _ensure_dirs()
    with _locked():
        _create_missing_files()


@contextmanager
def transaction(action, ref=None):
    _ensure_dirs()
    with _locked():
        _create_missing_files()
        data = migrate_database(load_json(DATA_FILE))
        registry = load_json(REGISTRY_FILE)
        yield data, registry
        save_json(DATA_FILE, data)
        save_json(REGISTRY_FILE, registry)
        append_audit(action, ref)


def append_audit(action, ref=None):
    entry = {"ts_utc": now_stamps()["utc"], "action": action}
    if ref:
        entry["ref"] = ref
    with open(AUDIT_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def read_database():
    _ensure_dirs()
    with _locked():
        _create_missing_files()
    return migrate_database(load_json(DATA_FILE)), load_json(REGISTRY_FILE)


# ---------------------------------------------------------------- migration

LEGACY_KEYS = ("stage", "client", "client_visible", "summary", "next_steps", "instructions",
               "references", "figures", "overview", "evaluation", "heading_en", "heading_bn",
               "description_en", "description_bn", "group", "progress")
PRIORITY_FROM_V2 = {"low": "low", "normal": "none", "high": "high", "urgent": "high"}


def migrate_database(data):
    """Bring any earlier format up to schema v3, in memory. Nothing is discarded:
    fields that no longer have a place are kept under task['legacy']."""
    if not isinstance(data, dict) or not isinstance(data.get("tasks"), list):
        raise TaskError("data.json is malformed: 'tasks' must be a list")
    lists = [l for l in data.get("lists", []) if isinstance(l, dict) and LIST_ID_RE.match(str(l.get("id", "")))]
    if not any(l["id"] == "inbox" for l in lists):
        lists.insert(0, dict(DEFAULT_LIST))
    data["lists"] = lists
    for task in data["tasks"]:
        if task.get("schema_version") == SCHEMA_VERSION:
            _fill_defaults(task)
        else:
            _upgrade_legacy(task, data)
    data["schema_version"] = SCHEMA_VERSION
    return data


def _fill_defaults(task):
    defaults = {
        "title": "", "body": "", "list": "inbox", "status": "open", "important": False,
        "my_day": False, "priority": "none", "due": "", "due_time": "", "repeat": "none",
        "tags": [], "checklist": [], "comments": [], "attachments": [], "history": [],
        "created_dhaka": "", "created_utc": "", "updated_dhaka": "", "updated_utc": "",
        "done_dhaka": None, "done_utc": None, "deleted_utc": "", "legacy": {},
    }
    for key, value in defaults.items():
        task.setdefault(key, value if not isinstance(value, (list, dict)) else type(value)())


def _list_for_name(data, name):
    for lst in data["lists"]:
        if lst["name"] == name:
            return lst["id"]
    numbers = [int(l["id"][1:]) for l in data["lists"] if re.fullmatch(r"l\d+", l["id"])]
    new_id = f"l{max(numbers, default=0) + 1}"
    data["lists"].append({"id": new_id, "name": name, "color": "#7a5af8"})
    return new_id


def _convert_items(items):
    out = []
    for item in items or []:
        out.append({
            "id": int(item.get("id")),
            "title": item.get("title", ""),
            "done": bool(item.get("completed")),
            "done_dhaka": item.get("completed_dhaka"),
            "done_utc": item.get("completed_utc"),
        })
    return out


def _convert_steps(steps):
    out = []
    for step in steps or []:
        item = _convert_items([step])[0]
        item["children"] = _convert_items(step.get("sub_steps", []))
        out.append(item)
    return out


def _convert_notes(notes):
    out = []
    for index, note in enumerate(notes or [], start=1):
        if isinstance(note, str):
            out.append({"id": index, "text": note, "kind": "note", "author": "mj-ahmad", "dhaka": "", "utc": ""})
        else:
            out.append({"id": int(note.get("id", index)), "text": note.get("text", ""),
                        "kind": note.get("kind", "note"), "author": note.get("author", "mj-ahmad"),
                        "dhaka": note.get("dhaka", ""), "utc": note.get("utc", "")})
    return out


def _upgrade_legacy(task, data):
    legacy = {key: task.pop(key) for key in LEGACY_KEYS if key in task}
    old_status = task.pop("status", "active")
    old_priority = task.pop("priority", "normal")
    group = (legacy.get("group") or "").strip()
    list_id = _list_for_name(data, group) if group else "inbox"
    history = task.pop("history", [])
    created_utc = task.get("created_utc", "")
    updated = history[-1] if history else {"dhaka": task.get("created_dhaka", ""), "utc": created_utc}

    new = {
        "task_id": task["task_id"],
        "registry": task["registry"],
        "title": task.pop("heading", ""),
        "body": task.pop("description", ""),
        "list": list_id,
        "status": "done" if old_status == "completed" else "open",
        "important": old_priority == "urgent",
        "my_day": False,
        "priority": PRIORITY_FROM_V2.get(old_priority, "none"),
        "due": task.pop("due", "") or "",
        "due_time": "",
        "repeat": "none",
        "tags": task.pop("tags", []),
        "checklist": _convert_steps(task.pop("steps", [])),
        "comments": _convert_notes(task.pop("notes", [])),
        "attachments": task.pop("attachments", []),
        "history": history,
        "created_dhaka": task.pop("created_dhaka", ""),
        "created_utc": created_utc,
        "updated_dhaka": updated.get("dhaka", ""),
        "updated_utc": updated.get("utc", ""),
        "done_dhaka": task.pop("completed_dhaka", None),
        "done_utc": task.pop("completed_utc", None),
        "deleted_utc": "",
        "schema_version": SCHEMA_VERSION,
        "legacy": legacy,
    }
    for key in ("overview", "evaluation"):
        if key in task:
            new["legacy"][key] = task.pop(key)
    task.clear()
    task.update(new)


# ---------------------------------------------------------------- attachments

def sha256_file(path):
    digest = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def store_attachment(task_id, file_path, index):
    import mimetypes
    original = os.path.basename(file_path)
    extension = re.sub(r"[^a-z0-9.]", "", os.path.splitext(original)[1].lower())[:10]
    name = f"{task_id}-{index:02d}{extension}"
    destination = os.path.join(ATTACH_DIR, name)
    shutil.copy2(file_path, destination)
    return {
        "file": f"attachments/{name}", "original": original,
        "size": os.path.getsize(destination),
        "mime": mimetypes.guess_type(destination)[0] or "application/octet-stream",
        "sha256": sha256_file(destination), "added_utc": now_stamps()["utc"],
    }


# ---------------------------------------------------------------- integrity

def validate_database(data, registry):
    errors, warnings = [], []
    list_ids = {l["id"] for l in data.get("lists", [])}
    seen_tasks, seen_regs = set(), set()
    max_task = max_reg = 0
    counts = {"open": 0, "done": 0, "deleted": 0}

    for task in data.get("tasks", []):
        tid = str(task.get("task_id", "<missing>"))
        if not TASK_ID_RE.match(tid):
            errors.append(f"{tid}: bad task_id")
        if tid in seen_tasks:
            errors.append(f"{tid}: duplicate task_id")
        seen_tasks.add(tid)
        rid = str(task.get("registry", ""))
        if not REG_ID_RE.match(rid):
            errors.append(f"{tid}: bad registry id '{rid}'")
        if rid in seen_regs:
            errors.append(f"{tid}: duplicate registry id {rid}")
        seen_regs.add(rid)
        if TASK_ID_RE.match(tid):
            max_task = max(max_task, int(tid[5:]))
        if REG_ID_RE.match(rid):
            max_reg = max(max_reg, int(rid[4:]))

        if not str(task.get("title", "")).strip():
            errors.append(f"{tid}: empty title")
        if task.get("status") not in ("open", "done"):
            errors.append(f"{tid}: invalid status")
        if task.get("priority") not in PRIORITIES:
            errors.append(f"{tid}: invalid priority")
        if task.get("repeat") not in REPEATS:
            errors.append(f"{tid}: invalid repeat")
        if task.get("list") not in list_ids:
            errors.append(f"{tid}: unknown list '{task.get('list')}'")
        if task.get("due") and not DATE_RE.match(task["due"]):
            errors.append(f"{tid}: invalid due date")
        if task.get("due_time") and not TIME_RE.match(task["due_time"]):
            errors.append(f"{tid}: invalid due time")
        if task.get("status") == "done" and not task.get("done_utc"):
            errors.append(f"{tid}: done without done_utc")

        ids = [i["id"] for i in task.get("checklist", [])]
        if len(ids) != len(set(ids)):
            errors.append(f"{tid}: duplicate checklist ids")
        for item in task.get("checklist", []):
            kids = item.get("children", [])
            if kids and item["done"] != all(k["done"] for k in kids):
                errors.append(f"{tid}: checklist {item['id']} out of sync with its sub-items")

        for att in task.get("attachments", []):
            path = os.path.join(BASE_DIR, att.get("file", ""))
            if not os.path.isfile(path):
                errors.append(f"{tid}: missing attachment {att.get('file')}")
            elif sha256_file(path) != att.get("sha256"):
                errors.append(f"{tid}: checksum mismatch {att.get('file')}")

        if task.get("deleted_utc"):
            counts["deleted"] += 1
        else:
            counts[task.get("status", "open")] = counts.get(task.get("status", "open"), 0) + 1

    if registry.get("last_task", 0) < max_task:
        errors.append("registry.last_task is behind the highest TASK id")
    if registry.get("last_registry", 0) < max_reg:
        errors.append("registry.last_registry is behind the highest REG id")
    if data.get("schema_version") != SCHEMA_VERSION:
        warnings.append("data.json is not schema v3; run './run.sh migrate'")
    return errors, warnings, {"tasks": len(data.get("tasks", [])), **counts,
                              "lists": len(list_ids), "last_task": registry.get("last_task", 0)}

#!/usr/bin/env python3
"""Shared core for the Stewardship Task System.

All task database reads/writes, IDs, timestamps, progress and validation
helpers live here. Existing flat-step records remain supported; new steps
include parent_id and step-specific notes.
"""

import hashlib
import json
import mimetypes
import os
import re
import shutil
import tempfile
from datetime import datetime, timezone, timedelta

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, "data.json")
REGISTRY_FILE = os.path.join(BASE_DIR, "registry.json")
ATTACHMENTS_DIR = os.path.join(BASE_DIR, "attachments")
ASSETS_DIR = os.path.join(BASE_DIR, "assets")

DHAKA_TZ = timezone(timedelta(hours=6))
TS_FORMAT = "%Y-%m-%d %H:%M:%S.%f"

VALID_STATUSES = ("active", "completed")
TASK_ID_RE = re.compile(r"^TASK-\d{6}$")
REG_ID_RE = re.compile(r"^REG-\d{6}$")


# ---------------------------------------------------------------- time

def now_stamps():
    """Return the current moment as Dhaka and UTC strings."""
    utc_now = datetime.now(timezone.utc)
    return {
        "dhaka": utc_now.astimezone(DHAKA_TZ).strftime(TS_FORMAT)[:-3],
        "utc": utc_now.strftime(TS_FORMAT)[:-3],
    }


# ---------------------------------------------------------------- storage

def load_json(path):
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def save_json(path, data):
    """Write JSON atomically so an interrupted write does not corrupt the file."""
    directory = os.path.dirname(os.path.abspath(path))
    os.makedirs(directory, exist_ok=True)

    fd, temporary_path = tempfile.mkstemp(dir=directory, suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(data, handle, indent=4, ensure_ascii=False)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())

        os.replace(temporary_path, path)
    except BaseException:
        if os.path.exists(temporary_path):
            os.remove(temporary_path)
        raise


def ensure_structure():
    """Create folders and empty database files on first use."""
    os.makedirs(ATTACHMENTS_DIR, exist_ok=True)
    os.makedirs(ASSETS_DIR, exist_ok=True)

    if not os.path.exists(DATA_FILE):
        save_json(DATA_FILE, {"tasks": []})

    if not os.path.exists(REGISTRY_FILE):
        save_json(REGISTRY_FILE, {"last_registry": 0, "last_task": 0})


# ---------------------------------------------------------------- IDs

def generate_ids():
    """Allocate the next TASK-XXXXXX and REG-XXXXXX IDs."""
    registry = load_json(REGISTRY_FILE)

    if not isinstance(registry, dict):
        raise ValueError("registry.json must contain a JSON object")

    last_registry = int(registry.get("last_registry", 0))
    last_task = int(registry.get("last_task", 0))

    registry["last_registry"] = last_registry + 1
    registry["last_task"] = last_task + 1
    save_json(REGISTRY_FILE, registry)

    return (
        f"TASK-{registry['last_task']:06d}",
        f"REG-{registry['last_registry']:06d}",
    )


# ---------------------------------------------------------------- attachments

def sha256_file(path):
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def store_attachment(task_id, file_path):
    """Copy a file into attachments/ and return metadata."""
    if not os.path.isfile(file_path):
        return None

    original = os.path.basename(file_path)
    extension = os.path.splitext(original)[1].lower()
    save_name = f"{task_id}{extension}"
    destination = os.path.join(ATTACHMENTS_DIR, save_name)

    # Keep the existing task-ID naming scheme, but do not silently overwrite
    # a previous attachment with the same extension.
    if os.path.exists(destination):
        stem, suffix = os.path.splitext(save_name)
        counter = 2
        while os.path.exists(os.path.join(ATTACHMENTS_DIR, f"{stem}-{counter}{suffix}")):
            counter += 1
        save_name = f"{stem}-{counter}{suffix}"
        destination = os.path.join(ATTACHMENTS_DIR, save_name)

    shutil.copy2(file_path, destination)

    return {
        "file": f"attachments/{save_name}",
        "original": original,
        "size": os.path.getsize(destination),
        "mime": mimetypes.guess_type(destination)[0] or "application/octet-stream",
        "sha256": sha256_file(destination),
    }


# ---------------------------------------------------------------- steps

def create_steps(step_string):
    """Turn comma-separated titles into numbered top-level step records."""
    if not step_string:
        return []

    titles = [item.strip() for item in step_string.split(",") if item.strip()]

    return [
        {
            "id": index,
            "parent_id": None,
            "title": title,
            "completed": False,
            "completed_dhaka": None,
            "completed_utc": None,
            "notes": [],
        }
        for index, title in enumerate(titles, start=1)
    ]


def calculate_progress(task):
    """Recompute task progress from every step, including nested steps."""
    steps = task.get("steps", [])
    if not isinstance(steps, list):
        steps = []

    total = len(steps)
    completed = sum(1 for step in steps if step.get("completed"))

    task["progress"] = {
        "completed": completed,
        "remaining": total - completed,
        "percentage": int(completed / total * 100) if total else 0,
    }
    return task["progress"]


def find_task(task_id, data):
    for task in data.get("tasks", []):
        if task.get("task_id") == task_id:
            return task
    return None


def append_history(task, action, stamps):
    task.setdefault("history", []).append({
        "dhaka": stamps["dhaka"],
        "utc": stamps["utc"],
        "action": action,
    })


# ---------------------------------------------------------------- completion

def build_completion_report(task):
    """Build a factual archive summary from the stored task record."""
    steps = task.get("steps", [])
    total = len(steps)
    completed = sum(1 for step in steps if step.get("completed"))
    progress = task.get("progress") or {}
    percentage = progress.get("percentage", 0)

    overview = (
        "Task record marked complete.\n\n"
        f"Task:\n{task.get('heading', '')}\n\n"
        "The task's tracked steps were completed before archival.\n"
        "Review supporting notes and attachments separately when needed.\n\n"
        f"Tracked step completion: {percentage}%\n"
    )

    evaluation = {
        "steps_total": total,
        "steps_completed": completed,
        "completion_percentage": percentage,
        "notes": len(task.get("notes", [])),
        "attachments": len(task.get("attachments", [])),
        "archive_ready": True,
    }

    return overview, evaluation


# ---------------------------------------------------------------- integrity

def validate_database(data, registry):
    """Return (errors, summary). Empty errors means the database is consistent."""
    errors = []

    if not isinstance(data, dict):
        return ["data.json must contain a JSON object"], {}

    tasks = data.get("tasks")
    if not isinstance(tasks, list):
        return ["'tasks' must be a list"], {}

    if not isinstance(registry, dict):
        return ["registry.json must contain a JSON object"], {}

    seen_task_ids = set()
    seen_reg_ids = set()
    total_steps = completed_steps = active = completed = 0
    max_task_no = max_reg_no = 0

    for task in tasks:
        if not isinstance(task, dict):
            errors.append("A task record is not a JSON object")
            continue

        task_id = str(task.get("task_id", "<missing>"))
        registry_id = str(task.get("registry", "<missing>"))

        if not TASK_ID_RE.fullmatch(task_id):
            errors.append(f"{task_id}: bad task_id format")
        if not REG_ID_RE.fullmatch(registry_id):
            errors.append(f"{task_id}: bad registry format ({registry_id})")

        if task_id in seen_task_ids:
            errors.append(f"{task_id}: duplicate task_id")
        seen_task_ids.add(task_id)

        if registry_id in seen_reg_ids:
            errors.append(f"{task_id}: duplicate registry ({registry_id})")
        seen_reg_ids.add(registry_id)

        if TASK_ID_RE.fullmatch(task_id):
            max_task_no = max(max_task_no, int(task_id.split("-")[1]))
        if REG_ID_RE.fullmatch(registry_id):
            max_reg_no = max(max_reg_no, int(registry_id.split("-")[1]))

        status = task.get("status")
        if status not in VALID_STATUSES:
            errors.append(f"{task_id}: invalid status '{status}'")

        if not str(task.get("heading", "")).strip():
            errors.append(f"{task_id}: empty heading")

        steps = task.get("steps", [])
        if not isinstance(steps, list):
            errors.append(f"{task_id}: steps must be a list")
            steps = []

        step_ids = []
        for step in steps:
            if not isinstance(step, dict):
                errors.append(f"{task_id}: a step is not a JSON object")
                continue
            step_ids.append(step.get("id"))

        try:
            if len(step_ids) != len(set(step_ids)):
                errors.append(f"{task_id}: duplicate step ids")
        except TypeError:
            errors.append(f"{task_id}: step IDs must be scalar values")

        step_by_id = {
            step.get("id"): step
            for step in steps
            if isinstance(step, dict) and step.get("id") is not None
        }

        for step in steps:
            if not isinstance(step, dict):
                continue

            step_id = step.get("id")
            parent_id = step.get("parent_id")

            # Old database records do not have parent_id; that is equivalent to None.
            if parent_id is not None:
                if parent_id not in step_by_id:
                    errors.append(
                        f"{task_id} step {step_id}: parent step {parent_id} not found"
                    )
                elif parent_id == step_id:
                    errors.append(f"{task_id} step {step_id}: cannot be its own parent")

            if not isinstance(step.get("title", ""), str):
                errors.append(f"{task_id} step {step_id}: title must be a string")

            if step.get("completed"):
                if not step.get("completed_utc") or not step.get("completed_dhaka"):
                    errors.append(
                        f"{task_id} step {step_id}: completed without timestamps"
                    )
            elif step.get("completed_utc") or step.get("completed_dhaka"):
                errors.append(
                    f"{task_id} step {step_id}: timestamps on an incomplete step"
                )

            notes = step.get("notes", [])
            if notes is not None and not isinstance(notes, list):
                errors.append(f"{task_id} step {step_id}: notes must be a list")

        # Detect parent cycles in the flat parent_id representation.
        for step_id in step_by_id:
            visited = set()
            current_id = step_id

            while current_id in step_by_id:
                if current_id in visited:
                    errors.append(f"{task_id} step {step_id}: parent cycle detected")
                    break
                visited.add(current_id)
                current_id = step_by_id[current_id].get("parent_id")

                if current_id is None:
                    break

        done = sum(
            1 for step in steps
            if isinstance(step, dict) and step.get("completed")
        )

        progress = task.get("progress", {})
        if not isinstance(progress, dict):
            errors.append(f"{task_id}: progress must be an object")
            progress = {}

        expected_percentage = int(done / len(steps) * 100) if steps else 0
        if progress.get("completed") != done:
            errors.append(
                f"{task_id}: progress.completed={progress.get('completed')} "
                f"but {done} steps are completed"
            )
        if progress.get("remaining") != len(steps) - done:
            errors.append(
                f"{task_id}: progress.remaining={progress.get('remaining')} "
                f"but {len(steps) - done} steps remain"
            )
        if progress.get("percentage") != expected_percentage:
            errors.append(
                f"{task_id}: progress.percentage={progress.get('percentage')} "
                f"but expected {expected_percentage}"
            )

        if status == "completed" and done != len(steps):
            errors.append(f"{task_id}: marked completed with unfinished steps")

        attachments = task.get("attachments", [])
        if not isinstance(attachments, list):
            errors.append(f"{task_id}: attachments must be a list")
            attachments = []

        for attachment in attachments:
            if not isinstance(attachment, dict):
                errors.append(f"{task_id}: an attachment record is not an object")
                continue

            relative = str(attachment.get("file", ""))
            normalized = os.path.normpath(relative)
            expected_prefix = "attachments" + os.sep

            if (
                os.path.isabs(relative)
                or normalized == ".."
                or normalized.startswith(".." + os.sep)
                or not normalized.startswith(expected_prefix)
            ):
                errors.append(f"{task_id}: unsafe attachment path {relative}")
                continue

            full_path = os.path.abspath(os.path.join(BASE_DIR, normalized))
            attachments_root = os.path.abspath(ATTACHMENTS_DIR)

            try:
                inside_attachment_dir = os.path.commonpath(
                    [full_path, attachments_root]
                ) == attachments_root
            except ValueError:
                inside_attachment_dir = False

            if not inside_attachment_dir:
                errors.append(f"{task_id}: unsafe attachment path {relative}")
            elif not os.path.isfile(full_path):
                errors.append(f"{task_id}: missing attachment file {relative}")

        total_steps += len(steps)
        completed_steps += done

        if status == "active":
            active += 1
        elif status == "completed":
            completed += 1

    try:
        last_task = int(registry.get("last_task", 0))
        last_registry = int(registry.get("last_registry", 0))
    except (TypeError, ValueError):
        last_task = last_registry = 0
        errors.append("registry counters must be integers")

    if last_task < max_task_no:
        errors.append("registry.last_task is behind the highest TASK id")
    if last_registry < max_reg_no:
        errors.append("registry.last_registry is behind the highest REG id")

    summary = {
        "total_tasks": len(tasks),
        "active_tasks": active,
        "completed_tasks": completed,
        "total_steps": total_steps,
        "completed_steps": completed_steps,
        "last_registry": registry.get("last_registry", 0),
        "last_task": registry.get("last_task", 0),
    }

    return errors, summary

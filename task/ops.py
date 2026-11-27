#!/usr/bin/env python3
"""Task operations shared by the CLI and the web API.

Each public operation is a handler `h_<name>(ctx, **args)`. run() validates the
arguments, opens a locked transaction and calls the handler. Handlers only
change data; they never write files themselves.
"""

import os
import re
import inspect
import calendar
from datetime import date, timedelta

from _lib import (TaskError, transaction, now_stamps, today_dhaka, store_attachment,
                  BASE_DIR, PRIORITIES, REPEATS, DATE_RE, TIME_RE, LIST_ID_RE, DEFAULT_LIST)

WEB_OPS = {
    "create", "update", "toggle", "check_add", "check_set", "check_del",
    "comment_add", "comment_del", "delete", "restore", "purge",
    "list_add", "list_update", "list_delete",
}
UPDATABLE = ("title", "body", "list", "important", "my_day", "priority", "due", "due_time", "repeat", "tags")


class Ctx:
    def __init__(self, data, registry, stamps):
        self.data, self.registry, self.stamps = data, registry, stamps


# ---------------------------------------------------------------- helpers

def resolve_ref(ref):
    text = str(ref).strip().upper()
    if re.fullmatch(r"\d{1,6}", text):
        text = f"TASK-{int(text):06d}"
    return text


def find_task(ctx, ref):
    task_id = resolve_ref(ref)
    task = next((t for t in ctx.data["tasks"] if t["task_id"] == task_id), None)
    if task is None:
        raise TaskError(f"Task not found: {task_id}")
    return task


def find_list(ctx, list_id):
    lst = next((l for l in ctx.data["lists"] if l["id"] == list_id), None)
    if lst is None:
        raise TaskError(f"List not found: {list_id}")
    return lst


def next_int_id(items):
    return max((int(i["id"]) for i in items), default=0) + 1


def log(task, action, ctx):
    task["history"].append({"dhaka": ctx.stamps["dhaka"], "utc": ctx.stamps["utc"], "action": action})
    task["updated_dhaka"] = ctx.stamps["dhaka"]
    task["updated_utc"] = ctx.stamps["utc"]


def parse_due(text):
    """Accepts '', 'today', 'tomorrow', '+3d', '+2w', or YYYY-MM-DD. Returns ISO date or ''."""
    value = (text or "").strip().lower()
    if value in ("", "none", "-"):
        return ""
    today = date.fromisoformat(today_dhaka())
    if value == "today":
        return today.isoformat()
    if value == "tomorrow":
        return (today + timedelta(days=1)).isoformat()
    match = re.fullmatch(r"\+(\d{1,3})([dw])", value)
    if match:
        days = int(match.group(1)) * (7 if match.group(2) == "w" else 1)
        return (today + timedelta(days=days)).isoformat()
    if DATE_RE.match(value):
        try:
            return date.fromisoformat(value).isoformat()
        except ValueError:
            pass
    raise TaskError(f"Invalid due date '{text}'. Use YYYY-MM-DD, today, tomorrow or +3d.")


def check_fields(ctx, fields):
    """Validate and normalise editable fields. Returns the cleaned dict."""
    clean = {}
    for key, value in fields.items():
        if key not in UPDATABLE:
            raise TaskError(f"Field cannot be changed: {key}")
        if key == "title":
            value = str(value or "").strip()
            if not value:
                raise TaskError("Title must not be empty")
        elif key == "body":
            value = str(value or "")
        elif key == "list":
            find_list(ctx, value)
        elif key in ("important", "my_day"):
            value = bool(value)
        elif key == "priority":
            if value not in PRIORITIES:
                raise TaskError(f"Invalid priority. Use one of: {', '.join(PRIORITIES)}")
        elif key == "due":
            value = parse_due(value)
        elif key == "due_time":
            value = str(value or "").strip()
            if value and not TIME_RE.match(value):
                raise TaskError("Invalid time. Use HH:MM (24-hour)")
        elif key == "repeat":
            if value not in REPEATS:
                raise TaskError(f"Invalid repeat. Use one of: {', '.join(REPEATS)}")
        elif key == "tags":
            if isinstance(value, str):
                value = [t.strip() for t in value.split(",")]
            value = [str(t).strip().lstrip("#") for t in value if str(t).strip()]
            value = list(dict.fromkeys(value))
        clean[key] = value
    return clean


def advance_due(task, today):
    """Next occurrence after the current due date (or today) for a repeating task."""
    base = date.fromisoformat(task["due"]) if task["due"] else date.fromisoformat(today)
    step = {"daily": 1, "weekly": 7}.get(task["repeat"])
    while True:
        if step:
            base = base + timedelta(days=step)
        else:
            year, month = (base.year + (base.month // 12), base.month % 12 + 1)
            base = date(year, month, min(base.day, calendar.monthrange(year, month)[1]))
        if base.isoformat() > today:
            return base.isoformat()


def _set_done(item, done, ctx):
    item["done"] = done
    item["done_dhaka"] = ctx.stamps["dhaka"] if done else None
    item["done_utc"] = ctx.stamps["utc"] if done else None


def _find_item(task, item_id, parent_id=None):
    container = task["checklist"]
    if parent_id is not None:
        parent = next((i for i in task["checklist"] if i["id"] == int(parent_id)), None)
        if parent is None:
            raise TaskError(f"Checklist item not found: {parent_id}")
        container = parent["children"]
    item = next((i for i in container if i["id"] == int(item_id)), None)
    if item is None:
        raise TaskError(f"Checklist item not found: {item_id}")
    return item, (task["checklist"] if parent_id is None else None), container


# ---------------------------------------------------------------- task handlers

def h_create(ctx, title, body="", list="inbox", important=False, my_day=False, priority="none",
             due="", due_time="", repeat="none", tags=None, checklist=None):
    fields = check_fields(ctx, {"title": title, "body": body, "list": list, "important": important,
                                "my_day": my_day, "priority": priority, "due": due,
                                "due_time": due_time, "repeat": repeat, "tags": tags or []})
    ctx.registry["last_task"] += 1
    ctx.registry["last_registry"] += 1
    task_id = f"TASK-{ctx.registry['last_task']:06d}"
    task = {
        "task_id": task_id, "registry": f"REG-{ctx.registry['last_registry']:06d}",
        "title": fields["title"], "body": fields.get("body", ""), "list": fields["list"],
        "status": "open", "important": fields["important"], "my_day": fields["my_day"],
        "priority": fields["priority"], "due": fields["due"], "due_time": fields["due_time"],
        "repeat": fields["repeat"], "tags": fields["tags"], "checklist": [], "comments": [],
        "attachments": [], "history": [], "created_dhaka": ctx.stamps["dhaka"],
        "created_utc": ctx.stamps["utc"], "updated_dhaka": ctx.stamps["dhaka"],
        "updated_utc": ctx.stamps["utc"], "done_dhaka": None, "done_utc": None,
        "deleted_utc": "", "schema_version": 3, "legacy": {},
    }
    for index, text in enumerate(checklist or [], start=1):
        if str(text).strip():
            task["checklist"].append({"id": index, "title": str(text).strip(), "done": False,
                                      "done_dhaka": None, "done_utc": None, "children": []})
    log(task, "Task created", ctx)
    ctx.data["tasks"].insert(0, task)
    return task


def h_update(ctx, ref, **fields):
    task = find_task(ctx, ref)
    clean = check_fields(ctx, fields)
    changed = [k for k, v in clean.items() if task.get(k) != v]
    if not changed:
        return task
    task.update({k: clean[k] for k in changed})
    if "due" in changed and not clean["due"]:
        task["due_time"] = ""
    if task["repeat"] != "none" and not task["due"]:
        task["due"] = today_dhaka()
    log(task, "Edited: " + ", ".join(changed), ctx)
    return task


def h_toggle(ctx, ref):
    task = find_task(ctx, ref)
    if task["status"] == "done":
        task["status"] = "open"
        task["done_dhaka"] = task["done_utc"] = None
        log(task, "Reopened", ctx)
        return task
    if task["repeat"] != "none":
        base_due = advance_due(task, today_dhaka())
        task["due"] = base_due
        for item in task["checklist"]:
            item["done"], item["done_utc"], item["done_dhaka"] = False, None, None
            for child in item["children"]:
                child["done"], child["done_utc"], child["done_dhaka"] = False, None, None
        log(task, f"Completed; repeats, next due {base_due}", ctx)
        return task
    task["status"] = "done"
    task["done_dhaka"] = ctx.stamps["dhaka"]
    task["done_utc"] = ctx.stamps["utc"]
    log(task, "Completed", ctx)
    return task


def h_check_add(ctx, ref, title, parent=None):
    task = find_task(ctx, ref)
    text = str(title or "").strip()
    if not text:
        raise TaskError("Checklist item must not be empty")
    if parent is None:
        item = {"id": next_int_id(task["checklist"]), "title": text, "done": False,
                "done_dhaka": None, "done_utc": None, "children": []}
        task["checklist"].append(item)
    else:
        parent_item, _, _ = _find_item(task, parent)
        item = {"id": next_int_id(parent_item["children"]), "title": text, "done": False,
                "done_dhaka": None, "done_utc": None}
        parent_item["children"].append(item)
        if parent_item["done"]:
            _set_done(parent_item, False, ctx)
    log(task, f"Checklist item added: {text}", ctx)
    return task


def h_check_set(ctx, ref, item, parent=None, done=None, title=None):
    task = find_task(ctx, ref)
    target, _, _ = _find_item(task, item, parent)
    if title is not None:
        text = str(title).strip()
        if not text:
            raise TaskError("Checklist item must not be empty")
        target["title"] = text
    if done is not None:
        done = bool(done)
        _set_done(target, done, ctx)
        if parent is None:
            for child in target["children"]:
                _set_done(child, done, ctx)
        else:
            parent_item, _, _ = _find_item(task, parent)
            kids = parent_item["children"]
            all_done = all(k["done"] for k in kids)
            if all_done != parent_item["done"]:
                _set_done(parent_item, all_done, ctx)
    log(task, f"Checklist updated: {target['title']}", ctx)
    return task


def h_check_del(ctx, ref, item, parent=None):
    task = find_task(ctx, ref)
    target, top, container = _find_item(task, item, parent)
    container.remove(target)
    if parent is not None:
        parent_item, _, _ = _find_item(task, parent)
        if parent_item["children"] and all(k["done"] for k in parent_item["children"]) and not parent_item["done"]:
            _set_done(parent_item, True, ctx)
    log(task, f"Checklist item removed: {target['title']}", ctx)
    return task


def h_comment_add(ctx, ref, text):
    task = find_task(ctx, ref)
    body = str(text or "").strip()
    if not body:
        raise TaskError("Comment must not be empty")
    task["comments"].append({"id": next_int_id(task["comments"]), "text": body, "kind": "note",
                             "author": "mj-ahmad", "dhaka": ctx.stamps["dhaka"], "utc": ctx.stamps["utc"]})
    log(task, "Comment added", ctx)
    return task


def h_comment_del(ctx, ref, comment):
    task = find_task(ctx, ref)
    before = len(task["comments"])
    task["comments"] = [c for c in task["comments"] if c["id"] != int(comment)]
    if len(task["comments"]) == before:
        raise TaskError(f"Comment not found: {comment}")
    log(task, "Comment removed", ctx)
    return task


def h_delete(ctx, ref):
    task = find_task(ctx, ref)
    task["deleted_utc"] = ctx.stamps["utc"]
    log(task, "Moved to trash", ctx)
    return task


def h_restore(ctx, ref):
    task = find_task(ctx, ref)
    task["deleted_utc"] = ""
    log(task, "Restored from trash", ctx)
    return task


def h_purge(ctx, ref):
    task = find_task(ctx, ref)
    if not task["deleted_utc"]:
        raise TaskError("Only tasks in the trash can be purged. Delete them first.")
    for att in task["attachments"]:
        path = os.path.join(BASE_DIR, att["file"])
        if os.path.isfile(path):
            os.remove(path)
    ctx.data["tasks"].remove(task)
    return {"purged": task["task_id"]}


def h_attach(ctx, ref, path):
    task = find_task(ctx, ref)
    if not os.path.isfile(path):
        raise TaskError(f"File not found: {path}")
    task["attachments"].append(store_attachment(task["task_id"], path, len(task["attachments"]) + 1))
    log(task, f"File attached: {os.path.basename(path)}", ctx)
    return task


# ---------------------------------------------------------------- list handlers

def h_list_add(ctx, name):
    text = str(name or "").strip()
    if not text:
        raise TaskError("List name must not be empty")
    numbers = [int(l["id"][1:]) for l in ctx.data["lists"] if re.fullmatch(r"l\d+", l["id"])]
    new = {"id": f"l{max(numbers, default=0) + 1}", "name": text, "color": "#7a5af8"}
    ctx.data["lists"].append(new)
    return new


def h_list_update(ctx, list_id, name=None, color=None):
    lst = find_list(ctx, list_id)
    if name is not None:
        text = str(name).strip()
        if not text:
            raise TaskError("List name must not be empty")
        lst["name"] = text
    if color is not None:
        if not re.fullmatch(r"#[0-9a-fA-F]{6}", str(color)):
            raise TaskError("Colour must be like #7a5af8")
        lst["color"] = color
    return lst


def h_list_delete(ctx, list_id):
    if list_id == "inbox":
        raise TaskError("The Inbox list cannot be deleted")
    lst = find_list(ctx, list_id)
    moved = 0
    for task in ctx.data["tasks"]:
        if task["list"] == list_id:
            task["list"] = "inbox"
            log(task, f"Moved to Inbox (list '{lst['name']}' deleted)", ctx)
            moved += 1
    ctx.data["lists"].remove(lst)
    return {"deleted": list_id, "moved_tasks": moved}


HANDLERS = {
    "create": h_create, "update": h_update, "toggle": h_toggle,
    "check_add": h_check_add, "check_set": h_check_set, "check_del": h_check_del,
    "comment_add": h_comment_add, "comment_del": h_comment_del,
    "delete": h_delete, "restore": h_restore, "purge": h_purge, "attach": h_attach,
    "list_add": h_list_add, "list_update": h_list_update, "list_delete": h_list_delete,
}


def run(op, **args):
    """Execute one operation atomically. Raises TaskError for user mistakes."""
    handler = HANDLERS.get(op)
    if handler is None:
        raise TaskError(f"Unknown operation: {op}")
    try:
        inspect.signature(handler).bind(None, **args)
    except TypeError as exc:
        raise TaskError(f"Invalid arguments for {op}: {exc}")
    ref = args.get("ref") or args.get("list_id")
    with transaction(op, ref) as (data, registry):
        ctx = Ctx(data, registry, now_stamps())
        return handler(ctx, **args)

#!/usr/bin/env python3
"""Command-line interface for the task system.

Short forms work everywhere: `42` means TASK-000042, `today` / `tomorrow` /
`+3d` are valid due dates, and `3.2` addresses sub-item 2 of checklist item 3.
"""

import os
import sys
import argparse
import getpass

import _lib
import ops
from _lib import TaskError, read_database, PRIORITIES, REPEATS

MARK = {True: "[x]", False: "[ ]"}
PRIO_LABEL = {"none": "", "low": "!", "medium": "!!", "high": "!!!"}


def show_line(task, lists):
    list_name = next((l["name"] for l in lists if l["id"] == task["list"]), task["list"])
    star = "★ " if task["important"] else ""
    due = ""
    if task["due"]:
        due = f"  due {task['due']}" + (f" {task['due_time']}" if task["due_time"] else "")
    rep = f"  ↻{task['repeat']}" if task["repeat"] != "none" else ""
    done = [i for i in task["checklist"] if i["done"]]
    steps = f"  {len(done)}/{len(task['checklist'])}" if task["checklist"] else ""
    prio = f" {PRIO_LABEL[task['priority']]}" if PRIO_LABEL[task["priority"]] else ""
    return (f"{task['task_id'][5:]:>6} {MARK[task['status'] == 'done']} {star}{task['title']}{prio}"
            f"   ({list_name}{due}{rep}{steps})")


def print_task(task, lists):
    print()
    print(f"{task['task_id']}  {MARK[task['status'] == 'done']}  {task['title']}")
    lst = next((l["name"] for l in lists if l["id"] == task["list"]), task["list"])
    print(f"List: {lst}   Priority: {task['priority']}   Repeat: {task['repeat']}"
          f"   Starred: {task['important']}   My Day: {task['my_day']}")
    if task["due"]:
        print(f"Due : {task['due']} {task['due_time']}".rstrip())
    if task["tags"]:
        print("Tags: " + ", ".join("#" + t for t in task["tags"]))
    if task["body"]:
        print(f"\n{task['body']}")
    if task["checklist"]:
        print("\nChecklist:")
        for item in task["checklist"]:
            print(f"  {item['id']:>2}. {MARK[item['done']]} {item['title']}")
            for child in item["children"]:
                print(f"      {item['id']}.{child['id']} {MARK[child['done']]} {child['title']}")
    if task["comments"]:
        print("\nComments:")
        for c in task["comments"]:
            print(f"  #{c['id']} {c['dhaka']}  {c['text']}")
    if task["attachments"]:
        print("\nFiles:")
        for a in task["attachments"]:
            print(f"  {a['file']}  ({a['original']})")
    print(f"\nCreated {task['created_dhaka']} (Dhaka)   Updated {task['updated_dhaka']} (Dhaka)")
    print()


def parse_step(text):
    try:
        if "." in text:
            a, b = text.split(".", 1)
            return int(a), int(b)
        return int(text), None
    except ValueError:
        raise TaskError(f"Invalid item reference '{text}'. Use N or N.M")


def view_filter(view, data):
    """Return a predicate for `taskctl ls <view>`."""
    key = view.lower()
    named = {
        "all": lambda t: t["status"] == "open",
        "today": lambda t: t["my_day"] and t["status"] == "open",
        "myday": lambda t: t["my_day"] and t["status"] == "open",
        "important": lambda t: t["important"] and t["status"] == "open",
        "planned": lambda t: bool(t["due"]) and t["status"] == "open",
        "done": lambda t: t["status"] == "done",
        "trash": lambda t: bool(t["deleted_utc"]),
    }
    if key in named:
        pred = named[key]
    else:
        list_id = next((l["id"] for l in data["lists"]
                        if l["id"] == key or l["name"].lower() == key), None)
        if list_id is None:
            raise TaskError(f"Unknown view or list: {view}")
        pred = lambda t: t["list"] == list_id and t["status"] == "open"
    if key == "trash":
        return pred
    return lambda t: not t["deleted_utc"] and pred(t)


def sort_key(task):
    prio_rank = {"high": 0, "medium": 1, "low": 2, "none": 3}[task["priority"]]
    return (task["due"] or "9999", task["due_time"] or "99:99", prio_rank, task["task_id"])


# ---------------------------------------------------------------- commands

def cmd_init(args):
    _lib.ensure_structure()
    print("Ready: data.json, registry.json, attachments/, backups/")


def cmd_add(args):
    title = " ".join(args.title).strip()
    kwargs = dict(title=title, body=args.note or "", list=args.list or "inbox",
                  important=args.star, my_day=args.myday, priority=args.priority,
                  due=ops.parse_due(args.due) if args.due else "", due_time=args.time or "",
                  repeat=args.repeat, tags=args.tag or [], checklist=args.step or [])
    task = ops.run("create", **kwargs)
    if args.file:
        for path in args.file:
            task = ops.run("attach", ref=task["task_id"], path=path)
    print(f"Added {task['task_id']}: {task['title']}")


def cmd_ls(args):
    data, _ = read_database()
    pred = view_filter(args.view, data)
    rows = sorted((t for t in data["tasks"] if pred(t)), key=sort_key)
    if args.view.lower() == "all" and args.done:
        rows += sorted((t for t in data["tasks"] if t["status"] == "done" and not t["deleted_utc"]),
                       key=sort_key)
    if not rows:
        print("Nothing here.")
        return
    for t in rows:
        print(show_line(t, data["lists"]))
    print(f"\n{len(rows)} task(s)")


def cmd_show(args):
    data, _ = read_database()
    task = ops.find_task(ops.Ctx(data, None, None), args.ref)
    print_task(task, data["lists"])


def cmd_done(args):
    for ref in args.refs:
        task = ops.run("toggle", ref=ref)
        if task["status"] == "done":
            print(f"Done: {task['task_id']} {task['title']}")
        else:
            print(f"{task['task_id']} {task['title']} (next due {task['due']})")


def cmd_undo(args):
    task = ops.run("toggle", ref=args.ref)
    print(f"Reopened: {task['task_id']} {task['title']}")


def cmd_edit(args):
    fields = {}
    if args.title is not None: fields["title"] = args.title
    if args.body is not None: fields["body"] = args.body
    if args.list is not None: fields["list"] = args.list
    if args.due is not None: fields["due"] = args.due
    if args.time is not None: fields["due_time"] = args.time
    if args.priority is not None: fields["priority"] = args.priority
    if args.repeat is not None: fields["repeat"] = args.repeat
    if args.tags is not None: fields["tags"] = args.tags
    if not fields:
        raise TaskError("Nothing to change. Use --title, --body, --list, --due, --time, --priority, --repeat or --tags")
    task = ops.run("update", ref=args.ref, **fields)
    print(f"Updated {task['task_id']}")


def cmd_flag(args, field, value):
    task = ops.run("update", ref=args.ref, **{field: value})
    labels = {("important", True): "starred", ("important", False): "unstarred",
              ("my_day", True): "added to My Day", ("my_day", False): "removed from My Day"}
    print(f"{task['task_id']}: {labels[(field, value)]}")


def cmd_step(args):
    if args.action == "add":
        task = ops.run("check_add", ref=args.ref, title=args.text, parent=args.under)
        print(f"Added checklist item to {task['task_id']}")
        return
    number, sub = parse_step(args.item)
    if args.action in ("done", "undo"):
        if sub is None:
            task = ops.run("check_set", ref=args.ref, item=number, done=args.action == "done")
        else:
            task = ops.run("check_set", ref=args.ref, item=sub, parent=number, done=args.action == "done")
        print(f"{args.action.capitalize()}: {task['task_id']} item {args.item}")
    elif args.action == "rename":
        if sub is None:
            task = ops.run("check_set", ref=args.ref, item=number, title=args.text)
        else:
            task = ops.run("check_set", ref=args.ref, item=sub, parent=number, title=args.text)
        print(f"Renamed item {args.item}")
    else:  # rm
        if sub is None:
            task = ops.run("check_del", ref=args.ref, item=number)
        else:
            task = ops.run("check_del", ref=args.ref, item=sub, parent=number)
        print(f"Removed item {args.item}")


def cmd_note(args):
    if args.action == "add":
        ops.run("comment_add", ref=args.ref, text=args.text)
        print(f"Comment added to {args.ref}")
    else:
        ops.run("comment_del", ref=args.ref, comment=args.text)
        print(f"Comment removed")


def cmd_trash(args):
    if args.action == "rm":
        for ref in args.refs:
            task = ops.run("delete", ref=ref)
            print(f"Moved to trash: {task['task_id']}")
    elif args.action == "restore":
        for ref in args.refs:
            task = ops.run("restore", ref=ref)
            print(f"Restored: {task['task_id']}")
    else:
        for ref in args.refs:
            result = ops.run("purge", ref=ref)
            print(f"Permanently deleted: {result['purged']}")


def cmd_list(args):
    if args.action == "ls":
        data, _ = read_database()
        counts = {}
        for t in data["tasks"]:
            if t["status"] == "open" and not t["deleted_utc"]:
                counts[t["list"]] = counts.get(t["list"], 0) + 1
        for l in data["lists"]:
            print(f"{l['id']:<10} {l['name']:<24} {counts.get(l['id'], 0):>3} open  {l['color']}")
    elif args.action == "add":
        lst = ops.run("list_add", name=args.name)
        print(f"Created list {lst['id']}: {lst['name']}")
    elif args.action == "rename":
        ops.run("list_update", list_id=args.id, name=args.name)
        print(f"Renamed {args.id}")
    elif args.action == "color":
        ops.run("list_update", list_id=args.id, color=args.name)
        print(f"Colour set for {args.id}")
    else:
        result = ops.run("list_delete", list_id=args.id)
        print(f"Deleted {args.id}; {result['moved_tasks']} task(s) moved to Inbox")


def cmd_attach(args):
    task = ops.run("attach", ref=args.ref, path=args.path)
    print(f"Attached to {task['task_id']}")


def cmd_passwd(args):
    pw = getpass.getpass("New password: ")
    if len(pw) < 8:
        raise TaskError("Password must be at least 8 characters")
    if getpass.getpass("Repeat password: ") != pw:
        raise TaskError("Passwords do not match")
    import auth
    auth.write_password(pw)
    print("Password saved (config.json, readable only by you).")


def cmd_serve(args):
    import server
    server.main(["--port", str(args.port)])


def cmd_validate(args):
    try:
        data, registry = read_database()
    except (OSError, ValueError, TaskError) as exc:
        print(f"Validation failed: cannot read database: {exc}")
        return 1
    errors, warnings, summary = _lib.validate_database(data, registry)
    if errors:
        print("Validation failed\n")
        for e in errors:
            print(f"  - {e}")
        print(f"\n{len(errors)} problem(s).")
        return 1
    print("Database OK")
    for w in warnings:
        print(f"  ! {w}")
    print(f"Tasks: {summary['tasks']}  open: {summary['open']}  done: {summary['done']}  "
          f"trash: {summary['deleted']}  lists: {summary['lists']}")
    return 0


def cmd_migrate(args):
    import shutil
    from datetime import datetime
    _lib.ensure_structure()
    dest = os.path.join(_lib.BACKUP_DIR, "pre-migrate-" + datetime.now().strftime("%Y%m%d-%H%M%S"))
    os.makedirs(dest, exist_ok=True)
    for path in (_lib.DATA_FILE, _lib.REGISTRY_FILE):
        shutil.copy2(path, dest)
    with _lib.transaction("migrate to schema v3") as (data, _):
        pass
    print(f"Migrated to schema v{_lib.SCHEMA_VERSION}. Backup: {dest}")


def cmd_backup(args):
    import shutil
    from datetime import datetime
    dest = os.path.join(_lib.BACKUP_DIR, "backup-" + datetime.now().strftime("%Y%m%d-%H%M%S"))
    os.makedirs(dest)
    for name in ("data.json", "registry.json", "audit.jsonl"):
        if os.path.exists(os.path.join(_lib.BASE_DIR, name)):
            shutil.copy2(os.path.join(_lib.BASE_DIR, name), dest)
    if os.path.isdir(_lib.ATTACH_DIR):
        shutil.copytree(_lib.ATTACH_DIR, os.path.join(dest, "attachments"))
    print(f"Backup written to {dest}")


# ---------------------------------------------------------------- parser

def build_parser():
    p = argparse.ArgumentParser(prog="taskctl", description="Task manager command line")
    sub = p.add_subparsers(dest="command", metavar="COMMAND")
    sub.required = True

    a = sub.add_parser("add", help="add a task")
    a.add_argument("title", nargs="+")
    a.add_argument("-l", "--list", help="list id or inbox (default inbox)")
    a.add_argument("-d", "--due", help="today, tomorrow, +3d, or YYYY-MM-DD")
    a.add_argument("-t", "--time", help="HH:MM")
    a.add_argument("-p", "--priority", choices=PRIORITIES, default="none")
    a.add_argument("-r", "--repeat", choices=REPEATS, default="none")
    a.add_argument("-s", "--star", action="store_true", help="mark important")
    a.add_argument("-m", "--myday", action="store_true", help="add to My Day")
    a.add_argument("-n", "--note", help="body text")
    a.add_argument("--tag", action="append")
    a.add_argument("--step", action="append", help="checklist item (repeatable)")
    a.add_argument("--file", action="append", help="attach a file (repeatable)")
    a.set_defaults(func=cmd_add)

    ls = sub.add_parser("ls", help="list tasks: all, today, important, planned, done, trash, or a list")
    ls.add_argument("view", nargs="?", default="all")
    ls.add_argument("--done", action="store_true", help="include completed tasks (with 'all')")
    ls.set_defaults(func=cmd_ls)

    sh = sub.add_parser("show", help="show one task")
    sh.add_argument("ref"); sh.set_defaults(func=cmd_show)

    dn = sub.add_parser("done", help="complete task(s); repeating tasks advance instead")
    dn.add_argument("refs", nargs="+"); dn.set_defaults(func=cmd_done)

    ud = sub.add_parser("undo", help="reopen a completed task")
    ud.add_argument("ref"); ud.set_defaults(func=cmd_undo)

    ed = sub.add_parser("edit", help="change fields of a task")
    ed.add_argument("ref")
    ed.add_argument("--title"); ed.add_argument("--body"); ed.add_argument("--list")
    ed.add_argument("--due"); ed.add_argument("--time"); ed.add_argument("--priority", choices=PRIORITIES)
    ed.add_argument("--repeat", choices=REPEATS); ed.add_argument("--tags", help="comma-separated")
    ed.set_defaults(func=cmd_edit)

    for name, field, value, help_text in (
        ("star", "important", True, "mark as important"),
        ("unstar", "important", False, "remove importance"),
        ("myday", "my_day", True, "add to My Day"),
        ("unmyday", "my_day", False, "remove from My Day"),
    ):
        x = sub.add_parser(name, help=help_text)
        x.add_argument("ref")
        x.set_defaults(func=lambda args, f=field, v=value: cmd_flag(args, f, v))

    st = sub.add_parser("step", help="checklist: add, done, undo, rename, rm (N or N.M)")
    sts = st.add_subparsers(dest="action", required=True)
    x = sts.add_parser("add"); x.add_argument("ref"); x.add_argument("text"); x.add_argument("--under", type=int)
    for name in ("done", "undo", "rm"):
        x = sts.add_parser(name); x.add_argument("ref"); x.add_argument("item")
    x = sts.add_parser("rename"); x.add_argument("ref"); x.add_argument("item"); x.add_argument("text")
    st.set_defaults(func=cmd_step)

    nt = sub.add_parser("note", help="comments: add or rm")
    nts = nt.add_subparsers(dest="action", required=True)
    x = nts.add_parser("add"); x.add_argument("ref"); x.add_argument("text")
    x = nts.add_parser("rm"); x.add_argument("ref"); x.add_argument("text", help="comment id")
    nt.set_defaults(func=cmd_note)

    rm = sub.add_parser("rm", help="move task(s) to trash")
    rm.add_argument("refs", nargs="+"); rm.set_defaults(func=cmd_trash, action="rm")
    rs = sub.add_parser("restore", help="restore task(s) from trash")
    rs.add_argument("refs", nargs="+"); rs.set_defaults(func=cmd_trash, action="restore")
    pg = sub.add_parser("purge", help="permanently delete task(s) in trash")
    pg.add_argument("refs", nargs="+"); pg.set_defaults(func=cmd_trash, action="purge")

    li = sub.add_parser("list", help="manage lists")
    lis = li.add_subparsers(dest="action", required=True)
    lis.add_parser("ls")
    x = lis.add_parser("add"); x.add_argument("name")
    x = lis.add_parser("rename"); x.add_argument("id"); x.add_argument("name")
    x = lis.add_parser("color"); x.add_argument("id"); x.add_argument("name", help="#rrggbb")
    x = lis.add_parser("rm"); x.add_argument("id")
    li.set_defaults(func=cmd_list)

    at = sub.add_parser("attach", help="attach a file to a task")
    at.add_argument("ref"); at.add_argument("path"); at.set_defaults(func=cmd_attach)

    sub.add_parser("passwd", help="set the web login password").set_defaults(func=cmd_passwd)
    sv = sub.add_parser("serve", help="run the web app")
    sv.add_argument("--port", type=int, default=8000); sv.set_defaults(func=cmd_serve)
    sub.add_parser("init", help="create data files").set_defaults(func=cmd_init)
    sub.add_parser("validate", help="check database").set_defaults(func=cmd_validate)
    sub.add_parser("migrate", help="upgrade data to schema v3 (backs up first)").set_defaults(func=cmd_migrate)
    sub.add_parser("backup", help="copy data, audit log and attachments").set_defaults(func=cmd_backup)
    return p


def main(argv=None):
    args = build_parser().parse_args(argv)
    try:
        return args.func(args) or 0
    except TaskError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except BrokenPipeError:
        os.dup2(os.open(os.devnull, os.O_WRONLY), sys.stdout.fileno())
        sys.exit(1)

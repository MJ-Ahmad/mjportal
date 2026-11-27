#!/usr/bin/env python3
"""Add nested task steps and timestamped notes without changing task IDs."""

import argparse
import sys

from _lib import (
    DATA_FILE,
    append_history,
    calculate_progress,
    find_task,
    load_json,
    now_stamps,
    save_json,
)


def fail(message):
    raise SystemExit(f"\n{message}\n")


def find_step(task, step_id):
    """Steps are stored flat; parent_id describes their nested display position."""
    return next(
        (step for step in task.get("steps", []) if step.get("id") == step_id),
        None,
    )


def add_step(args):
    title = args.title.strip()
    if not title:
        fail("Step title cannot be empty.")

    data = load_json(DATA_FILE)
    task = find_task(args.task_id.strip().upper(), data)

    if not task:
        fail(f"Task not found: {args.task_id}")

    if task.get("status") == "completed":
        fail("Cannot add a step to a completed task.")

    steps = task.setdefault("steps", [])

    parent = None
    if args.parent is not None:
        parent = find_step(task, args.parent)
        if parent is None:
            fail(f"Parent step not found: {args.parent}")
        if parent.get("completed"):
            fail("Cannot add a child under a completed step.")

    step_id = max(
        (int(step.get("id", 0)) for step in steps),
        default=0,
    ) + 1

    step = {
        "id": step_id,
        "parent_id": args.parent,
        "title": title,
        "completed": False,
        "completed_dhaka": None,
        "completed_utc": None,
        "notes": [],
    }
    steps.append(step)

    stamps = now_stamps()
    calculate_progress(task)
    parent_label = f" under step {args.parent}" if args.parent is not None else ""
    append_history(task, f"Added step {step_id}{parent_label}: {title}", stamps)
    save_json(DATA_FILE, data)

    print(f"Step added: {step_id}")
    print(f"Task      : {task['task_id']}")
    print(f"Parent    : {args.parent if args.parent is not None else 'top-level'}")
    print(f"Title     : {title}")


def add_note(args):
    text = args.text.strip()
    if not text:
        fail("Note cannot be empty.")

    data = load_json(DATA_FILE)
    task = find_task(args.task_id.strip().upper(), data)

    if not task:
        fail(f"Task not found: {args.task_id}")

    step = find_step(task, args.step_id)
    if step is None:
        fail(f"Step not found: {args.step_id}")

    stamps = now_stamps()
    note = {
        "text": text,
        "dhaka": stamps["dhaka"],
        "utc": stamps["utc"],
    }
    step.setdefault("notes", []).append(note)

    append_history(
        task,
        f"Added note to step {args.step_id}: {text}",
        stamps,
    )
    save_json(DATA_FILE, data)

    print(f"Note added to {task['task_id']} step {args.step_id}.")
    print(f"Dhaka: {stamps['dhaka']} · UTC: {stamps['utc']}")


def main():
    parser = argparse.ArgumentParser(
        description="Manage nested task steps and step-specific notes."
    )
    commands = parser.add_subparsers(dest="command", required=True)

    add = commands.add_parser("add", help="Add a top-level step or substep")
    add.add_argument("task_id")
    add.add_argument("title")
    add.add_argument(
        "--parent",
        type=int,
        help="Existing step ID; omit to add a top-level step",
    )
    add.set_defaults(func=add_step)

    note = commands.add_parser("note", help="Add a timestamped note to a step")
    note.add_argument("task_id")
    note.add_argument("step_id", type=int)
    note.add_argument("text")
    note.set_defaults(func=add_note)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()

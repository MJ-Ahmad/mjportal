আপনার বর্তমান task system-এ task ও step tracking আছে, তবে step-গুলো flat list; step-এর parent/substep ও নিজস্ব note নেই। নিচের additive পরিবর্তনে পুরোনো `data.json` format রাখা হবে—নতুন field না থাকা পুরোনো task-ও চলবে।

বর্তমান ফাইল: [`task/index.html`](https://github.com/MJ-Ahmad/mjportal/blob/main/task/index.html), [`task/run.sh`](https://github.com/MJ-Ahmad/mjportal/blob/main/task/run.sh), [`task/_lib.py`](https://github.com/MJ-Ahmad/mjportal/blob/main/task/_lib.py), [`task/validate.py`](https://github.com/MJ-Ahmad/mjportal/blob/main/task/validate.py)।

## ১. নতুন `task/manage_steps.py` তৈরি করুন

এটি substep যোগ করবে এবং নির্দিষ্ট step-এর note timestamp-সহ সংরক্ষণ করবে। পুরোনো task-এ নতুন field না থাকলেও script নিজে defaults যোগ করে নেবে।

```python name=task/manage_steps.py
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
```

## ২. `task/run.sh`-এ command যুক্ত করুন

`task/run.sh`-এর `case` block-এ `track)` অংশের পর এই দুইটি case যোগ করুন। Existing commands বদলাবেন না।

```bash name=task/run.sh
  step-add)
    shift
    "$PY" manage_steps.py add "$@"
    ;;
  step-note)
    shift
    "$PY" manage_steps.py note "$@"
    ;;
```

Help text-এর `Usage` অংশে এই command-গুলোও যোগ করুন:

```bash
  ./run.sh step-add TASK-000001 "Substep title" [--parent 2]
  ./run.sh step-note TASK-000001 2 "এই ধাপের বিশেষ নোট"
```

## ৩. নতুন step-এ nesting fields যোগ করুন

`task/_lib.py`-এর `create_steps()` function-এ প্রতিটি step object-এ নিচের দুটি field যোগ করুন। এতে এখন থেকে নতুন task-এর step সরাসরি nested step ও note সমর্থন করবে; পুরোনো task-গুলো অক্ষত থাকবে।

```python name=task/_lib.py
{
    "id": index,
    "parent_id": None,
    "title": title,
    "completed": False,
    "completed_dhaka": None,
    "completed_utc": None,
    "notes": [],
}
```

এটি `create_steps()`-এর ভেতরের বর্তমান step dictionary-টির বিকল্প। Step ID সংখ্যাভিত্তিক এবং task-এর ভেতরে unique থাকবে—এটাই পুরোনো `track` command-এর সঙ্গে backward compatibility রাখে।

## ৪. Dashboard-এ substep ও step note দেখান

`task/index.html`-এর `detailsHTML` function-এ বর্তমান `const steps = ...map(...)` block-টি নিচের recursive renderer দিয়ে বদলান। এটি `parent_id` দিয়ে nested step দেখায়; পুরোনো step-এ `parent_id` না থাকলে সেগুলো top-level হিসেবে দেখাবে।

```javascript
const stepChildren = new Map();
(task.steps || []).forEach((step) => {
  const parent = step.parent_id ?? null;
  if (!stepChildren.has(parent)) stepChildren.set(parent, []);
  stepChildren.get(parent).push(step);
});

const renderSteps = (parentId = null, depth = 0) => {
  const children = stepChildren.get(parentId) || [];
  if (!children.length) return "";

  return `<ol class="steps ${depth ? "nested-steps" : ""}">${
    children.map((step) => {
      const ownNotes = Array.isArray(step.notes) ? step.notes : [];
      const notesHTML = ownNotes.map((note) => {
        const text = typeof note === "string" ? note : note.text;
        const stamp = typeof note === "object" && note
          ? `${note.dhaka || ""}${note.utc ? ` · UTC ${note.utc}` : ""}`
          : "";

        return `
          <div class="step-note">
            <span>${esc(text || "")}</span>
            ${stamp ? `<small>${esc(stamp)}</small>` : ""}
          </div>`;
      }).join("");

      const completedTime = step.completed
        ? `${esc(t("dhaka"))} ${esc(step.completed_dhaka || "")} · UTC ${esc(step.completed_utc || "")}`
        : esc(t("pending"));

      return `
        <li class="step ${step.completed ? "ok" : ""}">
          <span class="mark">${step.completed ? "✓" : esc(step.id)}</span>
          <div class="step-content">
            <div class="step-title">${esc(step.title)}</div>
            <div class="step-time">${completedTime}</div>
            ${notesHTML}
            ${renderSteps(step.id, depth + 1)}
          </div>
        </li>`;
    }).join("")
  }</ol>`;
};

const steps = renderSteps();
```

`task/index.html`-এর `<style>`-এর শেষে responsive CSS যোগ করুন:

```css name=task/index.html
/* Nested steps and step-level notes */
.steps .nested-steps {
  margin-top: 9px;
  margin-inline-start: 18px;
}

.step-content {
  min-width: 0;
  flex: 1;
}

.step-note {
  display: grid;
  gap: 2px;
  margin-top: 7px;
  padding: 8px 10px;
  border-inline-start: 3px solid var(--gold);
  border-radius: 6px;
  background: var(--surface);
  overflow-wrap: anywhere;
}

.step-note small {
  color: var(--muted);
  font: 400 11px/1.5 var(--mono);
}

@media (max-width: 600px) {
  .wrap {
    width: min(100% - 24px, 1180px);
  }

  .masthead {
    padding: 18px 0 52px;
  }

  .masthead-row {
    align-items: flex-start;
    gap: 12px;
  }

  .masthead-tools {
    width: 100%;
    margin-left: 0;
    justify-content: flex-end;
  }

  .meta {
    display: none;
  }

  .stats {
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 8px;
    margin-top: -36px;
  }

  .stat {
    min-width: 0;
    padding: 12px;
  }

  .toolbar {
    align-items: stretch;
    gap: 9px;
  }

  .search {
    flex-basis: 100%;
  }

  .filters {
    width: 100%;
  }

  .filters button {
    min-width: 0;
    flex: 1;
    padding: 9px 5px;
  }

  .count {
    margin-inline-start: 0;
  }

  .card {
    min-width: 0;
    padding: 15px 13px;
  }

  .card-top,
  .ids,
  .stamps {
    gap: 6px;
  }

  .ids span,
  .stamps span {
    max-width: 100%;
    overflow-wrap: anywhere;
    font-size: 10px;
  }

  .step {
    gap: 8px;
    padding: 9px 8px;
  }

  .steps .nested-steps {
    margin-inline-start: 7px;
  }

  .footer {
    margin-top: 30px;
    padding: 22px 0 calc(18px + env(safe-area-inset-bottom, 0px));
  }

  .footer-grid {
    grid-template-columns: 1fr;
    gap: 16px;
  }

  .footer-grid > div:first-child {
    grid-column: auto;
  }

  .dlg-body {
    padding: 14px;
  }

  .cmd {
    min-width: 0;
  }

  .cmd code {
    min-width: 0;
    white-space: pre-wrap;
    overflow-wrap: anywhere;
  }
}
```

## ৫. Header-এর অকার্যকর “Last updated” সরান

বর্তমানে header-এর `#meta` browser-এ fetch শেষ হওয়ার সময় দেখায়; এটি task database-এর প্রকৃত `updated_at` নয়। তাই ভুল timestamp দেখানোর বদলে সরিয়ে ফেলুন।

`task/index.html`-এর masthead থেকে এই element মুছুন:

```html
<div class="meta" id="meta"></div>
```

JavaScript-এর `applyStatic()` function থেকে এই block-টিও মুছুন:

```javascript
$("#meta").textContent = state.loadedAt
  ? `${t("updated")}\n${state.loadedAt} ${t("zone")}`
  : t("loading");
```

`state.loadedAt` ও `load()`-এর client-side time assignment থাকলেও সমস্যা নেই, তবে আর UI-তে দেখানো হবে না। প্রকৃত database update timestamp না থাকায় আপাতত এটি সরানোই সঠিক।

## ৬. Footer-এর সব link সরিয়ে শুধু CLI রাখুন

`task/index.html`-এর বর্তমান `<footer class="footer"> ... </footer>` block-টি নিচের block দিয়ে বদলান। এতে Self Tracker, README, `data.json`, Registry ও Attachments links থাকবে না; শুধু CLI dialog খোলার বোতাম থাকবে।

```html name=task/index.html
<footer class="footer">
  <div class="wrap task-footer">
    <div>
      <h4 data-i18n="footBrand"></h4>
      <p data-i18n="footDesc"></p>
      <p class="footer-owner">
        <span data-i18n="footOwner"></span>
        <strong>mj-ahmad</strong>
      </p>
    </div>

    <button
      class="footer-cli"
      type="button"
      data-dialog="dlg-cli"
      data-i18n="linkCli"
    ></button>

    <div class="footer-bottom">
      <span>© 2026 Stewardship Task System</span>
      <span>Dhaka UTC+06 · ISO 8601</span>
    </div>
  </div>
</footer>
```

Footer-এর style-এ এই ছোট সংযোজন দিন:

```css name=task/index.html
.task-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 18px;
}

.task-footer .footer-bottom {
  width: 100%;
}

.footer-owner {
  margin-top: 8px;
}

.footer-cli {
  min-height: 40px;
  padding: 8px 14px;
  border: 1px solid rgba(255, 255, 255, .35);
  border-radius: 8px;
  background: transparent;
  color: #e8eef6;
  cursor: pointer;
}

.footer-cli:hover {
  border-color: var(--gold);
  color: var(--gold);
}

@media (max-width: 600px) {
  .task-footer {
    align-items: stretch;
    flex-direction: column;
  }

  .footer-cli {
    width: 100%;
  }

  .task-footer .footer-bottom {
    gap: 5px;
  }
}
```

`dlg-cli` dialog বিদ্যমান থাকলে সেটি রেখে দিন—footer-এর “CLI কমান্ড” বোতাম সেটিই খুলবে।

## ৭. Validator-এ parent-step যাচাই যোগ করুন

`task/validate.py` বা `_lib.py`-এর validation loop-এ duplicate step ID পরীক্ষা হওয়ার পর এই check যোগ করুন। Parent ID নেই এমন পুরোনো step ঠিকভাবেই গ্রহণযোগ্য।

```python name=task/validate.py
step_by_id = {step.get("id"): step for step in steps}

for step in steps:
    parent_id = step.get("parent_id")
    if parent_id is not None and parent_id not in step_by_id:
        errors.append(
            f"{tid} step {step.get('id')}: parent step {parent_id} not found"
        )
```

## ব্যবহার

```bash
# নতুন task-এর top-level steps আগের মতোই তৈরি করুন
./run.sh task "MJ-AI setup" "প্রাথমিক project structure তৈরি" \
  --steps "Scope review, Folder tree draft"

# TASK-এর মধ্যে নতুন top-level ধাপ যোগ করুন
./run.sh step-add TASK-000033 "Security checklist review"

# Step 2-এর অধীনে substep যোগ করুন
./run.sh step-add TASK-000033 "Permission policy লিখুন" --parent 2

# নির্দিষ্ট step-এ timestamp-সহ note যোগ করুন
./run.sh step-note TASK-000033 3 "প্রথমে read-only scope যাচাই করতে হবে"

# Step সম্পন্ন করতে আগের command-ই ব্যবহার করুন
./run.sh track TASK-000033 3

# ডেটা যাচাই
./run.sh validate

# Dashboard
./run.sh web
```

`step-add` চালানোর আগে task ID এবং `--parent` দিলে parent step ID সঠিক কি না নিশ্চিত করুন। Substep-গুলোও task-এর সাধারণ step হিসেবে গণনা হবে; task সম্পন্ন করার আগে সব substep-ও complete করতে হবে। পরিবর্তনের আগে `task/data.json`, `task/registry.json` ও `task/attachments/`-এর backup নিন:

```bash
mkdir -p task-backup
cp task/data.json task/registry.json task-backup/
cp -r task/attachments task-backup/
```

শেষে মোবাইল view যাচাই করতে ফোন ও desktop browser-এ `./run.sh web` খুলুন। নেটওয়ার্কের অন্য ডিভাইস থেকে দেখতে হলে কেবল নিজের trusted LAN-এ `BIND=0.0.0.0 ./run.sh web` ব্যবহার করুন; public internet-এ এই development server প্রকাশ করবেন না।

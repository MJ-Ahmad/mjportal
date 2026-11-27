# Stewardship Task System

বাংলা ও English-এ কাজ, ধাপ, সাবধাপ, note, attachment এবং activity history নথিভুক্ত করার একটি local-first task tracker।

- **Task ID:** `TASK-000001`
- **Registry ID:** `REG-000001`
- **সময়:** Dhaka ও UTC
- **ডেটা:** `data.json`
- **Dashboard:** `index.html`
- **কমান্ড চালানোর entry point:** `run.sh`

> এই project-এর dashboard static files পড়ে। এটি নিজে login, server-side authorization বা remote write API দেয় না। Sensitive task data public hosting-এ রাখবেন না।

## ফোল্ডার কাঠামো

```text
task/
├── README.md
├── index.html             Responsive task dashboard
├── run.sh                 CLI ও local web-server entry point
├── _lib.py                Data, ID, timestamp, attachment ও validation helpers
├── add_task.py            নতুন task তৈরি
├── track_task.py          ধাপ সম্পন্ন করে timestamp সংরক্ষণ
├── complete_task.py       Task complete ও archive report তৈরি
├── manage_steps.py        নতুন ধাপ, সাবধাপ ও ধাপের note যোগ
├── validate.py            Data ও registry যাচাই
├── data.json              Task records
├── registry.json          Task ও registry ID counter
├── attachments/           Task-এর সঙ্গে যুক্ত ফাইল
└── assets/
    └── logo.png           ঐচ্ছিক dashboard logo
```

`manage_steps.py` এই বর্ধিত সংস্করণের জন্য দরকার। এটি না থাকলে `step-add` ও `step-note` command কাজ করবে না। `run.sh`-এ ওই command-গুলোর case-ও থাকতে হবে—নিচের [সাবধাপ ও ধাপের নোট](#সাবধাপ-ও-ধাপের-নোট) দেখুন।

## প্রয়োজনীয়তা

- Python 3
- Bash
- আধুনিক browser
- Dashboard data পড়ার জন্য HTTP server

Python package install করার দরকার নেই; project-এর CLI Python standard library ব্যবহার করে।

## দ্রুত শুরু

Task directory-তে যান:

```bash
cd task
```

প্রথমবার structure ও data file তৈরি করুন:

```bash
chmod +x run.sh
./run.sh init
```

একটি task এবং ধাপ তৈরি করুন:

```bash
./run.sh task \
  "প্রকল্পের প্রাথমিক কাঠামো তৈরি" \
  "লক্ষ্য, কাজের ধাপ এবং যাচাইয়ের নথি গুছিয়ে তৈরি করা।" \
  --steps "Scope নির্ধারণ, Folder tree draft, Review ও backup"
```

Dashboard চালান:

```bash
./run.sh web
```

Browser-এ খুলুন:

```text
http://127.0.0.1:8000/
```

অন্য port ব্যবহার করতে:

```bash
./run.sh web 8080
```

## CLI command

| কাজ | Command |
|---|---|
| প্রথমবার data structure তৈরি | `./run.sh init` |
| নতুন task তৈরি | `./run.sh task "Heading" "Description"` |
| নতুন task-এর ধাপ যোগ | `./run.sh task "Heading" "Description" --steps "Step 1, Step 2"` |
| Task note যোগ | `./run.sh task "Heading" "Description" --add-note "Note"` |
| Attachment যোগ | `./run.sh task "Heading" "Description" --add-file path/to/file` |
| Step সম্পন্ন | `./run.sh track TASK-000001 2` |
| Top-level step যোগ | `./run.sh step-add TASK-000001 "নতুন ধাপ"` |
| Step-এর অধীনে substep যোগ | `./run.sh step-add TASK-000001 "সাবধাপ" --parent 2` |
| Step note যোগ | `./run.sh step-note TASK-000001 2 "বিশেষ নোট"` |
| Task complete ও archive | `./run.sh complete TASK-000001` |
| Data integrity যাচাই | `./run.sh validate` |
| Dashboard | `./run.sh web` |

### একাধিক note ও attachment

`--add-note` এবং `--add-file` একাধিকবার ব্যবহার করা যায়:

```bash
./run.sh task \
  "প্রকল্পের নথি প্রস্তুত" \
  "প্রয়োজনীয় নথি সংগ্রহ, যাচাই এবং সাজানো।" \
  --steps "তালিকা তৈরি, নথি সংগ্রহ, চূড়ান্ত যাচাই" \
  --add-note "প্রথমে বর্তমান নথির inventory করতে হবে" \
  --add-note "শেষে backup যাচাই করতে হবে" \
  --add-file ./brief.md \
  --add-file ./checklist.pdf
```

## সাবধাপ ও ধাপের নোট

Step ID একটি task-এর মধ্যে সংখ্যাভিত্তিক এবং unique। Substep-ও task-এর step list-এ থাকবে; তাই progress ও task completion গণনায় সেটিও অন্তর্ভুক্ত হবে।

```bash
# Task 1-এর অধীনে নতুন top-level ধাপ যোগ
./run.sh step-add TASK-000001 "Security review"

# Step 2-এর অধীনে একটি substep যোগ
./run.sh step-add TASK-000001 "Permission checklist যাচাই" --parent 2

# Step 3-এ timestamp-সহ note যোগ
./run.sh step-note TASK-000001 3 "Reviewer-এর অনুমোদনের পরে ধাপটি সম্পন্ন করব"
```

`--parent` দিলে বিদ্যমান, অসম্পন্ন parent step ID দিতে হবে। সম্পন্ন task-এ নতুন step যোগ করা যায় না। কোনো step সম্পন্ন করতে:

```bash
./run.sh track TASK-000001 3
```

Substep-এর নিজস্ব আলাদা hierarchy depth UI-তে প্রদর্শিত হয়। Step completion command আগের মতোই numeric step ID ব্যবহার করে।

### `manage_steps.py` বা command handler অনুপস্থিত হলে

এই command-গুলো ব্যবহারের আগে নিশ্চিত করুন:

1. `task/manage_steps.py` ফাইলটি আছে।
2. `task/run.sh`-এর `case` block-এ `step-add` ও `step-note` command handler আছে।
3. নতুন step তৈরির সময় step record-এ `parent_id` ও `notes` field সংরক্ষিত হয়।

যদি আপনার local copy-তে এগুলো না থাকে, command ব্যবহারের আগে সেগুলো যোগ করুন এবং তারপর `./run.sh validate` চালান।

## Task ID ও সময়

- `TASK-000001` প্রতিটি task-এর unique ID।
- `REG-000001` registry entry-এর unique ID।
- ID counter `registry.json`-এ থাকে।
- Task তৈরির সময় ও step completion time Dhaka ও UTC-তে সংরক্ষিত হয়।
- Task বা step-এর note-এ text ও timestamp রাখা হয়।
- পুরোনো step record-এ `parent_id` বা `notes` না থাকলে সেটি top-level step হিসেবে গণ্য করা উচিত।

সময় সংরক্ষণের format:

```text
Dhaka: YYYY-MM-DD HH:MM:SS.mmm
UTC:   YYYY-MM-DD HH:MM:SS.mmm
```

## বাংলা ও English

Dashboard-এর interface EN/বাংলায় বদলানো যায়; language preference browser storage-এ রাখা হয়।

Task-এর নিজস্ব লেখা স্বয়ংক্রিয়ভাবে অনুবাদ হয় না। চাইলে আলাদা language field দিন:

```bash
./run.sh task \
  "নমুনা কাজ" \
  "বাংলা বিবরণ" \
  --heading-en "Example task" \
  --heading-bn "নমুনা কাজ" \
  --description-en "An example description." \
  --description-bn "একটি নমুনা বিবরণ।"
```

## Android ও মোবাইল navigation

Root home page-এ Android-উপযোগী bottom navigation shared `assets/menu.js` script থেকে আসে। Task dashboard-এ একই bottom navigation দেখাতে `task/index.html`-এর `</body>`-এর ঠিক আগে যোগ করুন:

```html
<script src="../assets/menu.js" defer></script>
```

Task page-এ অন্য কোনো আলাদা bottom navigation থাকলে সেটি সরিয়ে shared script-টিই রাখুন; না হলে দুইটি navigation bar দেখা যেতে পারে।

Shared menu-এর item ও nesting root-এর `menu.json` থেকে আসে। Label-গুলো `en`, `bn` বা `ar` format-এ রাখা যায়। নতুন menu item যোগ বা URL বদলানোর আগে `menu.json` backup নিন।

Android ফোন থেকে local dashboard দেখতে একই trusted local network-এ computer/server ও phone যুক্ত থাকতে হবে। তারপর server machine-এর LAN IP-তে browser খুলুন:

```bash
BIND=0.0.0.0 ./run.sh web
```

যেমন:

```text
http://192.168.1.20:8000/
```

`0.0.0.0` server-কে ওই network-এর অন্য device থেকে reachable করে। এটি public internet-এ প্রকাশ করবেন না; trusted network ছাড়া ব্যবহার করবেন না।

## Dashboard-এর ব্যবহার

- Search box-এ task ID, registry ID, heading, description, task note, step title, substep title ও step note খুঁজুন।
- Filter থেকে সব, সক্রিয় বা সম্পন্ন task দেখুন।
- Task card খুললে full description, notes, nested steps, attachments, archive report ও history দেখা যায়।
- Step progress-এর হিসাবে top-level ও nested—সব step ধরা হয়।
- Task card-এর data browser-এ দেখা যায়; dashboard editing CLI দিয়ে হয়।

## Task complete ও archive

Task complete করার আগে task-টির সব step ও substep complete করুন:

```bash
./run.sh complete TASK-000001
```

কোনো incomplete step থাকলে command task complete করবে না। Complete করার পরে task status ও archive report `data.json`-এ লেখা হয়।

## Data যাচাই

```bash
./run.sh validate
```

Validator পরীক্ষা করে:

- `TASK` ও `REG` ID-এর format এবং uniqueness
- Registry counter সর্বশেষ ID-এর চেয়ে পিছিয়ে আছে কি না
- Task heading ও status
- Step ID unique কি না
- Parent step আছে কি না
- Parent cycle আছে কি না
- Completed step-এর Dhaka/UTC timestamp
- Progress count task-এর step list-এর সঙ্গে মেলে কি না
- Completed task-এর সব step সম্পন্ন কি না
- Attachment path নিরাপদ এবং ফাইল উপস্থিত কি না

Validation fail করলে error message অনুযায়ী data backup নিয়ে সংশোধন করুন। অজানা field মুছবেন না।

## Backup ও restore

কোনো update-এর আগে backup নিন:

```bash
cd task
mkdir -p ../task-backup
cp data.json registry.json ../task-backup/
cp -r attachments ../task-backup/
```

Restore করার আগে server বন্ধ করুন। তারপর backup থেকে `data.json`, `registry.json` এবং `attachments/` ফিরিয়ে আনুন। Restore শেষে:

```bash
./run.sh validate
```

Backup-এ ব্যক্তিগত বা client data থাকতে পারে; সেটি private ও access-controlled স্থানে রাখুন।

## Data ও privacy

- Dashboard static; access control নেই।
- `./run.sh web` development server—production hosting server নয়।
- GitHub Pages বা অন্য public static host-এ `data.json`/attachments publish করলে ඒවා public হতে পারে।
- Password, API token, bank information, private client data বা credentials task description/note-এ রাখবেন না।
- Phone-এ `BIND=0.0.0.0` ব্যবহার করলে local network-এর অন্য device-ও dashboard দেখতে পারে।
- Data update করার জন্য CLI ব্যবহার করুন; সরাসরি JSON edit করলে IDs, progress বা timestamps অসামঞ্জস্য হতে পারে।

## Troubleshooting

### Dashboard-এ data load হচ্ছে না

`task/` directory থেকে server চালান:

```bash
./run.sh web
```

`index.html`-কে file manager থেকে সরাসরি খুলবেন না; browser local JSON fetch করতে বাধা দিতে পারে।

### `step-add` বা `step-note` command পাওয়া যাচ্ছে না

`manage_steps.py` আছে কি না এবং `run.sh`-এ step command handler আছে কি না যাচাই করুন।

```bash
./run.sh help
```

### Task ID পাওয়া যাচ্ছে না

সঠিক `TASK-` ID ব্যবহার করুন এবং task list-এ ID আছে কি না `task/data.json` যাচাই করুন। JSON সরাসরি edit করার আগে backup নিন।

### Attachment link কাজ করছে না

ফাইলটি `task/attachments/`-এ আছে কি না যাচাই করুন, তারপর:

```bash
./run.sh validate
```

## সীমাবদ্ধতা

- এটি personal/local task registry; multi-user collaboration বা server-side permission system নয়।
- `data.json` একক local JSON data store; একাধিক concurrent writer-এর জন্য তৈরি নয়।
- Browser dashboard task data শুধু পড়ে; পরিবর্তন CLI দিয়ে করতে হয়।
- Progress percentage কেবল step completion-এর অনুপাত; কাজের বাস্তব quality বা বাহ্যিক approval-এর নিশ্চয়তা নয়।
- Local activity history tamper-proof audit system নয়।

## মালিকানা

© 2026 mj-ahmad. সর্বস্বত্ব সংরক্ষিত।

নিচের প্রাথমিক JSON সেটআপটি সাধারণ portfolio, client task এবং কাজের রেকর্ড ব্যবস্থাপনার জন্য উপযোগী। `json/files/`-এর ভিতরে যথাযথভাবে ফাইলগুলো তৈরি করুন।

```text name=directory-tree
json/files/
├── profile.json
├── clients/
│   ├── index.json
│   └── client-template.json
├── projects/
│   ├── index.json
│   └── project-template.json
├── tasks/
│   ├── index.json
│   └── task-template.json
├── services/
│   └── index.json
├── portfolio/
│   └── achievements.json
└── contacts/
    └── channels.json
```

## ১. Profile

```json name=json/files/profile.json
{
  "id": "MJ-AHMAD-001",
  "name": {
    "bn": "মোঃ জাফর আহমদ",
    "en": "Md. Jafar Ahmad"
  },
  "display_name": "MJ Ahmad",
  "professional_title": {
    "bn": "স্বনির্ভর প্রযুক্তি সহযোগী",
    "en": "Independent technology support specialist"
  },
  "location": {
    "district": "Bangladesh",
    "timezone": "Asia/Dhaka"
  },
  "status": "open-to-work",
  "availability": {
    "work_type": [
      "freelance",
      "remote",
      "local"
    ],
    "response_time": "১–২ কর্মদিবস",
    "preferred_contact": "email"
  },
  "bio": {
    "bn": "প্রযুক্তি, ডকুমেন্টেশন, স্বচ্ছ কাজের রেকর্ড এবং নিয়মিত অগ্রগতির মাধ্যমে ব্যক্তিগত ও ছোট প্রতিষ্ঠানের কাজে সহায়তা করি।",
    "en": "I help individuals and small organizations with technology, documentation, transparent work records, and regular project updates."
  },
  "skills": [
    "Documentation",
    "JSON",
    "Markdown",
    "Python",
    "Bash",
    "Git",
    "GitHub",
    "HTML",
    "CSS",
    "JavaScript",
    "Desktop setup",
    "Project organization"
  ],
  "services": [
    "documentation",
    "file-management",
    "web-setup",
    "automation",
    "github-setup",
    "client-project-management"
  ],
  "contact": {
    "email": "mjahmad2024@outlook.com",
    "github": "https://github.com/MJ-Ahmad",
    "website": "https://mj-ahmad.github.io/mjportal/"
  },
  "updated_at": "2026-11-26T00:00:00+06:00"
}
```

## ২. Client directory

```json name=json/files/clients/index.json
{
  "schema": "mj-client-directory/v1",
  "title": "ক্লায়েন্ট ডিরেক্টরি",
  "clients": [
    {
      "id": "CLT-2026-0001",
      "status": "active",
      "name": "নতুন ক্লায়েন্ট",
      "category": "technology-support",
      "start_date": "2026-11-26",
      "project_ids": [
        "PRJ-2026-0001"
      ],
      "contact": {
        "email": "",
        "phone": ""
      },
      "notes": "নাম, যোগাযোগ ও প্রকল্পের তথ্য ক্লায়েন্ট সম্মতিক্রমে যোগ করুন।",
      "updated_at": "2026-11-26T00:00:00+06:00"
    }
  ],
  "updated_at": "2026-11-26T00:00:00+06:00"
}
```

## ৩. Client template

কোনো নতুন ক্লায়েন্ট যোগ করার আগে এই ফাইলটি কপি করুন।

```json name=json/files/clients/client-template.json
{
  "schema": "mj-client/v1",
  "id": "CLT-YYYY-NNNN",
  "status": "lead",
  "name": "",
  "category": "",
  "contact": {
    "email": "",
    "phone": "",
    "address": ""
  },
  "engagement": {
    "start_date": "",
    "target_date": "",
    "contract_type": "project",
    "payment_status": "pending"
  },
  "scope": [],
  "deliverables": [],
  "project_ids": [],
  "notes": [],
  "privacy": {
    "public_profile": false,
    "sensitive_data": true,
    "consent_received": false
  },
  "created_at": "",
  "updated_at": ""
}
```

## ৪. Project list

```json name=json/files/projects/index.json
{
  "schema": "mj-project-directory/v1",
  "title": "প্রকল্প তালিকা",
  "projects": [
    {
      "id": "PRJ-2026-0001",
      "client_id": "CLT-2026-0001",
      "title": "ডকুমেন্টেশন ও ফাইল ব্যবস্থাপনা",
      "status": "planning",
      "priority": "medium",
      "start_date": "2026-11-26",
      "target_date": "",
      "progress": 10,
      "summary": "Markdown, JSON ও ফোল্ডার কাঠামোকে একটি পরিষ্কার এবং সহজে ব্যবহারের ব্যবস্থায় রূপ দেওয়া।",
      "deliverables": [
        "Folder structure",
        "Documentation",
        "JSON catalog",
        "Delivery guide"
      ],
      "tags": [
        "documentation",
        "file-management",
        "json",
        "python"
      ],
      "updated_at": "2026-11-26T00:00:00+06:00"
    }
  ],
  "updated_at": "2026-11-26T00:00:00+06:00"
}
```

## ৫. Project template

```json name=json/files/projects/project-template.json
{
  "schema": "mj-project/v1",
  "id": "PRJ-YYYY-NNNN",
  "client_id": "CLT-YYYY-NNNN",
  "title": "",
  "status": "planning",
  "priority": "medium",
  "start_date": "",
  "target_date": "",
  "progress": 0,
  "summary": "",
  "scope": [],
  "deliverables": [],
  "milestones": [
    {
      "id": "MLS-001",
      "title": "",
      "status": "pending",
      "due_date": "",
      "completed_at": ""
    }
  ],
  "tasks": [],
  "risks": [],
  "notes": [],
  "created_at": "",
  "updated_at": ""
}
```

## ৬. Task list

```json name=json/files/tasks/index.json
{
  "schema": "mj-task-directory/v1",
  "title": "কাজের তালিকা",
  "tasks": [
    {
      "id": "TSK-2026-0001",
      "project_id": "PRJ-2026-0001",
      "client_id": "CLT-2026-0001",
      "title": "ফোল্ডার কাঠামো ও নামকরণ পদ্ধতি নির্ধারণ",
      "description": "ফাইলের ধরন অনুযায়ী একরকম ও সহজ ফোল্ডার কাঠামো বানানো।",
      "status": "todo",
      "priority": "high",
      "assignee": "MJ Ahmad",
      "due_date": "2026-11-27",
      "started_at": "",
      "completed_at": "",
      "dependencies": [],
      "tags": [
        "planning",
        "documentation"
      ],
      "updated_at": "2026-11-26T00:00:00+06:00"
    }
  ],
  "updated_at": "2026-11-26T00:00:00+06:00"
}
```

## ৭. Task template

```json name=json/files/tasks/task-template.json
{
  "schema": "mj-task/v1",
  "id": "TSK-YYYY-NNNN",
  "project_id": "PRJ-YYYY-NNNN",
  "client_id": "CLT-YYYY-NNNN",
  "title": "",
  "description": "",
  "status": "todo",
  "priority": "medium",
  "assignee": "",
  "due_date": "",
  "started_at": "",
  "completed_at": "",
  "dependencies": [],
  "tags": [],
  "attachments": [],
  "comments": [],
  "created_at": "",
  "updated_at": ""
}
```

## ৮. Service catalogue

```json name=json/files/services/index.json
{
  "schema": "mj-service-catalog/v1",
  "title": "সেবা তালিকা",
  "services": [
    {
      "id": "SVC-001",
      "title": {
        "bn": "ফাইল ও ফোল্ডার ব্যবস্থাপনা",
        "en": "File and folder organization"
      },
      "description": {
        "bn": "নামকরণ, শাখা, archive ও পুনরুদ্ধারের নিয়মসহ কাঠামোগত ব্যবস্থা।",
        "en": "Clear file structure with naming, folders, archiving, and recovery rules."
      },
      "status": "available",
      "estimated_duration": "২–৫ কর্মদিবস",
      "deliverables": [
        "Folder structure",
        "Naming rules",
        "Backup procedure",
        "Handover guide"
      ],
      "starting_from": null,
      "currency": "BDT"
    },
    {
      "id": "SVC-002",
      "title": {
        "bn": "GitHub ও ডকুমেন্টেশন সেটআপ",
        "en": "GitHub and documentation setup"
      },
      "description": {
        "bn": "README, Markdown নথি, repository structure ও সহজ রক্ষণাবেক্ষণ ব্যবস্থা।",
        "en": "README, Markdown documentation, repository structure, and maintenance guidance."
      },
      "status": "available",
      "estimated_duration": "২–৭ কর্মদিবস",
      "deliverables": [
        "README",
        "Repository structure",
        "Documentation",
        "Usage instructions"
      ],
      "starting_from": null,
      "currency": "BDT"
    },
    {
      "id": "SVC-003",
      "title": {
        "bn": "ছোট Python স্বয়ংক্রিয়করণ",
        "en": "Small Python automation"
      },
      "description": {
        "bn": "পুনরাবৃত্তিমূলক কাজের জন্য ছোট ও সাবধানে লেখা স্বয়ংক্রিয় script।",
        "en": "Small scripts for repetitive and carefully controlled automation tasks."
      },
      "status": "available",
      "estimated_duration": "৩–১০ কর্মদিবস",
      "deliverables": [
        "Source code",
        "Setup instructions",
        "Test notes",
        "Handover guide"
      ],
      "starting_from": null,
      "currency": "BDT"
    },
    {
      "id": "SVC-004",
      "title": {
        "bn": "ক্লায়েন্ট প্রকল্পের অগ্রগতি হালনাগাদ",
        "en": "Client project progress updates"
      },
      "description": {
        "bn": "সময়ানুযায়ী কাজের অবস্থা, ডেলিভারেবল এবং হালনাগাদ নথিভুক্ত করা।",
        "en": "Timely records of project status, deliverables, and progress updates."
      },
      "status": "available",
      "estimated_duration": "চুক্তি অনুযায়ী",
      "deliverables": [
        "Progress report",
        "Task status",
        "Risk summary",
        "Next action"
      ],
      "starting_from": null,
      "currency": "BDT"
    }
  ],
  "updated_at": "2026-11-26T00:00:00+06:00"
}
```

## ৯. Achievement portfolio

```json name=json/files/portfolio/achievements.json
{
  "schema": "mj-achievement-record/v1",
  "title": "অর্জনের রেকর্ড",
  "achievements": [
    {
      "id": "ACH-2026-0001",
      "title": "নিজস্ব খাতা ও পোর্টাল সেটআপ",
      "category": "development",
      "status": "completed",
      "summary": "নিজের কাজ, শেখা, ডেটা ও সফটওয়্যার পোর্টাল এক স্থানে গুছিয়ে রাখা।",
      "technologies": [
        "HTML",
        "CSS",
        "JavaScript",
        "Python",
        "JSON",
        "Markdown",
        "GitHub"
      ],
      "started_at": "2026",
      "completed_at": "",
      "proof": [],
      "featured": true
    }
  ],
  "updated_at": "2026-11-26T00:00:00+06:00"
}
```

## ১০. Contact channels

গোপন পাসওয়ার্ড, টোকেন বা ব্যক্তিগত ঠিকানা এখানে রাখবেন না।

```json name=json/files/contacts/channels.json
{
  "schema": "mj-contact-channels/v1",
  "title": "যোগাযোগ মাধ্যম",
  "primary": {
    "email": "mjahmad2024@outlook.com",
    "github": "https://github.com/MJ-Ahmad",
    "website": "https://mj-ahmad.github.io/mjportal/"
  },
  "preferred_response": {
    "email": "১–২ কর্মদিবস",
    "project_update": "সপ্তাহে অন্তত একবার",
    "emergency": "নির্ধারিত চুক্তি অনুযায়ী"
  },
  "public": true,
  "updated_at": "2026-11-26T00:00:00+06:00"
}
```

## ফাইলগুলো স্বয়ংক্রিয়ভাবে তৈরি করুন

উপরের ফাইলগুলো নিজে copy না করে একটি script দিয়ে তৈরি করতে চান? `scripts/json_setup.py` সেটিকে শুধু catalog তৈরি করার কাজেই সীমাবদ্ধ রাখলে সুবিধা হবে। সব ফাইল একযোগে তৈরি করতে একটি পৃথক seed script বানানো ভালো—যাতে template আছে এবং আসল ডেটা ভুল করে overwrite না হয়।


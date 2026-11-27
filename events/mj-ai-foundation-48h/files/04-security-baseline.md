# MJ-AI Security Baseline

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

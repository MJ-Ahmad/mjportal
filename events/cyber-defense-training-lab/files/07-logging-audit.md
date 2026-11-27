# Logging & Evidence Handling

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

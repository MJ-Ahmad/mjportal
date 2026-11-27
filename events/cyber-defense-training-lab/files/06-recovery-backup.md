# Backup & Recovery Exercise

## Backup target

- configuration
- source code
- database schema and safe training data
- monitoring configuration
- detection rules
- event documentation
- audit logs
- infrastructure-as-code

## Recovery test

1. Record source checksums
2. Create isolated snapshot
3. Remove or isolate affected lab copy
4. Restore from snapshot or backup
5. Verify integrity
6. Verify service health
7. Verify logs
8. Record recovery time
9. Record unresolved loss
10. Restore safety controls

## Do not restore

- live secrets
- real customer data
- unknown malware
- unverified database dumps
- credentials outside lab boundary

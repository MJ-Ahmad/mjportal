# Detection Plan

## Recommended telemetry

- authentication logs
- endpoint process logs
- DNS or proxy logs
- firewall summaries
- application logs
- database audit logs
- file integrity monitoring
- backup verification logs
- container logs
- configuration changes

## Detection categories

- account misuse
- privilege misuse
- suspicious process behavior
- unexpected file modification
- configuration drift
- service disruption
- abnormal network communication
- unsafe package installation
- repeated login failures
- audit log gaps

## Rule lifecycle

1. Define baseline
2. Define benign test
3. Create detection
4. Validate in isolated lab
5. Review false positives
6. Approve threshold
7. Record owner
8. Schedule review

Never connect an untested destructive action directly to production.

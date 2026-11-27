# Defensive Threat Model

## Example analysis method

STRIDE:

- Spoofing
- Tampering
- Repudiation
- Information disclosure
- Denial of service
- Elevation of privilege

## Initial assets

- user accounts
- application configuration
- database
- backup snapshots
- local logs
- source code
- secrets
- network configuration
- API keys
- training datasets
- monitoring infrastructure

## Example scenarios

- unauthorized account login
- suspicious privileged action
- unexpected configuration change
- unusual outbound request
- suspicious file modification
- log deletion attempt
- repeated authentication failure
- backup integrity mismatch
- unsafe package or dependency update
- service unavailable due to misconfiguration

## Required evidence

প্রতিটি scenario-এর জন্য নথিভুক্ত করুন:

- asset
- threat
- precondition
- attack indicator
- telemetry source
- detection
- containment
- recovery
- residual risk

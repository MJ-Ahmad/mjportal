# Authorized Training Lab Boundaries

## Allowed

- isolated virtual machines
- localhost or private lab network
- synthetic identities and fake accounts
- benign test files
- defensive SIEM/EDR-style simulation
- tabletop incident exercises
- approved open-source defensive tools
- snapshot and restore testing
- log collection and analysis
- MITRE ATT&CK-like mapping for learning

## Forbidden

- unauthorized host scan
- public internet exploitation
- credential theft
- real phishing
- malware distribution
- persistence backdoor
- lateral movement outside lab
- data exfiltration
- denial-of-service against a third party
- covert monitoring
- exposing personal or sensitive data

## Rule before every drill

- [ ] Asset owner confirmed
- [ ] Lab isolation confirmed
- [ ] Test window documented
- [ ] Rollback tested
- [ ] Data sanitized
- [ ] Observers/participants identified
- [ ] Stop condition defined
- [ ] Emergency contact identified

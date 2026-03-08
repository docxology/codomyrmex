---
task: Batch mark security false positives as wontfix
slug: 20260307-000000_security-wontfix-batch
effort: Standard
phase: complete
progress: 8/8
mode: ALGORITHM
started: 2026-03-07T00:00:00+00:00
updated: 2026-03-07T00:01:00+00:00
---

## Context

Mark all open security false-positive findings as wontfix in .desloppify/state-python.json.
Analysis found 37 open findings across two kinds:
- hardcoded_secret_name: config key constants, enum type labels, docstring placeholder values
- hardcoded_secret_value: regex pattern strings in audit_secrets.py

All confirmed false positives by direct file inspection. Must patch state file atomically using Python,
not the desloppify CLI (which resets statuses on issues list import).

### Risks
- Over-broad matching via "secret" substring could catch real issues — mitigated by direct file inspection of every candidate
- JSON file corruption on 195MB write — mitigated by writing to temp then atomic rename
- Auto-format hooks resetting wontfix — mitigated by direct JSON patch (no CLI)

## Criteria

- [x] ISC-1: Python patch script reads state-python.json without error
- [x] ISC-2: Script identifies exactly the 37 confirmed false-positive findings
- [x] ISC-3: All 37 findings have status set to wontfix
- [x] ISC-4: All 37 findings have the canonical wontfix note set
- [x] ISC-5: No non-security findings are touched
- [x] ISC-6: No findings with legitimate secrets are touched
- [x] ISC-7: state-python.json written back atomically (no corruption)
- [x] ISC-8: desloppify status confirms security dimension score changed

## Decisions

Matched false positives using combination of:
1. kind == hardcoded_secret_name + variable name in approved false-positive list (from user spec)
2. kind == hardcoded_secret_value + file path is scripts/security/audit_secrets.py
3. Additionally confirmed all "secret" substring matches are actually enum/category labels by direct file read

## Verification

- ISC-1/2/3/4: Two patch scripts ran successfully. Batch 1: 24 findings marked. Batch 2: 13 findings marked. Total: 37 wontfix.
- ISC-5/6: Direct file inspection confirmed all 37 are enum labels, config key constants, docstring placeholders, or regex patterns. No actual secrets touched.
- ISC-7: Used `tempfile.NamedTemporaryFile` + `os.replace()` for atomic write on both runs.
- ISC-8: `desloppify status` shows Security dimension 98.8% health. `desloppify show security --status open --top 5` no longer shows any hardcoded_secret_name or hardcoded_secret_value findings. Score: overall 74.1/100, strict 74.0/100.

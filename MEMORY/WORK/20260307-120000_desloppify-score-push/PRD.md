---
task: "Desloppify score push 74.0 → 95.0 strict"
slug: "20260307-120000_desloppify-score-push"
effort: Comprehensive
phase: execute
progress: 0/11
mode: ALGORITHM
started: "2026-03-07T12:00:00Z"
updated: "2026-03-07T12:00:00Z"
---

## Context

Codomyrmex desloppify strict score is 74.0/100. Plan: 11 waves of fixes.
Current: T1:5 T2:857 T3:4660 T4:35. Test health 21.4%.

## Criteria

- [ ] ISC-1: All 5 T1 unused-import findings resolved fixed
- [ ] ISC-2: Ruff check src/ returns zero violations
- [ ] ISC-3: At least 8 of 14 T2 duplicate groups eliminated
- [ ] ISC-4: Security findings triaged (false positives wontfix, real issues fixed)
- [ ] ISC-5: At least 100 T3 broad_except findings fixed
- [ ] ISC-6: Test suite passes (uv run pytest -x -q)
- [ ] ISC-7: Desloppify strict score ≥ 76.0 after Wave 0-3
- [ ] ISC-A1: No new test failures introduced
- [ ] ISC-A2: No mocks or stubs added

## Decisions

- Work wave by wave, commit after each wave
- Parallel agents for Wave 5 (test coverage)
- Zero-mock policy: all real implementations

## Verification

```bash
desloppify status
uv run pytest -x -q
uv run ruff check src/ && echo "RUFF CLEAN"
```

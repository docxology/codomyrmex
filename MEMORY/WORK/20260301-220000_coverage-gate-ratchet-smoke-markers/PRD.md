---
task: "Ratchet coverage gate 68→70, add smoke markers to integration tests"
slug: "20260301-220000_coverage-gate-ratchet-smoke-markers"
effort: "Extended"
phase: "observe"
progress: "0/18"
mode: "algorithm"
started: "2026-03-01T22:00:00Z"
updated: "2026-03-01T22:00:00Z"
---

## Context

Continuing Sprint 14 work. Previous session added 169+ new tests (docs_gen: 84, release: 85) plus earlier 52 tests (dependency_resolver, mcp_tools, git_ops). Coverage gate currently at 68% in three places. Plan: run full test suite to confirm ≥70%, then ratchet all three config files. Also need to mark ~63 assertion-less integration tests with `@pytest.mark.smoke` (marker added to pytest.ini in previous session).

### Risks
- Coverage may still be below 70% (new tests added 169 new passing tests but coverage depends on LOC hit in new modules)
- Integration tests span large test files — wrong tests tagged as smoke could reduce meaningful assertion coverage
- Three config files must be updated atomically — partial update would leave system inconsistent

## Criteria

- [ ] ISC-1: Full test suite runs without collection errors
- [ ] ISC-2: Coverage percentage reported by pytest is ≥70.0%
- [ ] ISC-3: `pyproject.toml` `fail_under` changed from 68 to 70
- [ ] ISC-4: `pytest.ini` `--cov-fail-under` changed from 68 to 70
- [ ] ISC-5: `.github/workflows/ci.yml` `--cov-fail-under=68` changed to 70
- [ ] ISC-6: All three coverage gate files updated consistently (same value)
- [ ] ISC-7: `test_cross_module_workflows.py` assertion-less tests identified specifically
- [ ] ISC-8: `test_cross_module_workflows.py` assertion-less tests marked `@pytest.mark.smoke`
- [ ] ISC-9: `test_improvements.py` assertion-less tests identified specifically
- [ ] ISC-10: `test_improvements.py` assertion-less tests marked `@pytest.mark.smoke`
- [ ] ISC-11: `@pytest.mark.smoke` decorator import present in each modified test file
- [ ] ISC-12: Marked smoke tests still collected when running `-m smoke`
- [ ] ISC-13: Non-smoke tests in same files still collected when running `-m unit or integration`
- [ ] ISC-14: Full test suite passes at new 70% gate after changes
- [ ] ISC-A1: No test with actual assertions gets marked as smoke (false positive)
- [ ] ISC-A2: No coverage gate value set below 70 in any of the three files
- [ ] ISC-A3: No test file imports are broken by marker changes
- [ ] ISC-18: TO-DO.md Sprint 15 open item for coverage gate marked complete

## Decisions

## Verification

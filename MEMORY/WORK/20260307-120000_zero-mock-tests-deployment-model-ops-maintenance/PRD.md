---
task: Write zero-mock tests for deployment/model_ops/maintenance modules
slug: 20260307-120000_zero-mock-tests-deployment-model-ops-maintenance
effort: Advanced
phase: learn
progress: 24/24
mode: ALGORITHM
started: 2026-03-07T12:00:00Z
updated: 2026-03-07T12:00:00Z
---

## Context

Writing zero-mock tests for three codomyrmex modules that are near 0% coverage:
1. `src/codomyrmex/deployment/` — models.py, pure-logic deployment helpers (skip subprocess)
2. `src/codomyrmex/model_ops/` — fine_tuning models, training loop logic, non-GPU paths
3. `src/codomyrmex/maintenance/` — health_check.py, task management models

Rules: Zero mocks, @pytest.mark.skipif for external/GPU tests, test classes, real code calls.
Output files placed in tests/unit/<module>/ directories.
After writing, run ruff --fix then pytest -x -q to verify passing.
Commit with --no-verify.

### Risks
- Source modules may raise ImportError for optional heavy deps (torch, etc.)
- Maintenance module may have subprocess calls that need skipif guards
- model_ops likely has GPU-gated paths (CUDA/MPS required)
- Tests must exercise actual logic paths, not assert True
- Ruff may flag unused imports or style issues

### Plan
1. Read source files for all three modules to understand actual behavior
2. Write tests that call real functions with real inputs
3. Handle optional dependencies at module level with skipif guards
4. Run ruff fix then pytest verify
5. Commit

## Criteria

- [ ] ISC-1: deployment/models.py classes instantiate without error
- [ ] ISC-2: deployment model field defaults are correct values
- [ ] ISC-3: deployment model validation logic tested with valid inputs
- [ ] ISC-4: deployment model validation tested with invalid inputs
- [ ] ISC-5: deployment status enum values match expected set
- [ ] ISC-6: deployment helper pure-logic functions return expected types
- [ ] ISC-7: deployment test file passes ruff check with zero violations
- [ ] ISC-8: deployment test file passes pytest -x -q with all tests passing
- [ ] ISC-9: model_ops fine_tuning dataclass/model instantiation tested
- [ ] ISC-10: model_ops training config fields validated with real values
- [ ] ISC-11: model_ops non-GPU logic paths covered without skipif
- [ ] ISC-12: model_ops GPU/CUDA paths guarded with module-level skipif
- [ ] ISC-13: model_ops test file passes ruff check zero violations
- [ ] ISC-14: model_ops test file passes pytest -x -q all tests passing
- [ ] ISC-15: maintenance health_check function returns expected structure
- [ ] ISC-16: maintenance task model instantiation tested with real data
- [ ] ISC-17: maintenance task status transitions tested end-to-end
- [ ] ISC-18: maintenance health_check error paths tested explicitly
- [ ] ISC-19: maintenance test file passes ruff check zero violations
- [ ] ISC-20: maintenance test file passes pytest -x -q all tests passing
- [ ] ISC-21: git commit created with --no-verify flag
- [ ] ISC-22: all three test files exist at correct paths
- [ ] ISC-23: no assert True in any test file
- [ ] ISC-24: no unittest.mock imports in any test file

## Decisions

## Verification

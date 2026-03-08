---
task: Add zero-mock tests for cache/concurrency/formal_verification modules
slug: 20260307-000000_zero-mock-tests-cache-concurrency-fv
effort: Advanced
phase: complete
progress: 0/28
mode: ALGORITHM
started: "2026-03-07T00:00:00Z"
updated: "2026-03-07T00:00:00Z"
---

## Context

Three codomyrmex modules need new zero-mock test files at specific paths. Existing test suites in these dirs already have 740 tests; new files must add coverage of real behaviors not currently covered, targeting 40-60 tests per file. Zero-mock policy is absolute — no MagicMock, no monkeypatch. Z3 tests require `@pytest.mark.skipif` guard.

### Risks
- Z3 may not be installed in CI — all z3-dependent tests need module-level skip guard
- ResultAggregator needs TaskResult from concurrency.tasks.task_worker — different dataclass than AsyncWorkerPool's TaskResult
- File-based caches write to temp dirs — use tempfile.mkdtemp for isolation
- Existing 740 tests already cover much — new tests must be additive/non-duplicate

## Criteria

- [ ] ISC-1: test_cache_core.py file created at correct path
- [ ] ISC-2: test_concurrency_core.py file created at correct path
- [ ] ISC-3: test_formal_verification_core.py file created at correct path
- [ ] ISC-4: test_cache_core.py has 40+ test functions
- [ ] ISC-5: test_concurrency_core.py has 40+ test functions
- [ ] ISC-6: test_formal_verification_core.py has 40+ test functions
- [ ] ISC-7: No unittest.mock, MagicMock, monkeypatch in cache tests
- [ ] ISC-8: No unittest.mock, MagicMock, monkeypatch in concurrency tests
- [ ] ISC-9: No unittest.mock, MagicMock, monkeypatch in formal_verification tests
- [ ] ISC-10: CacheStats class tested with real recording methods
- [ ] ISC-11: InMemoryCache TTL expiry tested with real time.sleep
- [ ] ISC-12: InMemoryCache eviction under max_size tested
- [ ] ISC-13: CacheManager multi-backend listing tested
- [ ] ISC-14: MCP tools cache_get/cache_set/cache_delete/cache_stats tested
- [ ] ISC-15: TTLManager start/stop/register_cache tested
- [ ] ISC-16: ReadWriteLock read and write context managers tested
- [ ] ISC-17: LockManager register/get/list/stats tested
- [ ] ISC-18: LockManager acquire_all with unregistered lock raises ValueError
- [ ] ISC-19: AsyncWorkerPool submit with success tested via asyncio.run
- [ ] ISC-20: AsyncWorkerPool submit with failure tested (exception path)
- [ ] ISC-21: AsyncWorkerPool map tested with real items
- [ ] ISC-22: DeadLetterQueue add/list/replay/purge tested with real temp files
- [ ] ISC-23: ResultAggregator add/add_batch/aggregate/clear tested
- [ ] ISC-24: concurrency MCP tools pool_status/list_locks return correct shapes
- [ ] ISC-25: SolverStatus enum values tested
- [ ] ISC-26: SolverResult is_sat/is_unsat properties tested
- [ ] ISC-27: BackendNotAvailableError raised for unknown backend
- [ ] ISC-28: All three test files pass uv run pytest -q with 0 failures

## Decisions

## Verification

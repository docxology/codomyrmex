---
task: "Add zero-mock tests for search, scrape, networking modules"
slug: "20260307-000001_zero-mock-tests-search-scrape-networking"
effort: Advanced
phase: complete
progress: 32/32
mode: ALGORITHM
started: "2026-03-07T00:00:01Z"
updated: "2026-03-07T00:00:01Z"
---

## Context

Three codomyrmex modules (search, scrape, networking) are at 0% or near-0% test coverage.
The task is to write zero-mock pytest tests for each, targeting non-network logic
and skipping external calls via `@pytest.mark.skipif(not os.getenv("ALLOW_NETWORK"), reason="network")`.

Tests must follow the zero-mock policy: no MagicMock, unittest.mock, monkeypatch.setattr.
Test files go in `src/codomyrmex/tests/unit/{module}/test_{module}_core.py`.
Run ruff --fix --unsafe-fixes on each, then verify with uv run pytest -x -q.
Commit with --no-verify.

### Risks
- Source modules may have import errors or missing dependencies
- Models/dataclasses may require specific field values
- Network-dependent code paths must be accurately identified and skipped
- Ruff may flag test style patterns that need fixing

## Criteria

- [x] ISC-1: search/search_engine.py source file read and understood
- [x] ISC-2: search/models.py source file read and understood
- [x] ISC-3: scrape/extractors/scraper.py source file read and understood
- [x] ISC-4: scrape/models.py source file read and understood
- [x] ISC-5: networking/models.py source file read and understood
- [x] ISC-6: networking utils/non-network files read and understood
- [x] ISC-7: test_search_core.py created with TestSearchModels class
- [x] ISC-8: test_search_core.py includes TestSearchEngine class with real invocations
- [x] ISC-9: test_search_core.py includes TestSearchIndexing class
- [x] ISC-10: test_search_core.py includes edge case and error path tests
- [x] ISC-11: test_search_core.py has network-dependent tests guarded by skipif
- [x] ISC-12: test_scrape_core.py created with TestScrapeModels class
- [x] ISC-13: test_scrape_core.py includes TestScraper class with real invocations
- [x] ISC-14: test_scrape_core.py HTTP-dependent tests guarded by ALLOW_NETWORK skipif
- [x] ISC-15: test_scrape_core.py tests edge cases and error paths
- [x] ISC-16: test_networking_core.py created with TestNetworkingModels class
- [x] ISC-17: test_networking_core.py tests non-network logic (parsing, validation, utils)
- [x] ISC-18: test_networking_core.py network-dependent tests guarded by skipif
- [x] ISC-19: test_networking_core.py tests error paths and boundary conditions
- [x] ISC-20: ruff check --fix --unsafe-fixes run on test_search_core.py, zero violations
- [x] ISC-21: ruff check --fix --unsafe-fixes run on test_scrape_core.py, zero violations
- [x] ISC-22: ruff check --fix --unsafe-fixes run on test_networking_core.py, zero violations
- [x] ISC-23: uv run pytest test_search_core.py -x -q passes with no errors
- [x] ISC-24: uv run pytest test_scrape_core.py -x -q passes with no errors (124 pass, 1 skip)
- [x] ISC-25: uv run pytest test_networking_core.py -x -q passes with no errors
- [x] ISC-26: no assert True in any test file
- [x] ISC-27: no MagicMock/unittest.mock/monkeypatch in any test file
- [x] ISC-28: test classes use descriptive names matching AAA pattern
- [x] ISC-29: at least 8 test functions in test_search_core.py (70 found)
- [x] ISC-30: at least 8 test functions in test_scrape_core.py (125 found)
- [x] ISC-31: at least 8 test functions in test_networking_core.py (68 found)
- [x] ISC-32: git commit --no-verify created with all 3 files (29b379ff6)

## Decisions

## Verification

# tests/unit — Agent Context

## Purpose

This directory contains the unit test suite for all codomyrmex modules.
When working with tests, this is the primary location.

## Key Facts for Agents

- **417 test files** across all modules (Feb 2026)
- **10,041 tests collected**, 253 skipped (external dependencies), 0 failures
- **Zero-mock policy**: No `unittest.mock`, `MagicMock`, or `monkeypatch`. Real objects only.
- **pytest** with `importlib` import mode (allows testing without `__init__.py` in test dirs)
- Tests live here, not in module directories

## Test File Locations

```
src/codomyrmex/tests/unit/<module_name>/test_<module_name>.py
```

Examples:
- `tests/unit/orchestrator/test_core.py` — orchestrator.core.main()
- `tests/unit/agents/core/test_base.py` — agents.core.base interfaces
- `tests/unit/events/test_events.py` — events module emit/subscribe

## Quick Commands

```bash
# Run all unit tests
uv run pytest src/codomyrmex/tests/unit/ -v --no-cov

# Run a specific module's tests
uv run pytest src/codomyrmex/tests/unit/orchestrator/ -v

# Run by marker
uv run pytest -m unit --no-cov

# Check which tests would run (dry run)
uv run pytest --collect-only -q
```

## When to Skip Tests

Use `pytest.importorskip()` or `@pytest.mark.skipif` when:
- Test requires an API key not available in CI
- Test requires a running service (database, server)
- Test imports an optional SDK not in the base install

Never skip tests for core modules — use `uv sync --extra <module>` to install deps.

## Adding Tests for a New Module

1. Create directory: `src/codomyrmex/tests/unit/<module>/`
2. Create: `src/codomyrmex/tests/unit/<module>/test_<module>.py`
3. Import from the module under test: `from codomyrmex.<module> import ...`
4. Write classes with `Test` prefix, methods with `test_` prefix
5. Use real objects, `tmp_path` for filesystem, no mocks

## Anti-Patterns to Avoid

- `MagicMock`, `patch`, `monkeypatch` — zero-mock policy
- Hardcoded paths outside `tmp_path`
- Tests that depend on network without `@pytest.mark.network`
- Silent fallbacks that hide failures
- Tests that always pass regardless of behavior (assert True)

## Related Files

- `pytest.ini` — Markers, paths, coverage settings (project root)
- `src/codomyrmex/testing/` — Test fixtures and integration helpers
- `src/codomyrmex/tests/unit/orchestrator/test_core.py` — Reference example

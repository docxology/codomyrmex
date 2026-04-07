# tests/unit — Behavioral Specification

## Layout

- **`tests/unit/<module>/`** — primary home for `codomyrmex.<module>` tests.
- **`tests/unit/hermes/`** — Hermes client, session, templates, gateway, monitoring, provider router (not duplicated at `tests/unit/` root).
- **`tests/unit/agents/hermes/`** — Hermes MCP tools; **`agents/test_agents_hermes_client.py`** complements `hermes/test_hermes_client.py`.
- **Unit root** — `conftest.py`, `test_coverage_smoke.py`, milestone `test_v1_*.py` / `test_v13*_*.py`, and cross-cutting tests. No duplicate copies of module-scoped suites.

## Coverage Requirements

| Metric | Baseline | Target | Gate |
|--------|----------|--------|------|
| Line coverage | varies per run | 45%+ stretch | CI fails below **40%** floor (`pyproject.toml`) |
| Tests collected | 34,520 (April 2026; `pytest --collect-only`) | growing | `uv run pytest src/codomyrmex/tests/unit --collect-only -q` |
| Skipped | varies | minimize | — |
| Failures | 0 | 0 | Blocks merge |

## Naming Conventions

### File naming
```
test_<module_name>.py          # Primary module test
test_<module_name>_<aspect>.py # Secondary aspect (e.g., test_events_async.py)
```

### Class and function naming
```python
class TestFeatureName:         # CamelCase, Test prefix, describe the feature
    def test_behavior(self):   # snake_case, test_ prefix, describe the behavior
    def test_edge_case(self):  # Describe what edge case
    def test_error_condition(self):  # Describe the error
```

## Zero-Mock Policy (Hard Requirement)

Tests MUST NOT use:
- `unittest.mock.MagicMock`
- `unittest.mock.patch`
- `pytest-mock` (`mocker` fixture)
- `monkeypatch` for production code paths
- Any fake/stub objects returning hardcoded data

Tests MUST use:
- Real module instances with real configurations
- `tmp_path` for isolated filesystem operations
- `@pytest.mark.skipif` for tests that require unavailable services
- `pytest.importorskip()` for optional SDK dependencies

## Test Marker Requirements

Each test must be marked appropriately:

| Marker | Requirement |
|--------|-------------|
| `unit` | No external network, no real DB, no API keys |
| `integration` | Requires running service or multi-module coordination |
| `slow` | Runs in >5 seconds on reference hardware |
| `network` | Makes outbound HTTP/socket calls |
| `external` | Requires environment variable (API key, URL) |

Unmarked tests are treated as `unit` by default.

## Skip Policy

### Allowed skip patterns

```python
# Module-level SDK guard (preferred)
pytest.importorskip("heavy_sdk")

# Environment variable guard
@pytest.mark.skipif(
    not os.getenv("ANTHROPIC_API_KEY"),
    reason="Requires ANTHROPIC_API_KEY"
)

# Platform guard
@pytest.mark.skipif(sys.platform == "win32", reason="POSIX only")
```

### Prohibited skip patterns

```python
# NEVER: Unconditional skip
@pytest.mark.skip(reason="TODO")  # Delete or fix the test

# NEVER: Skip core module for missing deps — install them instead
# uv sync --extra <module>
```

## Test Independence Requirements

1. **No shared state**: Each test must work in isolation, in any order.
2. **No fixture side effects**: Fixtures must clean up after themselves.
3. **No hardcoded ports**: Use random available ports or avoid network.
4. **No hardcoded paths**: Use `tmp_path` or relative paths from fixtures.
5. **Deterministic**: Same result on every run, regardless of environment.

## Coverage Counting Rules

- Only `src/codomyrmex/` counts toward coverage (per `[tool.coverage.run]` in `pyproject.toml`)
- Tests in `src/codomyrmex/tests/` are excluded from coverage calculation
- Vendored code in `*/vendor/` is excluded
- Generated files in `__pycache__` are excluded

## CI Integration

The `ci.yml` workflow runs unit tests with:
```bash
uv run pytest src/codomyrmex/tests/unit/ ... --cov=src/codomyrmex --cov-fail-under=40
```

Coverage floor is **40%** in `[tool.coverage.report] fail_under` and mirrored on the CI command line.
All tests must pass and coverage must meet the floor when that job is configured to fail the workflow (see workflow `continue-on-error` flags).

### Baseline note (April 2026 layout refresh)

A full local `uv run pytest src/codomyrmex/tests/unit/ --cov=src/codomyrmex --cov-fail-under=40` completed coverage aggregation with **~76%** line coverage on measured `src/codomyrmex` before exit, while the same run reported **multiple failures** tied to optional services,plot backends, and provider SDK drift—**not** to file moves under `tests/unit/`. Treat **CI green** as the release gate; use module-scoped pytest locally when debugging.

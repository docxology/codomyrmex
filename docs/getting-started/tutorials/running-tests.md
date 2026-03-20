# Running the Test Suite

**Audience**: Contributors and CI systems

This tutorial covers running, filtering, and understanding the Codomyrmex test suite.

## Prerequisites

- Codomyrmex installed in development mode: `uv sync --all-extras`
- Python 3.10+

## Quick Start

```bash
# Run all tests
uv run pytest

# Quick check — collect only (no execution)
uv run pytest --collect-only -q

# Run with coverage
uv run pytest --cov=src/codomyrmex --cov-report=term-missing
```

## Test Organization

Tests live alongside source code under `src/codomyrmex/tests/`:

```text
src/codomyrmex/tests/
├── unit/           # Module-level unit tests (886+ files)
│   ├── agents/     # Tests for agents module
│   ├── security/   # Tests for security module
│   └── ...
└── integration/    # Cross-module integration tests
```

## Filtering Tests

```bash
# By module
uv run pytest src/codomyrmex/tests/unit/security/ -v

# By marker
uv run pytest -m unit        # Unit tests only
uv run pytest -m integration # Integration tests only

# By keyword
uv run pytest -k "test_audit"   # Tests matching 'audit'
uv run pytest -k "not slow"     # Skip slow tests

# Single file
uv run pytest src/codomyrmex/tests/unit/ide/test_agent_bridge.py -v
```

## Coverage

The project maintains a coverage gate at **31%** (ratcheted up over time):

```bash
# Check coverage (will fail if below gate)
uv run pytest --cov=src/codomyrmex --cov-fail-under=31

# HTML report
uv run pytest --cov=src/codomyrmex --cov-report=html
open htmlcov/index.html

# Per-file coverage for a specific module
uv run pytest src/codomyrmex/tests/unit/telemetry/ \
  --cov=src/codomyrmex/telemetry \
  --cov-report=term-missing
```

## Zero-Mock Policy

Codomyrmex enforces a **Zero-Mock** testing policy:

- ❌ No `unittest.mock`, `MagicMock`, `patch`, or `monkeypatch`
- ✅ Real objects, data factories, in-memory stores
- ✅ Environment-gated tests for external services (API keys, servers)

The policy is enforced via `ruff` — any import of mock libraries will fail linting:

```toml
# pyproject.toml
[tool.ruff.lint.flake8-tidy-imports.banned-api]
"unittest.mock" = {msg = "Zero-Mock policy: use real implementations"}
```

## Useful pytest Flags

| Flag | Purpose |
|------|---------|
| `-v` | Verbose output with test names |
| `-x` | Stop on first failure |
| `--tb=short` | Short tracebacks |
| `-q` | Quiet — summary only |
| `--lf` | Re-run only last-failed tests |
| `-n auto` | Parallel execution (requires `pytest-xdist`) |

## Key Metrics

| Metric | Value |
|--------|-------|
| Test files | 886 |
| Tests collected | 34,492 (`uv run pytest --collect-only -q --no-cov`) |
| Coverage gate | `fail_under=31` |
| Actual coverage | ~32% |

## Next Steps

- See [creating-a-module-03-test.md](creating-a-module-03-test.md) for writing tests
- See the [Zero-Mock Policy](../../../CLAUDE.md) section in CLAUDE.md

# tests/unit — Unit Test Suite

Unit tests for all codomyrmex modules. Each test file exercises one module in
isolation using real objects — no mocks, stubs, or fakes (zero-mock policy).

## Structure

```
tests/unit/
├── <module>/                # One directory per top-level module
│   └── test_<module>.py    # Primary test file for that module
├── orchestrator/
│   └── test_core.py
├── validation/
│   ├── schemas/
│   │   └── test_schemas.py  # removed — schemas module rebuilt as type registry
│   └── test_validation.py
└── ...
```

As of Feb 2026: **417 test files, 10,041 collected tests, 31% coverage**.

## Running Tests

```bash
# All tests
uv run pytest

# Specific module
uv run pytest src/codomyrmex/tests/unit/<module>/ -v

# Pattern match
uv run pytest -k "test_name_pattern"

# By marker
uv run pytest -m unit
uv run pytest -m "unit and not slow"

# Skip coverage (faster for dev)
uv run pytest --no-cov -v

# Single file
uv run pytest src/codomyrmex/tests/unit/orchestrator/test_core.py -v
```

## Test Markers

Defined in `pytest.ini`. Use `@pytest.mark.<marker>` on test classes or functions:

| Marker | When to use |
|--------|-------------|
| `unit` | Pure unit tests (default) |
| `integration` | Tests that connect multiple modules |
| `slow` | Tests that take >5 seconds |
| `performance` | Benchmarks and timing tests |
| `network` | Tests requiring network access |
| `database` | Tests requiring database connection |
| `external` | Tests requiring external services (API keys) |
| `security` | Security-focused tests |
| `asyncio` | Async tests (auto-detected via asyncio_mode=auto) |
| `crypto` | Cryptography tests |
| `orchestrator` | Orchestrator/workflow tests |

## Zero-Mock Policy

**This codebase never uses mocks.** Tests must use real objects or skip:

```python
# WRONG — never do this
from unittest.mock import MagicMock
mock_logger = MagicMock()

# CORRECT — use real objects or skip with guard
import pytest
@pytest.mark.skipif(
    not os.getenv("DATABASE_URL"),
    reason="Requires DATABASE_URL environment variable"
)
def test_with_database():
    db = RealDatabase(os.getenv("DATABASE_URL"))
    ...
```

## Skip Policy

Use `@pytest.mark.skipif` at **module level** (not per-test) for external dependencies:

```python
import pytest
import importlib.util

# Module-level guard — if SDK not installed, skip all tests in file
pytest.importorskip("some_sdk", reason="Requires optional SDK: uv sync --extra sdk")

class TestModule:
    def test_feature(self):
        ...
```

## Adding New Tests

1. Create `src/codomyrmex/tests/unit/<module>/test_<module>.py`
2. Follow the naming pattern: `class Test<Feature>:`, `def test_<behavior>(self):`
3. Use `tmp_path` pytest fixture for filesystem isolation
4. Mark with appropriate markers
5. No mocks — if you can't test without mocking, the code needs refactoring

## Coverage

Current baseline: **31%** (Feb 2026). Target: **35%**.

Run coverage report:
```bash
uv run pytest --cov=src/codomyrmex --cov-report=term-missing
```

The `htmlcov/` directory contains the visual coverage report after a test run.

# Tests

**Version**: v1.0.5 | **Status**: Active | **Last Updated**: March 2026

Comprehensive test suite for the Codomyrmex ecosystem.

## PAI Integration

| Algorithm Phase | Role | Tools Used |
|----------------|------|-----------|
| **VERIFY** | Execute full test suite and validate coverage gate | Direct Python import |
| **OBSERVE** | Monitor test health and analyze results by marker | Direct Python import |
| **BUILD** | Maintain test infrastructure and shared fixtures | Direct Python import |

PAI agents access this module via direct Python import through the MCP bridge for test suite execution and coverage validation.

## Directory Structure

```
tests/
├── unit/            # Isolated unit tests per module
├── integration/     # Cross-module integration tests
├── performance/     # Benchmarking and performance tests
├── examples/        # Example validation tests
├── visualization/   # Visualization output tests
├── fixtures/        # Shared test fixtures and data
├── conftest.py      # Shared pytest fixtures and configuration
└── RUNNING_TESTS.md # Detailed test execution guide
```

## Running Tests

```bash
# Run all tests
uv run pytest

# Run unit tests only
uv run pytest src/codomyrmex/tests/unit/

# Run integration tests only
uv run pytest src/codomyrmex/tests/integration/

# Run tests for a specific module
uv run pytest src/codomyrmex/tests/unit/<module>/

# Run tests matching a name pattern
uv run pytest -k "test_name_pattern"

# Run by marker
uv run pytest -m unit
uv run pytest -m integration
uv run pytest -m "not slow"
```

## Coverage

```bash
# Run with coverage (default via pytest.ini addopts)
uv run pytest

# Generate HTML coverage report
uv run pytest --cov-report=html:htmlcov

# View coverage summary in terminal
uv run pytest --cov-report=term-missing
```

Coverage reports are written to `htmlcov/` (HTML) and `coverage.json` (JSON).

## Test Markers

Markers are defined in `pytest.ini` at the project root:

| Marker | Description |
|--------|-------------|
| `unit` | Unit tests |
| `integration` | Integration tests |
| `slow` | Slow running tests |
| `performance` | Performance and benchmarking tests |
| `examples` | Example validation tests |
| `network` | Tests requiring network access |
| `database` | Tests requiring database access |
| `external` | Tests requiring external services |
| `security` | Security-related tests |
| `asyncio` | Asynchronous tests |
| `crypto` | Cryptography tests |
| `orchestrator` | Orchestrator and workflow tests |

## Naming Conventions

- Test files: `test_<module>.py`
- Test classes: `Test<Feature>`
- Test functions: `test_<behavior>`
- Fixtures: descriptive names in `conftest.py` or module-level `conftest.py`

## Navigation

- [RUNNING_TESTS.md](RUNNING_TESTS.md) — Detailed execution guide
- [AGENTS.md](AGENTS.md) | [SPEC.md](SPEC.md) | [PAI.md](PAI.md)

# Running Codomyrmex Tests

**Version**: v1.2.7 | **Status**: Active | **Last Updated**: March 2026

**Canonical copy:** [src/codomyrmex/tests/RUNNING_TESTS.md](../../../src/codomyrmex/tests/RUNNING_TESTS.md) — keep this module doc in sync when changing commands or counts.

## Overview

This document describes how to run and filter the Codomyrmex test suite. Canonical counts and inventory live in [docs/reference/inventory.md](../../reference/inventory.md).

**Collected tests (repo-wide):** **34,593** — `uv run pytest --collect-only -q --no-cov` from the repository root after `uv sync --all-extras --dev` (`testpaths` = `src/codomyrmex` per `pyproject.toml`). Count varies with optional extras and discovery paths.

### Zero-Mock Policy

**CRITICAL**: This project adheres to a strict **Zero-Mock Policy**.

- All tests must verify real functional behavior.
- Use of `unittest.mock`, `pytest-mock`, or similar libraries is **forbidden** for core logic.
- External services may be substituted with strictly typed, functional fakes only when absolutely necessary (e.g. avoiding real credit card charges), but prefer real local instances (e.g. local DBs) whenever possible.

## Test Organization

### Test Categories

| Category | Location | Count (indicative) | Notes |
|----------|----------|--------------------|--------|
| **All collected** | under `src/codomyrmex/` (`tests/` + `tests/**`) | **34,593** | Single source of truth: `pytest --collect-only` (with CI-parity extras) |
| **`unit` marker** | mostly `tests/unit/**` | **21,024** | `pytest -m unit --collect-only` |
| **`integration` marker** | mixed | **253** | `pytest -m integration --collect-only` |
| **Integration tree** | `tests/integration/` | **339** | `pytest tests/integration/ --collect-only` |
| **Example tests** | `tests/unit/examples/` | **24** | Example validation lives under unit tree |
| **Performance tree** | `tests/performance/` | **59** | Benchmark-style jobs |
| **Unit test files** | `tests/unit/**/test_*.py` | **1,117+** | `find` count; changes as tests are added |

Full-suite wall time varies widely (often **tens of minutes**); use markers, `-k`, scoped directories, or `make test-unit` / `make test-integration` for tighter loops.

### Test Markers

Tests are marked with pytest markers for selective execution:

- `@pytest.mark.unit` - Unit tests
- `@pytest.mark.integration` - Integration tests
- `@pytest.mark.slow` - Slow-running tests
- `@pytest.mark.performance` - Performance tests
- `@pytest.mark.examples` - Example validation tests
- `@pytest.mark.network` - Tests requiring network access
- `@pytest.mark.database` - Tests requiring database access
- `@pytest.mark.external` - Tests requiring external services

## Quick Start

### Prerequisites

Ensure you have the development environment set up:

```bash
# Install dependencies (use --all-extras --dev to mirror CI and optional stacks like FPF / scientific)
uv sync --dev
# CI parity (recommended before a full-suite gate):
uv sync --all-extras --dev

# Verify pytest installation
uv run pytest --version
```

### Run All Tests (coverage gate)

There is **no** in-repository batch shell runner. Use **`make`** targets or explicit **`uv run pytest`** (markers, directories, or `-k`).

```bash
# Full suite + 40% coverage floor + term/html/json reports
make test

# Lint, type-check, then full test target (release-style gate)
make verify-release

# Unit tests only (marker `unit`, coverage gate)
make test-unit

# Integration tree
make test-integration

# Quiet run aligned with CI coverage-gate (see .github/workflows/ci.yml)
uv run pytest src/codomyrmex/tests/ -q --tb=short \
  --cov=src/codomyrmex \
  --cov-report=term-missing \
  --cov-report=json:coverage-gate.json \
  --cov-fail-under=40
```

### Scoped runs (by tree or marker)

```bash
# Unit tests only (fastest)
uv run pytest src/codomyrmex/tests/unit/ -m "not slow"

# Integration tests
uv run pytest src/codomyrmex/tests/integration/

# Example validation
uv run pytest src/codomyrmex/tests/examples/

# Performance tests (slow)
uv run pytest src/codomyrmex/tests/performance/
```

## Detailed Test Execution

### Test Collection

Verify all tests can be collected without errors:

```bash
# Check test collection
uv run pytest --collect-only

# Check specific directory
uv run pytest src/codomyrmex/tests/unit/ --collect-only
```

### Coverage Reports

Default `uv run pytest` does **not** enable coverage (see `pyproject.toml` `[tool.pytest.ini_options]`). Use `make test`, `make test-coverage`, or explicit `--cov` flags. The documented floor is **40%** (`[tool.coverage.report] fail_under`); enforce it with `--cov-fail-under=40` when running pytest with `--cov`. The experimental `meme` package is omitted from coverage measurement (`[tool.coverage.run] omit`).

**Hypothesis / NumPy / `secrets`:** If you see `ImportError: cannot import name randbits` from `numpy.random`, check for a **test directory named `secrets`** under a path that appears on `sys.path` before the stdlib (the suite uses `secrets_tests/` under `tests/unit/security/` to avoid shadowing). `security/secrets/vault.py` must not repoint `sys.modules["secrets"]`. The `Makefile` and CI also set `HYPOTHESIS_NO_NPY=1` for the process.

Generate coverage reports:

```bash
# Run with coverage + gate
uv run pytest --cov=src/codomyrmex --cov-fail-under=40 --cov-report=html --cov-report=term-missing

# View HTML report
open htmlcov/index.html
```

### Verbose Output

For detailed test output:

```bash
# Verbose mode
uv run pytest -v src/codomyrmex/tests/unit/

# Very verbose (shows all output)
uv run pytest -vv src/codomyrmex/tests/unit/test_exceptions.py
```

### Selective Test Execution

Run specific tests:

```bash
# Run specific test file
uv run pytest src/codomyrmex/tests/unit/test_exceptions.py

# Run specific test class
uv run pytest src/codomyrmex/tests/unit/test_exceptions.py::TestCodomyrmexError

# Run specific test method
uv run pytest src/codomyrmex/tests/unit/test_exceptions.py::TestCodomyrmexError::test_basic_error_creation

# Run tests by marker
uv run pytest -m "unit and not slow"

# Run tests by keyword
uv run pytest -k "exception"
```

### Debugging Failed Tests

Debug failing tests:

```bash
# Stop on first failure
uv run pytest -x src/codomyrmex/tests/unit/

# Show full traceback
uv run pytest --tb=long src/codomyrmex/tests/unit/test_exceptions.py

# Debug with PDB
uv run pytest --pdb src/codomyrmex/tests/unit/test_exceptions.py::TestCodomyrmexError::test_basic_error_creation
```

## Split runs and pytest options

Use **`make test`**, **`make test-unit`**, **`make test-integration`**, or directory/marker-scoped **`uv run pytest`** when you want a smaller loop than the full suite.

Common flags on any command:

| Flag | Use |
|------|-----|
| `-x` / `--maxfail=1` | Stop on first failure |
| `--timeout=N` | Per-test timeout (requires `pytest-timeout` if configured) |
| `--durations=20` | Print slowest tests |
| `-vv` | Very verbose |

Typical order when running pieces by hand: **unit** → **integration** → **examples** → **performance** (slowest last).

## CI/CD Integration

### GitHub Actions

CI invokes **`uv run pytest`** on `src/codomyrmex/tests/` with coverage in the **`coverage-gate`** job, and splits **unit** vs **integration** paths in the test matrix. There is no batch shell script in this repository — see [`.github/workflows/ci.yml`](../../../.github/workflows/ci.yml).

### Parallel matrix (CI)

The workflow runs **unit** and **integration** steps per OS/Python combination. Locally, mirror that with `make test-unit` and `make test-integration`, or run `pytest` on each directory as needed.

## Troubleshooting

### Common Issues

#### Memory Errors

If tests run out of memory:

```bash
# Run smaller scopes (Makefile or explicit paths)
make test-unit
make test-integration

# Or run with limited parallelism (pytest-xdist)
uv run pytest -n 2 src/codomyrmex/tests/unit/
```

#### Hanging Tests

Tests that hang can be identified and fixed:

```bash
# Run with timeout to identify hanging tests
uv run pytest --timeout=60 src/codomyrmex/tests/unit/

# Debug specific slow test
uv run pytest --durations=10 src/codomyrmex/tests/unit/
```

#### Import Errors

If you encounter import errors:

```bash
# Check Python path
python -c "import sys; print('
'.join(sys.path))"

# Verify package installation
uv run python -c "import codomyrmex; print('Package imported successfully')"

# Check for syntax errors
# Check for syntax errors
find src/ -name "*.py" -exec uv run python -m py_compile {} \;
```

#### Network/External Dependencies

Tests requiring external services may fail in isolated environments:

```bash
# Skip network tests
uv run pytest -m "not network" src/codomyrmex/tests/unit/

# Run only local tests
uv run pytest -m "not external and not network" src/codomyrmex/tests/
```

### Test Performance

#### Identifying Slow Tests

```bash
# Show slowest tests
uv run pytest --durations=20 src/codomyrmex/tests/

# Profile test execution
uv run pytest --profile src/codomyrmex/tests/unit/
```

#### Optimizing Test Runs

```bash
# Run tests in parallel (if available)
uv run pytest -n auto src/codomyrmex/tests/unit/

# Use pytest-xdist for distributed execution
# Note: Ensure pytest-xdist is in your project dependencies (uv sync)
uv run pytest -n 4 src/codomyrmex/tests/unit/
```

## Test Development

### Adding New Tests

When adding tests:

1. **Follow naming conventions**: `test_*.py`, `Test*` classes, `test_*` methods
2. **Add appropriate markers**: Use `@pytest.mark.unit`, `@pytest.mark.integration`, etc.
3. **Include documentation**: Docstrings for test classes and methods
4. **Handle dependencies**: Use fixtures for setup/teardown
5. **Test edge cases**: Include both positive and negative test cases

### Test Fixtures

Common fixtures are available in `src/codomyrmex/tests/conftest.py`:

```python
def project_root():
    """Get project root directory."""

def temp_output_dir():
    """Create temporary output directory."""

def mock_config():
    """Create mock configuration for testing."""
```

### Test Markers

Apply markers appropriately:

```python
import pytest

@pytest.mark.unit
def test_fast_unit_test():
    """Fast unit test."""
    pass

@pytest.mark.integration
@pytest.mark.slow
def test_integration_workflow():
    """Slow integration test."""
    pass

@pytest.mark.performance
def test_performance_benchmark():
    """Performance benchmark."""
    pass
```

## Test Reports

### Coverage Reports

Coverage reports are generated automatically:

```bash
# HTML report
open src/codomyrmex/tests/htmlcov/index.html

# Terminal summary
uv run pytest --cov=src/codomyrmex --cov-report=term-missing

# JSON report for CI
uv run pytest --cov=src/codomyrmex --cov-report=json
```

### Test Summary Script

Use the test summary script for detailed analysis:

```bash
# Generate test summary
uv run python scripts/src/codomyrmex/tests/test_summary.py

# Analyze test durations
uv run python scripts/src/codomyrmex/tests/test_summary.py --durations

# Identify flaky tests
uv run python scripts/src/codomyrmex/tests/test_summary.py --flaky
```

## Best Practices

### Test Execution

1. **Run tests locally** before committing
2. **Use an appropriate scope** for your changes (`make test-unit` for small fixes, integration tree or `make test` for broader changes)
3. **Check coverage** to ensure adequate test coverage
4. **Review failures** carefully - they may indicate real issues

### Development Strategy

1. **Write tests first** (TDD approach)
2. **Keep tests fast** and isolated
3. **Use descriptive names** for tests and assertions
4. **Test error conditions** and edge cases
5. **Maintain test documentation**

### CI/CD Best Practices

1. **Use the same `uv run pytest` paths and coverage flags** as `.github/workflows/ci.yml`
2. **Set appropriate timeouts** to prevent hanging
3. **Generate coverage reports** for quality tracking
4. **Fail fast** in development, comprehensive in releases

## Support

### Getting Help

- Check this document first
- Review test error messages carefully
- Use `--pdb` for debugging failed tests
- Check the [Testing Guide](../../../docs/development/testing-strategy.md) for detailed testing strategy

### Contributing

When contributing tests:

1. Ensure tests pass locally
2. Add appropriate markers and documentation
3. Update this document if adding new test categories
4. Follow the existing test structure and patterns

---

## Quick Reference

```bash
# Quick validation (unit marker + coverage gate)
make test-unit

# Full test suite + 40% gate
make test

# Debug failing test
uv run pytest -vv --pdb src/codomyrmex/tests/unit/test_specific.py::TestClass::test_method

# Check coverage (40% gate when using --cov-fail-under)
uv run pytest --cov=src/codomyrmex --cov-fail-under=40 --cov-report=html

# Find slow tests
uv run pytest --durations=10 src/codomyrmex/tests/
```

## Navigation Links

- **Parent**: [Project Overview](../README.md)
- **Module Index**: [All Agents](../../AGENTS.md)
- **Documentation**: [Reference Guides](../../../docs/README.md)
- **Home**: [Root README](../../../README.md)

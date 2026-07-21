# Running Codomyrmex Tests

**Version**: v1.3.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

This document describes how to run and filter the Codomyrmex test suite. Canonical counts and inventory live in [docs/reference/inventory.md](../docs/reference/inventory.md).

**Collected tests (repo-wide):** **35,375** — `uv run python scripts/doc_inventory.py --pytest` from the repository root after `uv sync --all-extras --dev`. Count varies with optional extras and discovery paths.

### Zero-Mock Policy

**CRITICAL**: This project adheres to a strict **Zero-Mock Policy**.

- All tests must verify real functional behavior.
- Use of `unittest.mock`, `pytest-mock`, or similar libraries is **forbidden** for core logic.
- External services may be substituted with strictly typed, functional fakes only when absolutely necessary (e.g. avoiding real credit card charges), but prefer real local instances (e.g. local DBs) whenever possible.

## Test Organization

### Test Categories

| Category | Location | Count (indicative) | Notes |
|----------|----------|--------------------|--------|
| **All collected** | under `tests/` | **35,375** | Single source of truth: `uv run python scripts/doc_inventory.py --pytest` |
| **`unit` marker** | mostly `tests/unit/**` | **21,024** | `pytest -m unit --collect-only` |
| **`integration` marker** | mixed | **253** | `pytest -m integration --collect-only` |
| **Integration tree** | `tests/integration/` | **339** | `pytest tests/integration/ --collect-only` |
| **Example tests** | `tests/unit/examples/` | **24** | Example validation lives under unit tree |
| **Performance tree** | `tests/performance/` | **59** | Benchmark-style jobs |
| **Unit test files** | `tests/unit/**/test_*.py` | **1,156** | `find` count; changes as tests are added |

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
# Full suite + 60% coverage floor + term/html/json reports
make test

# Lint, type-check, then full test target (release-style gate)
make verify-release

# Unit tests only (marker `unit`, coverage gate)
make test-unit

# Integration tree
make test-integration

# Quiet run aligned with CI coverage-gate (see .github/workflows/ci.yml)
uv run pytest tests/ -q --tb=short \
  --cov=src/codomyrmex \
  --cov-report=term-missing \
  --cov-report=json:coverage-gate.json \
  --cov-fail-under=60
```

### Scoped runs (by tree or marker)

```bash
# Unit tests only (fastest)
uv run pytest tests/unit/ -m "not slow"

# Integration tests
uv run pytest tests/integration/

# Example validation
uv run pytest tests/examples/

# Performance tests (slow)
uv run pytest tests/performance/
```

## Detailed Test Execution

### Test Collection

Verify all tests can be collected without errors:

```bash
# Check test collection
uv run pytest --collect-only

# Check specific directory
uv run pytest tests/unit/ --collect-only
```

### Coverage Reports

Default `uv run pytest` does **not** enable coverage (see `pyproject.toml` `[tool.pytest.ini_options]`). Use `make test`, `make test-coverage`, or explicit `--cov` flags. The documented floor is **60%** (`[tool.coverage.report] fail_under`); enforce it with `--cov-fail-under=60` when running pytest with `--cov`. The experimental `meme` package is omitted from coverage measurement (`[tool.coverage.run] omit`); all other `src/codomyrmex/` code counts toward the gate.

**Hypothesis / NumPy / `secrets`:** If you see `ImportError: cannot import name randbits` from `numpy.random`, check for a **test directory named `secrets`** under a path that appears on `sys.path` before the stdlib (the suite uses `secrets_tests/` under `tests/unit/security/` to avoid shadowing). `security/secrets/vault.py` must not repoint `sys.modules["secrets"]`. The `Makefile` and CI also set `HYPOTHESIS_NO_NPY=1` for the process.

Generate coverage reports:

```bash
# Run with coverage + gate
uv run pytest --cov=src/codomyrmex --cov-fail-under=60 --cov-report=html --cov-report=term-missing

# View HTML report
open htmlcov/index.html
```

### Verbose Output

For detailed test output:

```bash
# Verbose mode
uv run pytest -v tests/unit/

# Very verbose (shows all output)
uv run pytest -vv tests/unit/test_exceptions.py
```

### Selective Test Execution

Run specific tests:

```bash
# Run specific test file
uv run pytest tests/unit/test_exceptions.py

# Run specific test class
uv run pytest tests/unit/test_exceptions.py::TestCodomyrmexError

# Run specific test method
uv run pytest tests/unit/test_exceptions.py::TestCodomyrmexError::test_basic_error_creation

# Run tests by marker
uv run pytest -m "unit and not slow"

# Run tests by keyword
uv run pytest -k "exception"
```

### Debugging Failed Tests

Debug failing tests:

```bash
# Stop on first failure
uv run pytest -x tests/unit/

# Show full traceback
uv run pytest --tb=long tests/unit/test_exceptions.py

# Debug with PDB
uv run pytest --pdb tests/unit/test_exceptions.py::TestCodomyrmexError::test_basic_error_creation
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

CI invokes **`uv run pytest`** on `tests/` with coverage in the **`coverage-gate`** job, and splits **unit** vs **integration** paths in the test matrix. There is no batch shell script in this repository — see [`.github/workflows/ci.yml`](../.github/workflows/ci.yml).

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
uv run pytest -n 2 tests/unit/
```

#### Hanging Tests

Tests that hang can be identified and fixed:

```bash
# Run with timeout to identify hanging tests
uv run pytest --timeout=60 tests/unit/

# Debug specific slow test
uv run pytest --durations=10 tests/unit/
```

#### Import Errors

If you encounter import errors:

```bash
# Check Python path
uv run python -c "import sys; print('\\n'.join(sys.path))"

# Verify package installation
uv run python -c "import codomyrmex; print('Package imported successfully')"

# Compile-check Python sources (sample)
find src -name "*.py" -print0 | xargs -0 -n 50 uv run python -m py_compile
```

#### Network/External Dependencies

Tests requiring external services may fail in isolated environments:

```bash
# Skip network tests
uv run pytest -m "not network" tests/unit/

# Run only local tests
uv run pytest -m "not external and not network" tests/
```

### Test Performance

#### Identifying Slow Tests

```bash
# Show slowest tests
uv run pytest --durations=20 tests/

# Profile test execution
uv run pytest --profile tests/unit/
```

#### Optimizing Test Runs

```bash
# Run tests in parallel (if available)
uv run pytest -n auto tests/unit/

# Use pytest-xdist for distributed execution
# Note: Ensure pytest-xdist is in your project dependencies (uv sync)
uv run pytest -n 4 tests/unit/
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

Shared fixtures live in `tests/conftest.py` (e.g. `project_root`, `code_dir`, `temp_env_file`, `sample_markdown_file`, `sample_json_file`, `sample_yaml_file`). Prefer real data and temp paths; do not use `unittest.mock` for core assertions (see Zero-Mock Policy above).

### Test Markers

Apply markers appropriately: decorate tests with `@pytest.mark.unit`, `@pytest.mark.integration`, `@pytest.mark.slow`, or `@pytest.mark.performance`. Each test body must exercise real code paths with concrete assertions (Zero-Mock Policy — no placeholder `assert True` or empty bodies in committed tests).

## Test Reports

### Coverage Reports

Coverage reports are generated automatically:

```bash
# HTML report
open tests/htmlcov/index.html

# Terminal summary
uv run pytest --cov=src/codomyrmex --cov-report=term-missing

# JSON report for CI
uv run pytest --cov=src/codomyrmex --cov-report=json
```

### Test Summary Script

Use the test summary script for detailed analysis:

```bash
# Generate test summary
uv run python scripts/tests/test_summary.py

# Analyze test durations
uv run python scripts/tests/test_summary.py --durations

# Identify flaky tests
uv run python scripts/tests/test_summary.py --flaky
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
- Check the [Testing Guide](../docs/development/testing-strategy.md) for detailed testing strategy

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

# Full test suite + 60% gate
make test

# Debug failing test
uv run pytest -vv --pdb tests/unit/test_specific.py::TestClass::test_method

# Check coverage (60% gate when using --cov-fail-under)
uv run pytest --cov=src/codomyrmex --cov-fail-under=60 --cov-report=html

# Find slow tests
uv run pytest --durations=10 tests/
```

## Navigation Links

- **Parent**: [Project Overview](../README.md)
- **Module Index**: [All Agents](../AGENTS.md)
- **Documentation**: [Reference Guides](../docs/README.md)
- **Home**: [Root README](../README.md)

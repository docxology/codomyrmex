# Running Codomyrmex Tests

**Version**: v1.2.7 | **Status**: Active | **Last Updated**: March 2026

## Overview

This document describes how to run and filter the Codomyrmex test suite. Canonical counts and inventory live in [docs/reference/inventory.md](../../../docs/reference/inventory.md).

**Collected tests (repo-wide):** **34,320** — `uv run pytest --collect-only -q --no-cov` from the repository root (`testpaths` = `src/codomyrmex` per `pyproject.toml`).

### Zero-Mock Policy

**CRITICAL**: This project adheres to a strict **Zero-Mock Policy**.

- All tests must verify real functional behavior.
- Use of `unittest.mock`, `pytest-mock`, or similar libraries is **forbidden** for core logic.
- External services may be substituted with strictly typed, functional fakes only when absolutely necessary (e.g. avoiding real credit card charges), but prefer real local instances (e.g. local DBs) whenever possible.

## Test Organization

### Test Categories

| Category | Location | Count (indicative) | Notes |
|----------|----------|--------------------|--------|
| **All collected** | under `src/codomyrmex/` (`tests/` + `tests/**`) | **34,320** | Single source of truth: `pytest --collect-only` |
| **`unit` marker** | mostly `tests/unit/**` | **20,488** | `pytest -m unit --collect-only` |
| **`integration` marker** | mixed | **241** | `pytest -m integration --collect-only` |
| **Integration tree** | `tests/integration/` | **339** | `pytest tests/integration/ --collect-only` |
| **Example tests** | `tests/unit/examples/` | **24** | Example validation lives under unit tree |
| **Performance tree** | `tests/performance/` | **59** | Benchmark-style jobs |
| **Unit test files** | `tests/unit/**/test_*.py` | **1,117+** | `find` count; changes as tests are added |

Full-suite wall time varies widely (often **tens of minutes**); use markers, `-k`, or the batch script for tighter loops.

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
# Install dependencies
uv sync --dev

# Verify pytest installation
uv run pytest --version
```

### Run All Tests (Recommended: Use Batches)

For the complete test suite, use the batch runner:

```bash
# Run complete test suite in batches
./scripts/src/codomyrmex/tests/run_tests_batched.sh all

# Run quick test suite (unit + examples)
./scripts/src/codomyrmex/tests/run_tests_batched.sh quick

# Run specific batch
./scripts/src/codomyrmex/tests/run_tests_batched.sh unit
./scripts/src/codomyrmex/tests/run_tests_batched.sh integration
./scripts/src/codomyrmex/tests/run_tests_batched.sh examples
./scripts/src/codomyrmex/tests/run_tests_batched.sh performance
```

### Manual Test Execution

If you prefer manual control:

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

Default `uv run pytest` does **not** enable coverage (see `pyproject.toml` `[tool.pytest.ini_options]`). Use `make test`, `make test-coverage`, or explicit `--cov` flags. The documented floor is **40%** (`[tool.coverage.report] fail_under`); enforce it with `--cov-fail-under=40` when running pytest with `--cov`. The experimental `meme` package is omitted from coverage measurement (`[tool.coverage.run] omit`); all other `src/codomyrmex/` code counts toward the gate.

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

## Batch Test Execution

### Using the Batch Script

The batch script provides intelligent test execution:

```bash
# Complete test suite
./scripts/src/codomyrmex/tests/run_tests_batched.sh all --coverage --verbose

# Quick validation
./scripts/src/codomyrmex/tests/run_tests_batched.sh quick --fail-fast

# Custom timeout
./scripts/src/codomyrmex/tests/run_tests_batched.sh unit --timeout=600
```

### Batch Script Options

| Option | Description | Default |
|--------|-------------|---------|
| `--coverage` | Generate coverage reports | No |
| `--verbose` | Verbose pytest output | No |
| `--fail-fast` | Stop on first failure | No |
| `--timeout=N` | Test timeout in seconds | 300 |

### Batch Execution Strategy

The batch script executes tests in optimal order:

1. **Unit Tests** - Fast, isolated tests
2. **Integration Tests** - Cross-module validation
3. **Example Tests** - Practical validation
4. **Performance Tests** - Slow benchmarks (last)

## CI/CD Integration

### GitHub Actions

For CI/CD pipelines, use the batch script:

```yaml
- name: Run Tests
  run: |
    ./scripts/src/codomyrmex/tests/run_tests_batched.sh all --coverage

- name: Upload Coverage
  uses: codecov/codecov-action@v3
  with:
    file: ./coverage.json
```

### Parallel Execution

For faster CI execution:

```yaml
# Unit tests
- run: ./scripts/src/codomyrmex/tests/run_tests_batched.sh unit

# Integration tests
- run: ./scripts/src/codomyrmex/tests/run_tests_batched.sh integration

# Examples and performance
- run: ./scripts/src/codomyrmex/tests/run_tests_batched.sh examples
- run: ./scripts/src/codomyrmex/tests/run_tests_batched.sh performance
```

## Troubleshooting

### Common Issues

#### Memory Errors

If tests run out of memory:

```bash
# Run in smaller batches
./scripts/src/codomyrmex/tests/run_tests_batched.sh unit
./scripts/src/codomyrmex/tests/run_tests_batched.sh integration

# Or run with limited parallelism
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

Shared fixtures live in `src/codomyrmex/tests/conftest.py` (e.g. `project_root`, `code_dir`, `temp_env_file`, `sample_markdown_file`, `sample_json_file`, `sample_yaml_file`). Prefer real data and temp paths; do not use `unittest.mock` for core assertions (see Zero-Mock Policy above).

### Test Markers

Apply markers appropriately: decorate tests with `@pytest.mark.unit`, `@pytest.mark.integration`, `@pytest.mark.slow`, or `@pytest.mark.performance`. Each test body must exercise real code paths with concrete assertions (Zero-Mock Policy — no placeholder `assert True` or empty bodies in committed tests).

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
2. **Use appropriate batch** for your changes (unit for small fixes, integration for larger changes)
3. **Check coverage** to ensure adequate test coverage
4. **Review failures** carefully - they may indicate real issues

### Development Strategy

1. **Write tests first** (TDD approach)
2. **Keep tests fast** and isolated
3. **Use descriptive names** for tests and assertions
4. **Test error conditions** and edge cases
5. **Maintain test documentation**

### CI/CD Best Practices

1. **Use batch execution** in CI pipelines
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
# Quick validation
./scripts/src/codomyrmex/tests/run_tests_batched.sh quick

# Full test suite
./scripts/src/codomyrmex/tests/run_tests_batched.sh all --coverage

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

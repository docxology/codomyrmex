# Running Codomyrmex Tests

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Overview

This document provides comprehensive guidance for running the Codomyrmex test suite. The test suite contains **1,203 tests** organized into multiple categories to ensure comprehensive coverage while managing resource usage.

## Test Organization

### Test Categories

| Category | Location | Count | Description | Execution Time |
|----------|----------|-------|-------------|----------------|
| **Unit Tests** | `src/codomyrmex/tests/unit/` | ~800 | Individual component testing | Fast (< 30s) |
| **Integration Tests** | `src/codomyrmex/tests/integration/` | ~200 | Cross-module workflow testing | Moderate (1-5 min) |
| **Example Tests** | `src/codomyrmex/tests/examples/` | ~150 | Example validation and execution | Moderate (30s-2 min) |
| **Performance Tests** | `src/codomyrmex/tests/performance/` | ~50 | Benchmarking and performance validation | Slow (5-15 min) |

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

Generate coverage reports:

```bash
# Run with coverage
uv run pytest --cov=src/codomyrmex --cov-report=html --cov-report=term-missing

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
python -c "import sys; print('
'.join(sys.path))"

# Verify package installation
uv run python -c "import codomyrmex; print('Package imported successfully')"

# Check for syntax errors
find src/ -name "*.py" -exec python -m py_compile {} \;
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
pip install pytest-xdist
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
python scripts/src/codomyrmex/tests/test_summary.py

# Analyze test durations
python scripts/src/codomyrmex/tests/test_summary.py --durations

# Identify flaky tests
python scripts/src/codomyrmex/tests/test_summary.py --flaky
```

## Best Practices

### Test Execution

1. **Run tests locally** before committing
2. **Use appropriate batch** for your changes (unit for small fixes, integration for larger changes)
3. **Check coverage** to ensure adequate test coverage
4. **Review failures** carefully - they may indicate real issues

### Test Development

1. **Write tests first** (TDD approach)
2. **Keep tests fast** and isolated
3. **Use descriptive names** for tests and assertions
4. **Test error conditions** and edge cases
5. **Maintain test documentation**

### CI/CD Integration

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

# Check coverage
uv run pytest --cov=src/codomyrmex --cov-report=html

# Find slow tests
uv run pytest --durations=10 src/codomyrmex/tests/
```

## Navigation Links

- **Parent**: [Project Overview](../README.md)
- **Module Index**: [All Agents](../../AGENTS.md)
- **Documentation**: [Reference Guides](../../../docs/README.md)
- **Home**: [Root README](../../../README.md)

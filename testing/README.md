# testing

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: December 2025

## Overview

The testing directory contains comprehensive test suites that validate the Codomyrmex platform's functionality, performance, and reliability. Tests follow test-driven development (TDD) principles with real data analysis and no mock methods.

The testing framework ensures code quality through automated validation, integration testing, and performance benchmarking.

## Test Organization

### Test Types

Tests are organized by scope and methodology:

**Unit Tests (`unit/`)**
- Individual component testing
- Function and class validation
- Edge case coverage
- Performance benchmarks per component

**Integration Tests (`integration/`)**
- Multi-component workflow validation
- Module interaction testing
- End-to-end scenario coverage
- Cross-module dependency verification

**Specialized Tests**
- Performance benchmarking
- Security validation
- Documentation accuracy testing

## Running Tests

### Complete Test Suite

```bash
# Run all tests with coverage
pytest --cov=src/codomyrmex --cov-report=html --cov-report=term

# Run with verbose output
pytest -v

# Run tests in parallel (if pytest-xdist installed)
pytest -n auto
```

### Specific Test Suites

```bash
# Unit tests only
pytest testing/unit/

# Integration tests only
pytest testing/integration/

# Specific module tests
pytest testing/unit/test_module_name.py
pytest testing/integration/test_workflow.py
```

### Test Configuration

```bash
# Run with different log levels
pytest --log-level=DEBUG

# Generate coverage reports
pytest --cov=src/codomyrmex --cov-report=html:htmlcov --cov-report=xml

# Run specific test markers
pytest -m "slow"  # Tests marked as slow
pytest -m "not integration"  # Exclude integration tests
```

## Test Standards

### TDD Principles

All tests follow test-driven development:

1. **Write Tests First** - Tests define expected behavior before implementation
2. **Real Data Only** - No mock methods; use actual data and implementations
3. **Comprehensive Coverage** - Target ≥80% code coverage across all modules
4. **Continuous Validation** - Tests run on every code change

### Test Structure

Each test follows this pattern:

```python
def test_feature_name():
    """Test description documenting expected behavior."""
    # Arrange - Set up test conditions
    # Act - Execute the functionality
    # Assert - Verify expected outcomes
```

### Test Categories

**Unit Tests**
- Test individual functions and classes
- Validate edge cases and error conditions
- Include property-based testing where applicable
- Mock external dependencies for isolation

**Integration Tests**
- Test real component interactions
- Validate data flow between modules
- Test error propagation and recovery
- Include performance validation under realistic loads

## Test Infrastructure

### Configuration Files

- `pytest.ini` - Test runner configuration and coverage settings
- `conftest.py` - Shared fixtures, setup, and teardown utilities
- `__init__.py` - Package initialization

### Shared Fixtures

Common test fixtures available across all tests:

- `temp_directory` - Temporary directory for file operations
- `mock_config` - Test configuration setup
- `sample_data` - Realistic test data generation
- `database_session` - Database connection for integration tests

## Coverage Requirements

### Coverage Targets

- **Overall Coverage**: ≥80% across all modules
- **Unit Test Coverage**: ≥85% for individual components
- **Integration Coverage**: ≥75% for module interactions
- **Critical Path Coverage**: 100% for user-facing workflows

### Coverage Reports

Generated reports include:
- Line coverage percentages
- Branch coverage analysis
- Missing coverage identification
- HTML visualization of coverage

## Performance Testing

### Benchmark Tests

Performance tests validate system responsiveness:

```python
def test_performance_baseline(benchmark):
    """Benchmark core functionality performance."""
    # Test executes within performance bounds
    result = benchmark(function_under_test, args)
    assert result.execution_time < MAX_TIME
```

### Performance Metrics

- Unit test execution: <100ms per test suite
- Integration test execution: <30 seconds per test suite
- Full test suite: <5 minutes total execution time

## Test Development

### Writing New Tests

1. **Identify Test Scope** - Unit or integration test
2. **Follow Naming Convention** - `test_feature_name.py`
3. **Use Descriptive Names** - `test_user_registration_success`
4. **Include Documentation** - Docstring explaining test purpose
5. **Add Appropriate Markers** - `@pytest.mark.slow`, `@pytest.mark.integration`

### Test Examples

**Unit Test Example**
```python
def test_validate_config_valid_input():
    """Test configuration validation with valid input."""
    config = {"api_key": "valid_key", "timeout": 30}
    validator = ConfigValidator()

    result = validator.validate(config)

    assert result.is_valid is True
    assert len(result.errors) == 0
```

**Integration Test Example**
```python
def test_user_workflow_complete():
    """Test complete user registration and login workflow."""
    # Register user
    user_service.register("test@example.com", "password")

    # Login user
    session = auth_service.login("test@example.com", "password")

    # Verify session
    assert session.is_active is True
    assert session.user.email == "test@example.com"
```

## Directory Contents

### Core Test Infrastructure
- `README.md` – This documentation
- `__init__.py` – Test package initialization
- `conftest.py` – Shared test configuration and fixtures
- `run_all_git_examples.py` – Specialized test runner for git operations

### Test Suites
- `unit/` – Unit tests for individual components and modules
- `integration/` – Integration tests for multi-component workflows

### Test Reports
Generated test outputs:
- `htmlcov/` – HTML coverage reports
- `coverage.xml` – XML coverage data for CI/CD
- `.coverage` – Raw coverage data

## Continuous Integration

### CI/CD Integration

Tests run automatically on:
- Pull request creation
- Code pushes to main branch
- Scheduled nightly runs
- Release candidate validation

### Quality Gates

Code must pass all quality checks:
- All tests pass (unit + integration)
- Coverage requirements met
- No new linting errors
- Performance benchmarks satisfied

## Troubleshooting

### Common Test Issues

**Import Errors**
- Ensure test environment matches development environment
- Check PYTHONPATH includes src directory
- Verify all dependencies installed

**Coverage Issues**
- Run `pytest --cov=src/codomyrmex --cov-report=html`
- Check htmlcov/index.html for missing lines
- Add tests for uncovered code paths

**Performance Failures**
- Identify bottleneck using profiling tools
- Optimize slow code paths
- Update performance benchmarks if justified

### Debug Mode

```bash
# Run tests with debugging
pytest --pdb  # Drop into debugger on failure
pytest -s     # Don't capture output
pytest -v     # Verbose output
```

## Navigation

### Getting Started
- **Quick Start**: Run `pytest` in project root
- **Coverage Report**: Open `htmlcov/index.html` after test run

### Advanced Usage
- **Test Configuration**: [pytest.ini](../../../pytest.ini) - Test runner settings
- **Shared Fixtures**: [conftest.py](conftest.py) - Available test utilities

### Related Documentation
- **Project Root**: [README](../../../README.md) - Main project documentation
- **Testing Strategy**: [docs/development/testing-strategy.md](../../../docs/development/testing-strategy.md)
- **Contributing**: [docs/project/contributing.md](../../../docs/project/contributing.md)

## Contributing

When adding tests:

1. **Write Tests First** - Follow TDD principles
2. **Use Real Data** - No mock methods or fake data
3. **Comprehensive Coverage** - Test edge cases and error conditions
4. **Clear Documentation** - Explain test purpose and expected behavior
5. **Performance Aware** - Include benchmarks for performance-critical code

### Test Template

```python
"""
Test module for feature_name functionality.
"""
import pytest

class TestFeatureName:
    """Test suite for feature_name."""

    def test_basic_functionality(self):
        """Test basic feature operation."""
        # Test implementation
        pass

    def test_edge_cases(self):
        """Test edge cases and error conditions."""
        # Test implementation
        pass

    def test_performance(self, benchmark):
        """Test performance characteristics."""
        # Benchmark implementation
        pass
```

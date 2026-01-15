# Tests Module

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## 1. Overview
The `tests` directory contains the comprehensive test suite for the Codomyrmex project. It ensures code correctness, regression prevention, and performance standards through organized unit, integration, and performance tests.

## 2. Directory Structure

### 2.1 Test Categories
- **`unit/`**: Tests focusing on individual components in isolation. Fast execution, mocked dependencies.
- **`integration/`**: Tests verifying interactions between components or with external systems (e.g., databases, APIs).
- **`performance/`**: Benchmarks and load tests to verify system stability under stress.

### 2.2 Support Files
- **`conftest.py`**: Global Pytest configurations and shared fixtures.
- **`fixtures/`**: Reusable data and state setups for tests.
- **`examples/`**: Example test cases and usage patterns.

## 3. Running Tests
Codomyrmex uses `pytest` as its test runner.

```bash
# Run all tests
pytest src/codomyrmex/tests

# Run only unit tests
pytest src/codomyrmex/tests/unit

# Run tests with coverage
pytest --cov=codomyrmex src/codomyrmex/tests
```

For detailed instructions, refer to [RUNNING_TESTS.md](RUNNING_TESTS.md).

## 4. Key Fixtures
Common fixtures defined in `conftest.py` include:
- `temp_project`: Provides a temporary project directory structure.
- `mock_db`: A session-scoped mock database connection.
- `sample_data`: Standardized input datasets for validation tests.

## 5. Navigation
- **Technical Documentation**: [AGENTS.md](AGENTS.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
- **Detailed Guide**: [RUNNING_TESTS.md](RUNNING_TESTS.md)
- **Parent Directory**: [codomyrmex](../README.md)
- **Project Root**: [README](../../../README.md)

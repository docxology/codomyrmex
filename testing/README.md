# testing

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2025

## Overview

Top-level testing suite coordinating integration and unit coverage for the Codomyrmex platform.

## Testing Architecture

Codomyrmex uses a **dual-location testing strategy**:

### 1. Project-Level Tests (`testing/`)
- **`testing/unit/`** - Centralized unit tests that test modules from the project root perspective
- **`testing/integration/`** - Integration tests verifying cross-module interactions
- **Purpose**: Validate the entire system works together, run in CI/CD pipelines

### 2. Module-Level Tests (`src/codomyrmex/{module}/tests/`)
- Each module may contain its own `tests/` directory
- **Purpose**: Allow modules to be developed and tested in isolation
- **Benefit**: Enables independent module development and self-contained testing

## Directory Structure

```
testing/
├── unit/                    # Centralized unit tests
│   ├── test_ai_code_editing.py
│   ├── test_data_visualization.py
│   ├── test_git_operations.py
│   └── ... (30+ test files)
├── integration/             # Cross-module integration tests
│   ├── test_documentation_accuracy.py
│   ├── test_comprehensive_improvements.py
│   └── ... (integration test files)
├── conftest.py              # Shared pytest fixtures
├── AGENTS.md                # Testing agent configuration
└── README.md                # This file
```

## Key Components

### Active Components
- `integration/` – Integration tests verifying cross-module interactions
- `unit/` – Centralized unit tests for all modules

## Running Tests

### Run All Tests
```bash
# Using pytest directly
pytest testing/ -v

# Using make
make test

# Using uv
uv run pytest testing/ -v
```

### Run Unit Tests Only
```bash
pytest testing/unit/ -v --tb=short
```

### Run Integration Tests Only
```bash
pytest testing/integration/ -v --tb=short
```

### Run Tests with Coverage
```bash
pytest testing/ -v --cov=src/codomyrmex --cov-report=html
```

### Run Tests for a Specific Module
```bash
pytest testing/unit/test_ai_code_editing.py -v
```

## Test Configuration

Tests are configured via:
- **`pytest.ini`** - Root pytest configuration
- **`pyproject.toml`** - Additional pytest settings under `[tool.pytest.ini_options]`
- **`conftest.py`** - Shared fixtures (provides `code_dir` fixture for all tests)

## Test Markers

Available pytest markers:
- `@pytest.mark.unit` - Unit tests
- `@pytest.mark.integration` - Integration tests
- `@pytest.mark.slow` - Long-running tests

## Operating Contracts

- All tests use real implementations (no mock-only tests for core functionality)
- Tests maintain comprehensive coverage (target: 80%+)
- Test files follow naming convention: `test_{module_name}.py`
- Shared fixtures defined in `conftest.py` for consistency

## Related Documentation

- **[Testing Strategy](../docs/development/testing-strategy.md)** - Comprehensive testing approach
- **[Contributing Guide](../docs/project/contributing.md)** - How to add new tests
- **[AGENTS.md](AGENTS.md)** - Testing agent configuration

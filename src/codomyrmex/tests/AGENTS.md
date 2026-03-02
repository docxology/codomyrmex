# Agent Guidelines - Tests

**Version**: v1.0.5 | **Status**: Active | **Last Updated**: March 2026

## Module Overview

Test framework with fixtures, utilities, and test patterns.

## Key Directories

- `unit/` — Unit tests
- `integration/` — Integration tests
- `performance/` — Performance tests
- `fixtures/` — Shared fixtures

## Agent Instructions

1. **Follow AAA** — Arrange, Act, Assert
2. **Use fixtures** — Share setup with fixtures
3. **Test with real data** — Use real data factories, not mocks
4. **Test edge cases** — Not just happy path
5. **Name descriptively** — `test_user_login_fails_with_wrong_password`

## Common Patterns

```python
import pytest
from codomyrmex.tests.fixtures.real_data_factory import create_test_data

# Basic test
def test_function_returns_expected():
    result = function_under_test(input_data)
    assert result == expected_output

# Using fixtures
@pytest.fixture
def sample_user():
    return {"id": 1, "name": "Test"}

def test_user_creation(sample_user):
    user = create_user(sample_user)
    assert user.id == 1

# Parametrized tests
@pytest.mark.parametrize("input,expected", [
    ("a", 1), ("b", 2), ("c", 3)
])
def test_mapping(input, expected):
    assert map_value(input) == expected
```

## Running Tests

```bash
# All tests
pytest

# Specific module
pytest tests/unit/test_auth.py

# With coverage
pytest --cov=codomyrmex
```

## PAI Agent Role Access Matrix

| PAI Agent | Access Level | Primary Capabilities | Trust Level |
|-----------|-------------|---------------------|-------------|
| **Engineer** | Full | Direct Python import, class instantiation, full API access | TRUSTED |
| **Architect** | Read + Design | API review, interface design, dependency analysis | OBSERVED |
| **QATester** | Validation | Integration testing via pytest, output validation | OBSERVED |

### Engineer Agent
**Use Cases**: Maintain test infrastructure, create shared fixtures, manage conftest.py and RealDataFactory during BUILD phases

### Architect Agent
**Use Cases**: Review test architecture, design fixture sharing strategy, evaluate test directory organization

### QATester Agent
**Use Cases**: Run full test suite with coverage, validate coverage gate compliance, verify parametrized test completeness

## Navigation

- [README](README.md) | [SPEC](SPEC.md) | [PAI](PAI.md)

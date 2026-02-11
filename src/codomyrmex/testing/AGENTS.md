# Agent Guidelines - Testing

## Module Overview

Test utilities, fixtures, and testing patterns for Codomyrmex.

## Key Classes

- **TestRunner** — Execute tests with configuration
- **RealDataFactory** — Generate real test data (Zero-Mock policy: no test doubles)
- **FixtureManager** — Manage test fixtures
- **AssertionHelpers** — Enhanced assertions

## Agent Instructions

1. **Use real data** — Avoid mocks; use real implementations with test data
2. **Isolate tests** — Each test should be independent
3. **Use fixtures** — Share setup via pytest fixtures in conftest.py
4. **Cover edge cases** — Test boundaries, errors, empty inputs
5. **Verify assertions** — Include meaningful assertion messages

## Testing Patterns

```python
# Use shared fixtures
@pytest.fixture
def sample_data():
    return {"key": "value"}

def test_feature(sample_data):
    result = process(sample_data)
    assert result is not None, "Processing returned None"

# Test exceptions
def test_error_handling():
    with pytest.raises(ValueError, match="Invalid input"):
        process(None)

# Parameterized tests
@pytest.mark.parametrize("input,expected", [
    ("a", 1),
    ("b", 2),
])
def test_parametrized(input, expected):
    assert transform(input) == expected
```

## Integration Points

- **All modules** — Provide test utilities
- **ci_cd** — Run tests in pipelines

## Navigation

- [README](README.md) | [SPEC](SPEC.md) | [PAI](PAI.md)

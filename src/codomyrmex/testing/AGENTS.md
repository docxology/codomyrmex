# Agent Guidelines - Testing

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

## Module Overview

Test utilities, fixtures, and testing patterns for Codomyrmex.

## Key Classes

- **TestRunner** — Execute tests with configuration
- **RealDataFactory** — Generate real test data (Zero-Mock policy: no test doubles)
- **FixtureManager** — Manage test fixtures
- **AssertionHelpers** — Enhanced assertions

## Agent Instructions

1. **Use real data** — Avoid mocks; use real implementations with test data.
2. **Property Tests** — Use `property_test` for functions with large input spaces.
3. **Resilience Testing** — Use `chaos` sub-module to verify recovery from failure.
4. **Isolate tests** — Each test should be independent and stateless.
5. **Cover edge cases** — Test boundaries, errors, and malicious inputs.

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

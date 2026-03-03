# Agent Guidelines - Testing

**Version**: v1.0.5 | **Status**: Active | **Last Updated**: March 2026

## Module Overview

Test utilities, data factories, and testing patterns for the Codomyrmex platform. Provides
`RealDataFactory` for generating realistic test data under the Zero-Mock policy, `TestRunner` for
configurable test execution, and `FixtureManager` for shared fixture lifecycle. Both MCP tools
(`testing_generate_data`, `testing_list_strategies`) expose data generation capabilities to PAI
agents.

## Key Files

| File | Purpose |
|------|---------|
| `__init__.py` | Exports `TestRunner`, `RealDataFactory`, `FixtureManager`, `AssertionHelpers` |
| `test_runner.py` | Execute tests with configuration and reporting |
| `data_factory.py` | Generate real test data (`RealDataFactory`) |
| `fixture_manager.py` | Manage test fixture lifecycle |
| `assertion_helpers.py` | Enhanced assertion utilities |
| `mcp_tools.py` | MCP tools: `testing_generate_data`, `testing_list_strategies` |

## Key Classes

- **TestRunner** — Execute tests with configuration
- **RealDataFactory** — Generate real test data (Zero-Mock policy: no test doubles)
- **FixtureManager** — Manage test fixture lifecycle
- **AssertionHelpers** — Enhanced assertion utilities

## MCP Tools Available

| Tool | Description | Trust Level |
|------|-------------|-------------|
| `testing_generate_data` | Generate a list of realistic test data records using a named strategy | SAFE |
| `testing_list_strategies` | List all available data generation strategy names | SAFE |

## Agent Instructions

1. **Use real data** — Avoid mocks; use real implementations with `RealDataFactory` test data
2. **Property Tests** — Use parameterized tests for functions with large input spaces
3. **Isolate tests** — Each test must be independent and stateless
4. **Cover edge cases** — Test boundaries, error conditions, and malformed inputs
5. **Zero-Mock** — Never use `unittest.mock`, `MagicMock`, or `monkeypatch` for module internals

## Operating Contracts

- `RealDataFactory` generates deterministic data when a `seed` is provided
- `TestRunner` raises `NotImplementedError` for unsupported test frameworks
- `FixtureManager` fixtures are not shared across test sessions — create fresh per test
- `testing_generate_data` is idempotent with the same strategy name and count
- **DO NOT** use `unittest.mock` or `MagicMock` in tests — use real objects only

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

- **All modules** — Provide test utilities and data factories
- **ci_cd** — Run tests in pipelines

## PAI Agent Role Access Matrix

| PAI Agent | Access Level | MCP Tools | Trust Level |
|-----------|-------------|-----------|-------------|
| **Engineer** | Full | `testing_generate_data`, `testing_list_strategies` | TRUSTED |
| **Architect** | Read + Design | `testing_list_strategies` — test strategy taxonomy review | OBSERVED |
| **QATester** | Validation | `testing_generate_data`, `testing_list_strategies` — full test data generation during VERIFY | OBSERVED |
| **Researcher** | Read-only | `testing_list_strategies`, `testing_generate_data` — data generation for research samples | SAFE |

### Engineer Agent
**Use Cases**: Write and run test suites, configure `TestRunner` and `RealDataFactory` during BUILD/VERIFY phases.

### Architect Agent
**Use Cases**: Design test strategy taxonomy, define coverage targets, plan fixture architecture.

### QATester Agent
**Use Cases**: Generate realistic test data, execute all test categories (unit, integration, performance), report coverage metrics.

### Researcher Agent
**Use Cases**: Generating representative data samples for research analysis using named strategies.

## Navigation

- [README](README.md) | [SPEC](SPEC.md) | [PAI](PAI.md)

# testing

**Version**: v1.0.8 | **Status**: Active | **Last Updated**: March 2026

## Overview

Testing utilities module providing property-based testing, fuzzing, fixture management, and test data generation. Includes configurable generator strategies for producing synthetic test data (integers, floats, strings, lists, dicts) and a `Fuzzer` for randomized input testing. Also contains `chaos` and `workflow` submodules for chaos engineering and workflow testing.

## PAI Integration

| PAI Phase | Capability |
|-----------|-----------|
| VERIFY | Property-based testing via `property_test`, fuzz testing via `Fuzzer` |
| BUILD | Test data generation via generator strategies |
| EXECUTE | Fixture management via `FixtureManager`, chaos scenarios |

## Key Exports

- **`property_test`** -- Decorator for property-based testing
- **`PropertyTestResult`** -- Result of a property test run
- **`Fuzzer`** -- Fuzzing engine with configurable strategies
- **`FuzzingStrategy`** -- Base class for fuzzing strategies
- **`FuzzResult`** -- Result of a fuzz test run
- **`Fixture`** -- Test fixture base class
- **`FixtureManager`** -- Manages fixture lifecycle and dependencies
- **`fixture`** -- Decorator for registering fixtures
- **`TestDataFactory`** -- Factory for creating test data
- **Generator strategies**: `IntGenerator`, `FloatGenerator`, `StringGenerator`, `ListGenerator`, `DictGenerator`, `OneOfGenerator`, `GeneratorStrategy`

## MCP Tools

| Tool | Description |
|------|-------------|
| `testing_generate_data` | Generate synthetic test data using a named strategy (int/float/string/list/dict) |
| `testing_list_strategies` | List available generator strategy type names |

## Quick Start

```python
from codomyrmex.testing import IntGenerator, Fuzzer, property_test

# Generate test data
gen = IntGenerator(min_val=0, max_val=100)
values = [gen.generate() for _ in range(10)]

# Property-based testing
@property_test(num_cases=100)
def test_addition_commutative(a: int, b: int):
    assert a + b == b + a

# Fuzzing
fuzzer = Fuzzer()
result = fuzzer.fuzz(target_function, iterations=1000)
```

## Architecture

```
testing/
  __init__.py         -- Package root; exports all components
  strategies.py       -- GeneratorStrategy, IntGenerator, FloatGenerator, etc.
  property_testing.py -- property_test decorator, PropertyTestResult
  fuzzing.py          -- Fuzzer, FuzzingStrategy, FuzzResult
  fixture_utils.py    -- Fixture, FixtureManager, fixture decorator, TestDataFactory
  mcp_tools.py        -- 2 MCP tool definitions
  chaos/              -- Chaos engineering scenarios
  workflow/           -- Workflow testing utilities
```

## Testing

```bash
uv run pytest src/codomyrmex/tests/unit/testing/ -v
```

## Navigation

- [Root](../../../../../../README.md)

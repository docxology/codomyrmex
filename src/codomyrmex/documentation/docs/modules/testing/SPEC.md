# testing -- Technical Specification

**Version**: v1.1.9 | **Status**: Active | **Last Updated**: March 2026

## Overview

Testing utilities module providing property-based testing, fuzzing, fixture management, and configurable data generators. Includes `chaos` and `workflow` submodules for specialized testing scenarios.

## Design Principles

- **Strategy pattern**: All generators implement `GeneratorStrategy` base class with `generate()` method.
- **Composable generators**: `ListGenerator` and `DictGenerator` accept inner generators.
- **Pure Python**: No external dependencies for core functionality.
- **Decorator-based API**: `@property_test` and `@fixture` for declarative testing.

## Architecture

```
testing/
  __init__.py         -- Package root (exports ~20 symbols)
  strategies.py       -- GeneratorStrategy, IntGenerator, FloatGenerator, StringGenerator, ListGenerator, DictGenerator, OneOfGenerator
  property_testing.py -- property_test decorator, PropertyTestResult
  fuzzing.py          -- Fuzzer, FuzzingStrategy, FuzzResult
  fixture_utils.py    -- Fixture, FixtureManager, fixture decorator, TestDataFactory
  mcp_tools.py        -- 2 MCP tools
  chaos/              -- Chaos engineering scenarios
  workflow/           -- Workflow testing utilities
```

## Functional Requirements

### Generator Strategies
- `IntGenerator(min_val, max_val)` -- Generate random integers in range.
- `FloatGenerator(min_val, max_val)` -- Generate random floats in range.
- `StringGenerator(min_length, max_length)` -- Generate random strings.
- `ListGenerator(element_generator, min_length, max_length)` -- Generate lists using inner generator.
- `DictGenerator(key_generator, value_generator, min_size, max_size)` -- Generate dicts using inner generators.
- `OneOfGenerator(generators)` -- Randomly select and invoke one of multiple generators.

### Property Testing
- `property_test(num_cases: int)` -- Decorator running function with random inputs `num_cases` times.
- `PropertyTestResult` -- Contains pass/fail counts, counterexamples on failure.

### Fuzzing
- `Fuzzer.fuzz(target, iterations)` -- Run target function with randomized inputs.
- `FuzzResult` -- Contains crash info, input that triggered failure.

### Fixtures
- `FixtureManager` -- Lifecycle management for test fixtures (setup/teardown).
- `TestDataFactory` -- Factory for creating complex test data objects.

## Interface Contracts

MCP tool return formats:
- `testing_generate_data`: `list` of generated values (type depends on `strategy_type`)
- `testing_list_strategies`: `["int", "float", "string", "list", "dict"]`

`testing_generate_data` `config` parameter keys by strategy:
- int/float: `min_val`, `max_val`
- string/list: `min_length`, `max_length`
- dict: `min_size`, `max_size`

## Dependencies

- **Internal**: `model_context_protocol.decorators` for `@mcp_tool`, `validation.schemas` (optional)
- **Standard library**: `random`, `string` (no external dependencies)

## Constraints

- `testing_generate_data` raises `ValueError` for unknown `strategy_type`.
- All generators produce non-deterministic output (no seed control via MCP).
- `ListGenerator` defaults to `IntGenerator(0, 10)` as element generator via MCP.

## Navigation

- [Root](../../../../../../README.md)

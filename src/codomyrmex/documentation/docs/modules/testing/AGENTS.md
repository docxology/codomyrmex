# testing - Agent Coordination

**Version**: v1.0.8 | **Status**: Active | **Last Updated**: March 2026

## Overview

Testing utilities module exposing 2 MCP tools for synthetic test data generation plus a comprehensive library of property-based testing, fuzzing, fixture management, and generator strategies for agent-driven test workflows.

## Key Files

| File | Role |
|------|------|
| `__init__.py` | Package root; exports all components + `cli_commands()` |
| `mcp_tools.py` | 2 MCP tool definitions |
| `strategies.py` | `GeneratorStrategy`, `IntGenerator`, `FloatGenerator`, `StringGenerator`, `ListGenerator`, `DictGenerator`, `OneOfGenerator` |
| `property_testing.py` | `property_test` decorator, `PropertyTestResult` |
| `fuzzing.py` | `Fuzzer`, `FuzzingStrategy`, `FuzzResult` |
| `fixture_utils.py` | `Fixture`, `FixtureManager`, `fixture` decorator, `TestDataFactory` |
| `chaos/` | Chaos engineering scenarios |
| `workflow/` | Workflow testing utilities |

## MCP Tools Available

| Tool | Parameters | Returns |
|------|-----------|---------|
| `testing_generate_data` | `strategy_type: str, count: int, config: dict` | List of generated values |
| `testing_list_strategies` | none | `["int", "float", "string", "list", "dict"]` |

## Agent Instructions

1. `testing_generate_data` accepts `strategy_type` as one of `"int"`, `"float"`, `"string"`, `"list"`, `"dict"`.
2. The `config` parameter is optional and controls generator bounds: `min_val`/`max_val` for int/float, `min_length`/`max_length` for string/list, `min_size`/`max_size` for dict.
3. `count` controls how many values to generate (default 10).
4. Both tools are pure Python with no external dependencies.
5. `testing_generate_data` raises `ValueError` for unknown strategy types.

## Operating Contracts

- All generators are stateless; each call produces fresh random values.
- `Fuzzer` is designed for CPU-intensive randomized testing; use with appropriate timeouts.
- Property-based testing via `@property_test` runs `num_cases` iterations by default.

## Common Patterns

```python
# MCP tool usage
result = testing_generate_data("string", count=5, config={"min_length": 3, "max_length": 10})
# Returns: ["abc", "defgh", "ij", "klmno", "pq"]
```

## PAI Agent Role Access Matrix

| Agent Role | Access Level | Primary Tools |
|-----------|-------------|---------------|
| Engineer | Full | Both tools |
| QATester | Full | Both tools |

## Navigation

- [Root](../../../../../../README.md)

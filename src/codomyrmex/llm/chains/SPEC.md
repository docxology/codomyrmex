# Reasoning Chains -- Technical Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Composable chain abstractions for multi-step LLM reasoning. Chains decouple prompt construction and output parsing from the underlying LLM call, allowing the same chain logic to work with any provider.

## Architecture

Strategy pattern: `Chain` is an abstract base class. Concrete strategies (`SimpleChain`, `SequentialChain`, `ReActChain`) implement `run()`. A factory function `create_chain(ChainType, **kwargs)` instantiates the correct class. `ChainStep` objects define individual prompt templates and optional output parsers.

## Key Classes

### `ChainStep`

| Field | Type | Description |
|-------|------|-------------|
| `name` | `str` | Identifier for this step |
| `prompt_template` | `str` | Template with `{variable}` placeholders |
| `output_key` | `str` | Key under which parsed output is stored in context (default `"output"`) |
| `input_keys` | `list[str]` | Expected input keys from context |
| `parser` | `Callable[[str], Any] \| None` | Optional output parser |

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `format_prompt` | `context: dict[str, Any]` | `str` | Substitutes context values into template |
| `parse_output` | `output: str` | `Any` | Applies parser if set, else returns raw string |

### `SimpleChain`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `run` | `input_data: dict, llm_func: Callable` | `ChainResult` | Formats single prompt, calls LLM, returns result |

### `SequentialChain`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `run` | `input_data: dict, llm_func: Callable` | `ChainResult` | Iterates steps, accumulating output keys in a shared context dict |
| `add_step` | `step: ChainStep` | `Chain` | Appends step to chain (fluent API) |

### `ReActChain`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `run` | `input_data: dict, llm_func: Callable` | `ChainResult` | Iterative loop: parse `Action: Tool[input]`, call tool, append observation |

Constructor: `tools: dict[str, Callable[[str], str]]`, `max_iterations: int = 5`

### Output Parsers

| Function | Returns | Description |
|----------|---------|-------------|
| `json_parser(output)` | `dict` | Extracts JSON from raw output or markdown code blocks |
| `list_parser(output)` | `list[str]` | Strips numbering/bullets, returns clean list items |

## Dependencies

- **Internal**: None
- **External**: Standard library only (`json`, `re`, `abc`, `dataclasses`, `enum`)

## Constraints

- `ReActChain` stops after `max_iterations` and returns `ChainResult(success=False, error="Max iterations reached")`.
- Template variable substitution uses simple string replace, not full Jinja2.
- Zero-mock: real LLM calls only; `NotImplementedError` for unimplemented paths.

## Error Handling

- All exceptions in `run()` are caught and returned in `ChainResult(success=False, error=str(e))`.
- No exception propagation from chain execution -- callers check `ChainResult.success`.

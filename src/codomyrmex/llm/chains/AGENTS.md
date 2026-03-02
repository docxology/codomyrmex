# Codomyrmex Agents — src/codomyrmex/llm/chains

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose

Provides composable chain implementations for multi-step LLM reasoning. Includes sequential chains, chain-of-thought prompting, ReAct (Reason + Act) tool-use loops, and output parsers for structured extraction from LLM responses.

## Key Components

| File | Class / Function | Role |
|------|-----------------|------|
| `__init__.py` | `ChainType` | Enum of chain types: SIMPLE, SEQUENTIAL, PARALLEL, CONDITIONAL, MAP_REDUCE, ROUTER |
| `__init__.py` | `ChainStep` | Dataclass representing a single step with prompt template, output key, and optional parser |
| `__init__.py` | `ChainResult` | Dataclass for chain execution result with success flag, output, step history, and context |
| `__init__.py` | `Chain` | Abstract base class requiring `run(input_data, llm_func)` |
| `__init__.py` | `SimpleChain` | Single-step chain that substitutes variables into a prompt template |
| `__init__.py` | `SequentialChain` | Runs steps in order, passing each output into the next step's context |
| `__init__.py` | `ChainOfThought` | Pre-configured SequentialChain with reasoning and answer extraction steps |
| `__init__.py` | `ReActChain` | Iterative Reason+Act loop that parses `Action: ToolName[input]` from LLM output |
| `__init__.py` | `create_chain` | Factory function mapping `ChainType` to chain class |
| `__init__.py` | `json_parser` | Extracts JSON from LLM output (handles markdown code blocks) |
| `__init__.py` | `list_parser` | Parses numbered or bulleted lists from LLM output |

## Operating Contracts

- All chains accept an `llm_func: Callable[[str], str]` -- the caller provides the LLM call.
- `ChainResult.success` is `False` on any exception; the error message is captured in `ChainResult.error`.
- `ReActChain` enforces a `max_iterations` limit (default 5) to prevent infinite loops.
- `ChainStep.parser` is optional; when absent, raw LLM output string is used as-is.
- Errors must be logged via `logging_monitoring` before re-raising.

## Integration Points

- **Depends on**: Standard library only (`json`, `re`, `abc`, `dataclasses`, `enum`)
- **Used by**: `codomyrmex.llm` (parent module exports), agent orchestration pipelines

## Navigation

- **Parent**: [llm](../README.md)
- **Root**: [Root](../../../../README.md)

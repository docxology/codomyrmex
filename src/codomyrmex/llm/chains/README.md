# llm/chains

**Version**: v0.1.7 | **Status**: Active | **Last Updated**: February 2026

## Overview

Chain implementations for LLM reasoning. Provides chain-of-thought, ReAct (Reason + Act), and multi-step sequential processing patterns. Chains accept an LLM function callback and input data, executing through defined steps with context propagation and output parsing.

## Key Exports

### Enums

- **`ChainType`** -- Chain execution patterns: `SIMPLE`, `SEQUENTIAL`, `PARALLEL`, `CONDITIONAL`, `MAP_REDUCE`, `ROUTER`

### Data Classes

- **`ChainStep`** -- A single step in a chain with name, prompt template (supports `{key}` substitution), output key, input key dependencies, and an optional output parser function
- **`ChainResult`** -- Result of a chain execution with success flag, final output, per-step results, accumulated context, and optional error message. Includes `get_step_output()` for named step retrieval

### Abstract Base Class

- **`Chain`** -- ABC with `chain_type`, step list, and `run(input_data, llm_func)` interface. Supports `add_step()` for fluent chain building

### Chain Implementations

- **`SimpleChain`** -- Single-step chain that formats a prompt template and calls the LLM function once
- **`SequentialChain`** -- Multi-step chain that runs steps in order, passing each step's output into the shared context for subsequent steps. Supports custom output parsers per step
- **`ChainOfThought`** -- Pre-configured SequentialChain implementing chain-of-thought reasoning with a systematic reasoning step followed by an answer extraction step
- **`ReActChain`** -- Implements the Reason + Act pattern with tool integration. Parses `Action: ToolName[input]` from LLM output, executes matching tools, accumulates a scratchpad of observations, and terminates when `Action: Finish[answer]` is produced or max iterations reached

### Output Parsers

- **`json_parser()`** -- Parse JSON from LLM output, including extraction from Markdown code blocks
- **`list_parser()`** -- Parse numbered or bulleted lists from LLM output, stripping markers

### Factory Function

- **`create_chain()`** -- Create a chain by `ChainType` enum with keyword arguments

## Directory Contents

- `__init__.py` - Chain ABC, four implementations, step/result models, parsers, and factory function (331 lines)
- `py.typed` - PEP 561 typing marker
- `SPEC.md` - Module specification
- `AGENTS.md` - Agent integration documentation
- `PAI.md` - PAI integration notes

## Navigation

- **Parent Module**: [llm](../README.md)
- **Project Root**: [codomyrmex](../../../../README.md)

# llm/tools

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

Tool calling framework for LLMs. Provides utilities for defining, registering, and executing tools compatible with both OpenAI and Anthropic function calling formats. Includes a decorator for automatic tool creation from Python functions and a global registry for tool management.

## Key Exports

### Enums

- **`ParameterType`** -- JSON Schema parameter types: `STRING`, `INTEGER`, `NUMBER`, `BOOLEAN`, `ARRAY`, `OBJECT`

### Data Classes

- **`ToolParameter`** -- Definition of a tool parameter with name, type, description, required flag, optional enum constraints, default value, and array items type. Includes `to_json_schema()` conversion
- **`ToolResult`** -- Result of tool execution with success flag, output value, optional error message, and metadata. Includes `to_string()` for LLM-friendly output formatting (JSON for dicts/lists, plain string otherwise)
- **`Tool`** -- A callable tool with name, description, parameter list, function reference, and optional category. Includes:
  - `to_openai_format()` -- Convert to OpenAI function calling schema
  - `to_anthropic_format()` -- Convert to Anthropic tool use schema
  - `execute()` -- Run the tool with keyword arguments, returning a ToolResult

### Registry

- **`ToolRegistry`** -- Central registry for managing tools with methods:
  - `register()` -- Register a tool with optional category tracking
  - `get()` -- Retrieve a tool by name
  - `list_tools()` -- List all tools or filter by category
  - `to_openai_format()` / `to_anthropic_format()` -- Bulk schema conversion
  - `execute()` -- Execute a registered tool by name

### Decorator

- **`tool()`** -- Decorator that creates a `Tool` from a Python function. Automatically extracts parameters from type hints and function signature, parses descriptions from docstrings, and optionally auto-registers into a `ToolRegistry`

### Built-in Tool Factories

- **`create_calculator_tool()`** -- Create a calculator tool for safe mathematical expression evaluation
- **`create_datetime_tool()`** -- Create a datetime tool returning current time in configurable strftime format

### Global Registry

- **`DEFAULT_REGISTRY`** -- Module-level singleton `ToolRegistry` instance
- **`register_tool()`** -- Register a tool in the default registry
- **`get_tool()`** -- Retrieve a tool from the default registry

## Directory Contents

- `__init__.py` - Tool framework: Tool, ToolRegistry, decorator, parameter types, built-in tools, and global registry (325 lines)
- `py.typed` - PEP 561 typing marker
- `SPEC.md` - Module specification
- `AGENTS.md` - Agent integration documentation
- `PAI.md` - PAI integration notes

## Navigation

- **Parent Module**: [llm](../README.md)
- **Project Root**: [codomyrmex](../../../../README.md)

# Codomyrmex Agents — src/codomyrmex/model_context_protocol/quality

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose

Provides argument validation, tool taxonomy classification, and testing utilities for MCP tools. Three sub-concerns: (1) validating tool arguments against JSON Schema before dispatch, with optional type coercion; (2) auto-classifying tools into semantic categories (analysis, generation, execution, query, mutation) via regex pattern matching; (3) testing MCP tools, servers, and end-to-end integration scenarios.

## Key Components

| File | Class / Function | Role |
|------|-----------------|------|
| `validation.py` | `validate_tool_arguments()` | Validates arguments against a tool's `inputSchema` with optional type coercion (`str` to `int`/`bool`/`float`) |
| `validation.py` | `ValidationResult` | Dataclass with `valid`, `errors`, and `coerced_args` fields |
| `validation.py` | `_generate_schema_from_func()` | Generates JSON Schema from a function's type annotations and signature |
| `taxonomy.py` | `ToolCategory` | Enum: ANALYSIS, GENERATION, EXECUTION, QUERY, MUTATION |
| `taxonomy.py` | `categorize_tool()` | Classifies a tool name against ordered regex rules; defaults to QUERY |
| `taxonomy.py` | `generate_taxonomy_report()` | Produces a `TaxonomyReport` with per-category counts and tool assignments |
| `testing.py` | `ToolTester` | Runs test cases against individual MCP tools via a registry |
| `testing.py` | `ServerTester` | Tests MCP server `initialize` and `tools/list` endpoints via JSON-RPC |
| `testing.py` | `IntegrationTester` | Orchestrates multi-step scenarios with shared context and template substitution |
| `testing.py` | `TestMCPClient` | Lightweight client for testing MCP servers (initialize, list_tools, call_tool, list_resources) |
| `testing.py` | `TestResult` / `TestSuite` | Dataclasses for individual test results and aggregated suite metrics |

## Operating Contracts

- Validation uses `jsonschema` when available; falls back to a built-in checker for `required`, `type`, `enum`, `minimum`/`maximum`, and `pattern`.
- Type coercion is opt-in (default enabled): converts string values to declared schema types before validation.
- Taxonomy classification uses first-match-wins ordering on regex rules; unmatched tools default to `QUERY` (conservative: assume read-only).
- `ServerTester` sends real JSON-RPC 2.0 messages to the server's `handle_request` method.
- Errors must be logged via `logging_monitoring` before re-raising.

## Integration Points

- **Depends on**: `codomyrmex.logging_monitoring` (structured logging)
- **Used by**: `model_context_protocol.discovery` (imports `_generate_schema_from_func` for schema generation at decoration time), `model_context_protocol.transport.server` (calls `validate_tool_arguments` before tool dispatch)

## Navigation

- **Parent**: [model_context_protocol](../README.md)
- **Root**: [Root](../../../../README.md)

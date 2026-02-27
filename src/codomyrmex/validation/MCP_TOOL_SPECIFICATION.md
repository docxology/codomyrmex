# Validation - MCP Tool Specification

This document specifies the MCP tools exposed by the Validation module via `@mcp_tool` decorators in `mcp_tools.py`. These tools are auto-discovered by the PAI MCP bridge.

## Available MCP Tools

### `validate_schema`

Validate arbitrary data against a JSON Schema or Pydantic model.

**Parameters:**
- `data` (dict, required): Data to validate
- `schema` (dict, required): JSON Schema definition or Pydantic model reference
- `validator_type` (str, default `"json_schema"`): Strategy — `"json_schema"`, `"pydantic"`, or `"custom"`

**Returns:** `{is_valid, errors: [{field, message}], warnings: [...]}`

**Trust level:** Safe

---

### `validate_config`

Validate a configuration dictionary for required keys and type correctness.

**Parameters:**
- `config` (dict, required): Configuration dictionary to validate
- `required_keys` (list[str], optional): Keys that must be present
- `strict` (bool, default `false`): Reject unknown keys if `true`

**Returns:** `{is_valid, missing_keys: [...], extra_keys: [...], errors: [...]}`

**Trust level:** Safe

---

### `validation_summary`

Return aggregate statistics from the validation manager.

**Parameters:** None

**Returns:** `{run_count, pass_rate, error_rate, validators_used: [...]}`

**Trust level:** Safe

---

For programmatic Python integration, refer to `README.md` and `API_SPECIFICATION.md`.

## Navigation Links

- **Parent**: [Project Overview](../README.md)
- **Module Index**: [All Agents](../../AGENTS.md)
- **Documentation**: [Reference Guides](../../../docs/README.md)
- **Home**: [Root README](../../../README.md)

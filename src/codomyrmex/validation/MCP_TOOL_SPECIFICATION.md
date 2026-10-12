# Validation - MCP Tool Specification

This document specifies the MCP tools exposed by the Validation module via `@mcp_tool` decorators in `mcp_tools.py`. These tools are auto-discovered by the PAI MCP bridge and surfaced as `codomyrmex.<name>`.

## Available MCP Tools

### `validate_schema`

Validate arbitrary data against a JSON Schema or Pydantic model.

**Parameters:**

- `data` (dict, required): Data to validate
- `schema` (dict, required): JSON Schema definition or Pydantic model reference
- `validator_type` (str, default `"json_schema"`): Strategy — `"json_schema"`, `"pydantic"`, or `"custom"`

**Returns:** `{is_valid, errors: [{message, field, code}], warnings: [{message, field}]}`

**Trust level:** Safe

---

### `validation_validate_config`

Validate a configuration dictionary for required keys. (`validate_config` is a different tool, provided by the `config_management` module.)

**Parameters:**

- `config` (dict, required): Configuration dictionary to validate
- `required_keys` (list[str], optional): Keys that must be present
- `strict` (bool, default `false`): Warn about keys not in `required_keys` (only when `required_keys` is given)

**Returns:** `{is_valid, errors: [{field, message}], warnings: [{field, message}], missing_keys: [...], key_count}`. Missing required keys are errors; required keys set to `null` and, in strict mode, unknown keys are warnings.

**Trust level:** Safe

---

### `validation_summary`

Return aggregate statistics from the module's `ValidationManager`.

**Parameters:** None

**Returns:** `{runs, successes, failures, pass_rate, avg_duration_ms, validators_used: [...]}`, or `{runs: 0, pass_rate: 0}` before any validation has run.

**Trust level:** Safe

---

For programmatic Python integration, refer to `README.md` and `API_SPECIFICATION.md`.

## Navigation Links

- **Parent**: [Project Overview](../README.md)
- **Module Index**: [All Agents](../../AGENTS.md)
- **Documentation**: [Reference Guides](../../../docs/README.md)
- **Home**: [Root README](../../../README.md)

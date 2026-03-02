# Personal AI Infrastructure — Validation Module

**Version**: v1.0.5 | **Status**: Active | **Last Updated**: March 2026

## Overview

The Validation module provides data schema and configuration validation. It validates
data against JSON Schema definitions, checks configuration dictionaries for required
keys, and reports session-level validation statistics.

Validation is a **Foundation Layer** utility — it is consumed by `maintenance/`,
`ci_cd_automation/`, and any module that needs to confirm data shapes at runtime
before processing. It also exposes the shared `Result` and `ResultStatus` types used
across codomyrmex for uniform, machine-readable operation outcomes.

## PAI Capabilities

### Schema Validation (MCP)

Validate any data dictionary against a JSON Schema definition:

```python
result = mcp_call("codomyrmex.validate_schema", {
    "data": {"name": "Alice", "age": 30},
    "schema": {
        "type": "object",
        "properties": {"name": {"type": "string"}, "age": {"type": "integer"}},
        "required": ["name", "age"],
    },
    "validator_type": "json_schema",
})
# Returns: {"is_valid": true, "errors": [], "warnings": []}
```

### Config Validation (MCP)

Check a configuration dictionary for required keys and optionally reject unknown keys:

```python
result = mcp_call("codomyrmex.validate_config", {
    "config": {"host": "localhost", "port": 5432, "db": "main"},
    "required_keys": ["host", "port", "db"],
    "strict": False,
})
# Returns: {"is_valid": true, "errors": [], "warnings": [], "missing_keys": [], "key_count": 3}
```

### Validation Summary (MCP)

Retrieve session-wide statistics on all validation runs performed:

```python
result = mcp_call("codomyrmex.validation_summary")
# Returns: run count, pass rate, error rate, validators used
```

### Result and ResultStatus Types (Python)

The module exports canonical result types used across codomyrmex:

```python
from codomyrmex.validation import Result, ResultStatus

result = Result(
    status=ResultStatus.SUCCESS,
    data={"key": "value"},
    message="Operation completed",
)

if result.status == ResultStatus.SUCCESS:
    process(result.data)
elif result.status == ResultStatus.FAILURE:
    raise RuntimeError(result.message)
```

`ResultStatus` values: `SUCCESS`, `FAILURE`, `PARTIAL`, `PENDING`, `SKIPPED`

## MCP Tools

| Tool | Description | Trust Level | Category |
|------|-------------|-------------|----------|
| `codomyrmex.validate_schema` | Validate data against a JSON Schema definition | Safe | validation |
| `codomyrmex.validate_config` | Check config dict for required keys; strict mode rejects extras | Safe | validation |
| `codomyrmex.validation_summary` | Return session-wide validation run statistics | Safe | validation |

### Tool Signatures

**`validate_schema(data, schema, validator_type="json_schema")`**
- `data`: dict — data to validate
- `schema`: dict — JSON Schema or Pydantic model reference
- `validator_type`: str — `"json_schema"`, `"pydantic"`, or `"custom"`
- Returns: `{"is_valid": bool, "errors": [...], "warnings": [...]}`

**`validate_config(config, required_keys=None, strict=False)`**
- `config`: dict — configuration dictionary
- `required_keys`: list[str] | None — keys that must be present
- `strict`: bool — if True, reject unknown keys as warnings
- Returns: `{"is_valid": bool, "errors": [...], "warnings": [...], "missing_keys": [...], "key_count": int}`

**`validation_summary()`**
- No arguments
- Returns: summary dict with run count, pass rate, error rate, validators used

## PAI Algorithm Phase Mapping

| Phase | Validation Contribution | MCP Tools |
|-------|-------------------------|-----------|
| **OBSERVE** (1/7) | Confirm input data shapes before work begins | `validate_schema`, `validate_config` |
| **BUILD** (4/7) | Verify produced artifact schemas match expected contracts | `validate_schema` |
| **VERIFY** (6/7) | Final confirmation that output data is well-formed | `validate_schema`, `validation_summary` |
| **LEARN** (7/7) | Review session validation statistics for system health trends | `validation_summary` |

### Concrete PAI Usage Pattern

In a VERIFY phase ISC criterion "Output data matches expected schema":

```python
# PAI VERIFY — confirm output data is well-formed before declaring success
result = mcp_call("codomyrmex.validate_schema", {
    "data": produced_output,
    "schema": expected_schema,
})
assert result["is_valid"], f"Output schema violations: {result['errors']}"
```

## PAI Configuration

| Environment Variable | Default | Purpose |
|---------------------|---------|---------|
| `CODOMYRMEX_VALIDATION_STRICT` | `false` | If `true`, treat warnings as errors |
| `CODOMYRMEX_SKIP_VALIDATION_MODULES` | `""` | Comma-separated modules to skip in batch runs |

## PAI Best Practices

1. **Use `validate_config` at module entry points**: Before running any module
   operation that requires configuration, call `validate_config` with `required_keys`
   to fail fast if a required setting is absent.

2. **Use `validate_schema` to protect integration boundaries**: When one module
   consumes output from another, validate the shape before processing. This prevents
   silent data corruption from propagating.

3. **Use `validation_summary` in CI**: Add a post-run check that calls
   `validation_summary` and asserts the pass rate is above threshold — this catches
   regressions in data quality across the pipeline.

4. **Use `Result`/`ResultStatus` for all module return values**: Uniform result types
   give PAI agents a consistent way to check operation outcomes without
   module-specific parsing logic.

## Architecture Role

**Foundation Layer** — Cross-cutting validation utility. No upstream codomyrmex
dependencies. Consumed by `maintenance/`, `ci_cd_automation/`, and any module that
validates data at runtime.

## Navigation

- **Self**: [PAI.md](PAI.md)
- **Parent**: [../PAI.md](../PAI.md) — Source-level PAI module map
- **Root Bridge**: [../../../PAI.md](../../../PAI.md) — Authoritative PAI system bridge doc
- **Siblings**: [README.md](README.md) | [AGENTS.md](AGENTS.md) | [SPEC.md](SPEC.md) | [API_SPECIFICATION.md](API_SPECIFICATION.md)

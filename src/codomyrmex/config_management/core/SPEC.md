# Config Management Core -- Functional Specification

## Overview

Multi-source configuration loading, JSON schema validation, and environment-aware configuration management. All classes reside in `config_loader.py`.

## Key Classes

### `ConfigSchema`

JSON schema wrapper for configuration validation.

| Field | Type | Description |
|-------|------|-------------|
| `schema` | `dict[str, Any]` | JSON schema definition |
| `version` | `str` | Schema draft version (default `"draft7"`) |
| `title` | `str` | Schema title |
| `description` | `str` | Schema description |

| Method | Description |
|--------|-------------|
| `validate(config) -> list[str]` | Validate config dict against schema; returns list of error strings (empty = valid). Uses `jsonschema.FormatChecker` for draft versions. |

### `Configuration`

Configuration data object with validation and metadata.

| Field | Type | Description |
|-------|------|-------------|
| `data` | `dict[str, Any]` | Configuration key-value data |
| `source` | `str` | Comma-separated source identifiers |
| `loaded_at` | `datetime` | Auto-set on init (UTC) |
| `schema` | `ConfigSchema \| None` | Optional validation schema |
| `environment` | `str` | Environment name (default `"default"`) |
| `version` | `str` | Config version (default `"1.0.0"`) |
| `metadata` | `dict[str, Any]` | Arbitrary metadata |

| Method | Description |
|--------|-------------|
| `validate() -> list[str]` | Delegate to `schema.validate()` if schema is set |
| `get_value(key, default=None)` | Dot-notation lookup (`"a.b.c"` traverses nested dicts) |
| `set_value(key, value)` | Dot-notation setter; creates intermediate dicts |
| `to_dict() -> dict` | Serialise to JSON-compatible dict |

### `ConfigurationManager`

Comprehensive multi-source configuration manager.

| Field | Type | Description |
|-------|------|-------------|
| `config_dir` | `str` | Configuration directory (default `{cwd}/config/`) |
| `configurations` | `dict[str, Configuration]` | Loaded configs keyed by name |
| `schemas` | `dict[str, ConfigSchema]` | Registered schemas |
| `environment` | `str` | From `ENVIRONMENT` env var (default `"development"`) |

| Method | Description |
|--------|-------------|
| `load_configuration(name, sources, schema_path)` | Load and merge from multiple sources; validate if schema provided |
| `get_configuration(name)` | Retrieve previously loaded config |
| `register_schema(name, schema_path)` | Register a JSON schema for future validation |

**Source types supported by `_load_source()`:**

| Prefix | Handling |
|--------|----------|
| `env://` | Read from environment variable |
| `file://` | Read from explicit file path |
| `http://` / `https://` | Fetch via `requests.get()` |
| *(bare path)* | Resolve relative to `config_dir`; load YAML or JSON |

**Default source search order** (when `sources` is `None`):
1. `{name}.yaml`
2. `{name}.yml`
3. `{name}.json`
4. `environments/{environment}/{name}.yaml`
5. `environments/{environment}/{name}.yml`
6. `environments/{environment}/{name}.json`
7. Environment variables with `{NAME}_` prefix

## Dependencies

- `jsonschema` -- JSON schema validation
- `pyyaml` (via `yaml`) -- YAML file parsing
- `requests` -- URL source fetching
- `codomyrmex.logging_monitoring` -- structured logging
- `codomyrmex.exceptions` -- `ConfigurationError`, `FileOperationError`, `ValidationError`

## Error Handling

- Schema validation errors are collected and returned as `list[str]` (non-throwing).
- `FileNotFoundError` raised when a specific single source is requested but not found.
- Falls back to `tempfile.mkdtemp()` if config directory is not writable (`OSError`/`PermissionError`).

## Navigation

- **Specification**: This file
- **Agent coordination**: [AGENTS.md](AGENTS.md)
- **Parent**: [config_management/](../SPEC.md)

# Config Management Core -- Agent Coordination

## Purpose

Core configuration loading, validation, and management. Provides multi-source configuration loading (YAML, JSON, environment variables, URLs), JSON schema validation via `jsonschema`, dot-notation access, and environment-specific configuration merging.

## Key Components

| Component | File | Role |
|-----------|------|------|
| `ConfigSchema` | `config_loader.py` | JSON schema wrapper with `jsonschema` validation and `FormatChecker` support |
| `Configuration` | `config_loader.py` | Config object with dot-notation `get_value()` / `set_value()`, schema validation, serialisation |
| `ConfigurationManager` | `config_loader.py` | Multi-source loader, schema registry, env-specific merging, hot-reload |

## Operating Contracts

- **Multi-source loading**: `ConfigurationManager.load_configuration()` merges from files (YAML/JSON), environment variables (`{NAME}_` prefix), and URL sources (`http://`, `https://`). Later sources override earlier ones.
- **Source resolution order**: `{name}.yaml` -> `{name}.yml` -> `{name}.json` -> `environments/{env}/{name}.*` -> environment variables.
- **Schema validation**: If a `schema_path` is provided, configuration is validated against a JSON schema using `jsonschema`. Validation errors are logged as warnings but do not prevent loading.
- **Dot-notation access**: `Configuration.get_value("a.b.c")` traverses nested dicts. `set_value()` creates intermediate dicts as needed.
- **Config directory**: Defaults to `{cwd}/config/`. Falls back to `tempfile.mkdtemp()` if the path is not writable.
- **No MCP tools**: This submodule does not directly expose MCP tools. The parent `config_management` module exposes `get_config`, `set_config`, `validate_config` via `@mcp_tool` decorators.

## Integration Points

- **Logging**: Uses `codomyrmex.logging_monitoring.core.logger_config.get_logger`.
- **Exceptions**: Uses `codomyrmex.exceptions.ConfigurationError`, `FileOperationError`, `ValidationError`.
- **External deps**: `jsonschema` (validation), `pyyaml` (YAML loading), `requests` (URL source loading).

## Navigation

- **Parent**: [config_management/](../AGENTS.md)
- **Siblings**: [monitoring/](../monitoring/AGENTS.md)
- **Specification**: [SPEC.md](SPEC.md)

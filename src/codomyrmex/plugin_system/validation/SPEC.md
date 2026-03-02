# Plugin System Validation -- Technical Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Provides security scanning, metadata validation, dependency checking, Dockerfile auditing, and interface enforcement for plugins before they are loaded into the Codomyrmex plugin system.

## Architecture

Two complementary validation subsystems: `PluginValidator` for metadata, dependency, and source-level security scanning, and `InterfaceEnforcer` for structural interface conformance checks with optional signature validation via `inspect.signature`.

## Key Classes

### `PluginValidator`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `validate` | `plugin: Plugin` | `ValidationResult` | Check required methods (`initialize`, `shutdown`) exist |
| `validate_plugin_metadata` | `metadata: dict` | `ValidationResult` | Verify required fields (`name`, `version`) |
| `check_plugin_dependencies` | `deps_or_info: PluginInfo\|list[str], available: list[str]\|None` | `ValidationResult` | Check dependency satisfaction; warns on risky deps |
| `validate_dockerfile` | `content: str` | `ValidationResult` | Check for `FROM` instruction, flag `chmod 777` and `USER root` |
| `validate_plugin` | `target: str\|Plugin` | `ValidationResult` | Dispatch: file path triggers security scan, Plugin triggers `validate` |

### `ValidationResult` (dataclass)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `valid` | `bool` | `True` | Overall pass/fail |
| `issues` | `list[dict]` | `[]` | Error-level findings with type, message, severity |
| `warnings` | `list[dict]` | `[]` | Warning-level findings |
| `security_score` | `float` | `100.0` | Starts at 100, decremented by 20 per finding |

### `InterfaceEnforcer`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `enforce` | `plugin_obj, interface_class` | `bool` | Quick check: all public callable methods present |
| `enforce_detailed` | `plugin_obj, interface_class` | `EnforcementResult` | Full check with signature comparison |
| `enforce_batch` | `plugins: list, interface_class` | `list[EnforcementResult]` | Validate multiple plugins at once |
| `report` | `results: list[EnforcementResult]` | `str` | Human-readable enforcement report |

### `EnforcementResult` (dataclass)

| Field | Type | Description |
|-------|------|-------------|
| `plugin_name` | `str` | Class name of the plugin object |
| `interface_name` | `str` | Class name of the required interface |
| `passed` | `bool` | Whether all checks passed |
| `missing_methods` | `list[str]` | Required callable methods not found |
| `missing_properties` | `list[str]` | Required properties not found |
| `signature_mismatches` | `list[str]` | Parameter count mismatches |

## Dependencies

- **Internal**: `plugin_system.core.plugin_registry` (Plugin, PluginInfo)
- **External**: `os`, `re`, `inspect` (stdlib)

## Constraints

- Risky imports list: `os`, `subprocess`, `shutil`, `socket`, `requests`, `urllib`.
- Suspicious patterns: `os.system`, `subprocess.`, `eval(`, `exec(`, `open(.*w`, `rm -rf`, `chmod`, hardcoded API key regex.
- Safe dependencies: `requests`, `click`, `pyyaml`, `pytest`; risky dependencies: `cryptography`, `paramiko`, `docker`, `os`, `subprocess`.
- Signature validation compares parameter count only (excluding `self`); `ValueError`/`TypeError` during signature inspection is logged and skipped.
- Zero-mock: real file reads and regex scans only, `NotImplementedError` for unimplemented paths.

## Error Handling

- File scanning catches all exceptions and records them as issues with severity `error`.
- `enforce_detailed` catches `ValueError`/`TypeError` from `inspect.signature` without failing the check.
- All errors logged before propagation.

# Codomyrmex Agents -- src/codomyrmex/plugin_system/validation

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose

Validates plugins for security, compatibility, metadata correctness, dependency safety, and interface conformance before they are loaded into the plugin system.

## Key Components

| File | Class / Function | Role |
|------|-----------------|------|
| `plugin_validator.py` | `PluginValidator` | Central validator checking metadata, dependencies, Dockerfile safety, and source file security patterns |
| `plugin_validator.py` | `ValidationResult` | Dataclass holding `valid`, `issues`, `warnings`, and `security_score` |
| `plugin_validator.py` | `validate_plugin` | Module-level helper instantiating `PluginValidator` and running validation |
| `enforcer.py` | `InterfaceEnforcer` | Static methods that verify plugin objects implement required interface methods, properties, and signatures |
| `enforcer.py` | `EnforcementResult` | Dataclass with `passed`, `missing_methods`, `missing_properties`, `signature_mismatches` |

## Operating Contracts

- `PluginValidator` maintains lists of risky imports (`os`, `subprocess`, `shutil`, `socket`, `requests`, `urllib`) and suspicious patterns (`eval`, `exec`, `os.system`, `subprocess`, hardcoded API keys).
- Security score starts at 100 and decreases by 20 for each issue found during file scanning.
- `validate_plugin` accepts either a file path (triggers `_scan_file_security`) or a `Plugin` instance (triggers `validate` method check).
- `InterfaceEnforcer.enforce` returns a boolean; `enforce_detailed` returns a full `EnforcementResult` with signature mismatch details.
- `InterfaceEnforcer.enforce_batch` validates multiple plugins against a single interface class.
- Errors must be logged via `logging_monitoring` before re-raising.

## Integration Points

- **Depends on**: `plugin_system.core.plugin_registry` (Plugin, PluginInfo)
- **Used by**: `plugin_system.core.plugin_manager.PluginManager` (auto_validate gate before loading)

## Navigation

- **Parent**: [plugin_system](../AGENTS.md)
- **Root**: [../../../../README.md](../../../../README.md)

# Codomyrmex Agents — projects/test_project/config

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: January 2026

## Signposting

- **Parent**: [test_project/AGENTS.md](../AGENTS.md)
- **Self**: [config/AGENTS.md](AGENTS.md)
- **Children**: None
- **Key Artifacts**:
  - [settings.yaml](settings.yaml)
  - [modules.yaml](modules.yaml)
  - [workflows.yaml](workflows.yaml)

## Purpose

Configuration directory containing YAML files that control test_project behavior. Demonstrates integration with `codomyrmex.config_management` and `codomyrmex.orchestrator` modules.

## Active Components

| File | Purpose | Codomyrmex Module |
| :--- | :--- | :--- |
| `settings.yaml` | Core project settings | `config_management` |
| `modules.yaml` | Module enablement | `config_management` |
| `workflows.yaml` | Workflow definitions | `orchestrator` |

## Operating Contracts

### Configuration Standards

1. **YAML Format**: All configuration uses YAML with proper structure
2. **Hierarchical Keys**: Use dot notation hierarchy (e.g., `project.name`)
3. **Default Values**: Always provide sensible defaults
4. **Documentation**: Comment non-obvious settings

### When Modifying Configuration

1. **Validate Schema**: Ensure YAML is valid before committing
2. **Test Impact**: Changes may affect multiple components
3. **Update Docs**: Update README if adding new settings
4. **Version Control**: Track configuration changes

### Configuration Loading Priority

1. Default values in code
2. `settings.yaml` base configuration
3. Environment-specific overrides
4. Runtime arguments

## Navigation Links

- **📁 Parent**: [../AGENTS.md](../AGENTS.md)
- **🏠 Project Root**: [../../README.md](../../README.md)

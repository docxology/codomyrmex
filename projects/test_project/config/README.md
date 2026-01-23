# config/

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: January 2026

## Overview

Configuration directory containing YAML configuration files for the test_project. These files demonstrate proper usage of the `codomyrmex.config_management` module for managing project settings, module enablement, and workflow definitions.

## Directory Contents

| File | Purpose | Module Integration |
| :--- | :--- | :--- |
| `settings.yaml` | Core project settings | `config_management` |
| `modules.yaml` | Module enablement configuration | `config_management` |
| `workflows.yaml` | Workflow/pipeline definitions | `orchestrator` |
| `README.md` | This documentation | - |
| `AGENTS.md` | Agent coordination | - |
| `SPEC.md` | Functional specification | - |
| `PAI.md` | Personal AI context | - |

## Configuration Files

### settings.yaml

Core project configuration including:

- Project metadata (name, version, environment)
- Logging settings (level, format, output)
- Analysis parameters (include/exclude patterns, complexity limits)
- Visualization options (theme, output formats)
- Reporting configuration (formats, styling)
- Data paths

### modules.yaml

Module management including:

- Enabled modules by layer (foundation, core, service, utility)
- Module-specific configuration overrides
- Dependency graph for validation

### workflows.yaml

Workflow definitions including:

- Analysis workflow (validate → analyze → report)
- Visualization workflow (load → charts → dashboard)
- Reporting workflow (validate → HTML → JSON)
- Full pipeline (complete end-to-end workflow)
- Execution settings and event hooks

## Usage

### Loading Configuration

```python
from pathlib import Path
from codomyrmex.config_management import ConfigManager

# Load settings
config = ConfigManager(Path("config/settings.yaml"))
project_name = config.get("project.name")
log_level = config.get("logging.level", default="INFO")
```

### Accessing Module Configuration

```python
import yaml
from pathlib import Path

# Load modules configuration
with open("config/modules.yaml") as f:
    modules = yaml.safe_load(f)

enabled_core = modules["enabled_modules"]["core"]
static_analysis_config = modules["module_overrides"]["static_analysis"]
```

## Navigation

- **Parent**: [../README.md](../README.md)
- **Project Root**: [../../README.md](../../README.md)

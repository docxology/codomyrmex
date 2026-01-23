# Personal AI Infrastructure - Config Context

**Directory**: `projects/test_project/config/`
**Status**: Active

## Overview

Configuration layer demonstrating YAML-based configuration management with codomyrmex integration.

## AI Context

### Key Files

| File | Read | Write | Purpose |
| :--- | :---: | :---: | :--- |
| `settings.yaml` | ✓ | ✓ | Core settings |
| `modules.yaml` | ✓ | Rare | Module enablement |
| `workflows.yaml` | ✓ | ✓ | Workflow definitions |

### Common Modifications

1. **Change log level**: Edit `logging.level` in `settings.yaml`
2. **Enable module**: Add to `enabled_modules` in `modules.yaml`
3. **Add workflow step**: Add step to workflow in `workflows.yaml`

### Configuration Loading Pattern

```python
from codomyrmex.config_management import ConfigManager
from pathlib import Path

config = ConfigManager(Path("config/settings.yaml"))
```

## Navigation

- **Parent**: [../PAI.md](../PAI.md)
- **Parent Dir**: [../README.md](../README.md)

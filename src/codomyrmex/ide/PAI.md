# Personal AI Infrastructure — IDE Module

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

The IDE module provides PAI integration for programmatic IDE control, enabling AI agents to interact with development environments.

## PAI Capabilities

### IDE Integration

Control IDEs programmatically:

```python
from codomyrmex.ide import CursorClient, IDECommand

client = CursorClient()
client.connect()

# Execute IDE commands
result = client.execute(IDECommand.OPEN_FILE, path="src/main.py")

# Get open files
files = client.list_open_files()
```

### Multi-IDE Support

Work across different IDEs:

```python
from codomyrmex.ide import IDEManager

manager = IDEManager()
ides = manager.discover()  # Find running IDEs

for ide in ides:
    print(f"{ide.name}: {ide.workspace}")
```

## PAI Integration Points

| Component | PAI Use Case |
|-----------|-------------|
| `CursorClient` | Cursor AI integration |
| `IDECommand` | Execute IDE actions |
| `IDEManager` | Multi-IDE management |

## Navigation

- [README](README.md) | [AGENTS](AGENTS.md) | [SPEC](SPEC.md)

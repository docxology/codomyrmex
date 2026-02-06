# Personal AI Infrastructure — Coding Module

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

The Coding module provides PAI integration for code generation and editing.

## PAI Capabilities

### Code Generation

Generate code:

```python
from codomyrmex.coding import CodeGenerator

generator = CodeGenerator()
code = generator.generate_function(
    name="greet", params=["name"], return_type="str"
)
```

### Code Editing

Edit existing code:

```python
from codomyrmex.coding import CodeEditor

editor = CodeEditor("src/main.py")
editor.add_import("from datetime import datetime")
editor.save()
```

## PAI Integration Points

| Component | PAI Use Case |
|-----------|-------------|
| `CodeGenerator` | Generate code |
| `CodeEditor` | Modify code |
| `DiffApplier` | Apply diffs |

## Navigation

- [README](README.md) | [AGENTS](AGENTS.md) | [SPEC](SPEC.md)

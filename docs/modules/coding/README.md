# Coding Module Documentation

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

Code generation, editing, and transformation utilities with AST-based operations.

## Key Features

- **Generation** — Generate code from specs
- **Editing** — Safe AST-based edits
- **Transformation** — Refactoring operations
- **Diff** — Apply code diffs

## Quick Start

```python
from codomyrmex.coding import CodeGenerator, CodeEditor

generator = CodeGenerator()
code = generator.generate_function(
    name="hello", params=["name"], return_type="str"
)

editor = CodeEditor("src/main.py")
editor.add_import("from datetime import datetime")
editor.save()
```

## Directory Contents

| File | Description |
|------|-------------|
| `README.md` | This file |
| `SPEC.md` | Technical specification |

## Navigation

- **Source**: [src/codomyrmex/coding/](../../../src/codomyrmex/coding/)
- **Parent**: [Modules](../README.md)

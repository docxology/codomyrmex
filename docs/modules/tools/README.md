# Tools Module Documentation

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

External tool integration and management for running linters, formatters, and other development tools.

## Key Features

- **Discovery** — Find available tools
- **Execution** — Run tools with args
- **Version Check** — Verify tool versions
- **Output Parsing** — Structure tool output

## Quick Start

```python
from codomyrmex.tools import ToolRegistry, ToolRunner

registry = ToolRegistry()
available = registry.discover()

runner = ToolRunner()
result = runner.run("ruff", ["check", "src/"])
print(result.stdout)
```

## Directory Contents

| File | Description |
|------|-------------|
| `README.md` | This file |
| `SPEC.md` | Technical specification |

## Navigation

- **Source**: [src/codomyrmex/tools/](../../../src/codomyrmex/tools/)
- **Parent**: [Modules](../README.md)

# CLI Handler Framework

**Module**: `codomyrmex.agents.cli` | **Category**: Infrastructure | **Last Updated**: March 2026

## Overview

Common CLI handler framework shared by all CLI-based agents. Provides subprocess management, output parsing, timeout handling, and structured response extraction.

## Key Classes

| Class | Purpose |
|:---|:---|
| `CLIHandler` | Generic subprocess wrapper for CLI agents |
| `CLIConfig` | CLI execution configuration |

## Usage

```python
from codomyrmex.agents.cli import CLIHandler

client = CLIHandler()
```

## Source Module

Source: [`src/codomyrmex/agents/cli/`](../../../src/codomyrmex/agents/cli/)

## Navigation

- **Parent**: [docs/agents/](../README.md)
- **Source**: [src/codomyrmex/agents/cli/](../../../src/codomyrmex/agents/cli/)
- **Project Root**: [README.md](../../../README.md)

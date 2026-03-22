# Paperclip Agent

**Module**: `codomyrmex.agents.paperclip` | **Category**: CLI Client | **Last Updated**: March 2026

## Overview

Integration with [Paperclip](https://github.com/paperclipai/paperclip) — a zero-human company orchestration platform that enables autonomous agent workflows.

## Key Classes

| Class | Purpose |
|:---|:---|
| `PaperclipClient` | CLI client for Paperclip orchestration |
| `PaperclipAPIClient` | REST API client for Paperclip cloud |
| `PaperclipIntegrationAdapter` | Codomyrmex integration layer |

## Usage

```python
from codomyrmex.agents.paperclip import PaperclipClient

client = PaperclipClient()
```

## Requirements

- Paperclip CLI installed (`npm install -g paperclip`)
- Optional: Paperclip cloud account for API access

## Source Module

Source: [`src/codomyrmex/agents/paperclip/`](../../../../src/codomyrmex/agents/paperclip/)

## Navigation

- **Parent**: [docs/agents/](../README.md)
- **Source**: [src/codomyrmex/agents/paperclip/](../../../../src/codomyrmex/agents/paperclip/)
- **Project Root**: [README.md](../../../README.md)
# Relations Module Documentation

**Version**: v0.1.7 | **Status**: Active | **Last Updated**: February 2026

## Overview

Social relationship management and external communication engine. Integrates CRM capabilities, social media management, and network analysis.

## Installation

```bash
uv pip install codomyrmex
```

## Key Features

- **`Contact`** -- External entity representation for relationship tracking.
- **`Interaction`** -- Record of communication events.
- **`Deal`** -- Business opportunity tracking.

## Submodules

| Submodule | Description |
|-----------|-------------|
| `crm` | Contact management |
| `social_media` | Platform integration |
| `network_analysis` | Social graph processing |

## Quick Start

```python
from codomyrmex.relations import Contact

contact = Contact(name="Jane Doe", email="jane@example.com")
contact.log(Interaction(type="email", summary="Introductory call"))
```

## API Reference

### Classes

| Class | Description |
|-------|-------------|
| `Contact` | External entity representation |
| `Interaction` | Record of communication |
| `Deal` | Business opportunity tracking |

## Directory Contents

| File | Description |
|------|-------------|
| `README.md` | This documentation |
| `AGENTS.md` | Agent coordination guide |
| `SPEC.md` | Technical specification |

## Testing

```bash
uv run python -m pytest src/codomyrmex/tests/ -k relations -v
```

## Navigation

- **Source**: [src/codomyrmex/relations/](../../../src/codomyrmex/relations/)
- **API Spec**: [API_SPECIFICATION.md](../../../src/codomyrmex/relations/API_SPECIFICATION.md)
- **MCP Spec**: [MCP_TOOL_SPECIFICATION.md](../../../src/codomyrmex/relations/MCP_TOOL_SPECIFICATION.md)
- **Parent**: [Modules](../README.md)

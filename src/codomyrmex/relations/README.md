# Relations Module

**Version**: v0.1.7 | **Status**: Active | **Last Updated**: February 2026

## Overview

Social relationship management and external communication engine. Integrates CRM capabilities, social media management, and network analysis.

## Installation

```bash
uv add codomyrmex
```

## Key Exports

### CRM

- **`Contact`** — External entity representation
- **`Interaction`** — Record of communication
- **`Deal`** — Business opportunity tracking

### UOR (Universal Object Reference)

- **`PrismEngine`** — PRISM triadic coordinate engine
- **`UOREntity`** — Content-addressed entity with structural identity
- **`EntityManager`** — Entity CRUD + similarity search
- **`UORGraph`** — Content-addressed relationship graph

### Submodules

- `crm/` — Contact management
- `social_media/` — Platform integration
- `network_analysis/` — Social graph processing
- `uor/` — Universal Object Reference (PRISM coordinates, content-addressed entities)

## Quick Start

```python
from codomyrmex.relations import Contact, Interaction

contact = Contact(name="Jane Doe", email="jane@example.com")
contact.log(Interaction(type="email", summary="Introductory call"))
```

## Navigation

- [SPEC](SPEC.md) | [AGENTS](AGENTS.md) | [Parent](../README.md)

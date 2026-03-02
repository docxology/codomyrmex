# Relations Module

**Version**: v1.0.5 | **Status**: Active | **Last Updated**: March 2026

## Overview

The Relations module provides CRM (Contact Relationship Management), social network analysis, and Universal Object Reference (UOR) capabilities. It enables agents to track contacts, analyze social graphs, and maintain bidirectional entity relationships.

## PAI Integration

| Algorithm Phase | Role | Tools Used |
|----------------|------|-----------|
| **OBSERVE** | Score relationship strength between entities in the knowledge graph | `relations_score_strength` |
| **THINK** | Use relationship strengths to weight context retrieval | `relations_score_strength` |

PAI uses `relations_score_strength` to compute relevance between entities (modules, agents, tasks) during OBSERVE and THINK. This informs capability selection by weighting related prior decisions more heavily.

## Installation

```bash
uv add codomyrmex
```

## Key Exports

### CRM

| Export | Type | Purpose |
|--------|------|---------|
| `Contact` | Class | Contact record with metadata |
| `ContactManager` | Class | Contact CRUD and search |
| `Interaction` | Class | Tracked interaction with a contact |

### Network Analysis

| Export | Type | Purpose |
|--------|------|---------|
| `SocialGraph` | Class | Social relationship graph |
| `GraphMetrics` | Class | Centrality, clustering, connectivity metrics |

### Universal Object Reference (UOR)

| Export | Type | Purpose |
|--------|------|---------|
| UOR types | Various | Bidirectional entity references across modules |

## Quick Start

```python
from codomyrmex.relations import Contact, ContactManager, SocialGraph, GraphMetrics

# Contact management
manager = ContactManager()
contact = Contact(name="Alice", role="developer")
manager.add(contact)

# Social graph analysis
graph = SocialGraph()
graph.add_relationship(contact_a, contact_b, type="collaborator")
metrics = GraphMetrics(graph)
print(metrics.centrality())
```

## Architecture

```
relations/
├── __init__.py          # All exports
├── crm.py               # Contact, ContactManager, Interaction
├── network_analysis.py  # SocialGraph, GraphMetrics
├── uor.py               # Universal Object Reference
└── tests/               # Zero-Mock tests
```

## Navigation

- **Extended Docs**: [docs/modules/relations/](../../../docs/modules/relations/)
- [SPEC.md](SPEC.md) | [AGENTS.md](AGENTS.md) | [PAI.md](PAI.md) | [Parent](../README.md)

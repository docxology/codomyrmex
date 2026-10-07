# Personal AI Infrastructure -- Relations Module

**Version**: v1.3.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

The Relations module is the **social relationship management engine** for the Codomyrmex ecosystem. It provides CRM capabilities including contact management with tagging, interaction history logging across communication channels (email, call, meeting, note), search, and social graph summaries.

## PAI Capabilities

### Contact Management

Create contacts and log interactions:

```python
from codomyrmex.relations.crm import ContactManager

crm = ContactManager()
contact = crm.add_contact("Jane Doe", "jane@example.com", tags=["partner"])
crm.add_interaction(contact.id, type="email", notes="Initial outreach")

results = crm.search_contacts("jane")  # Case-insensitive search by name, email or tag
```

### Social Graph Visualization

Build a graph definition of the contact network:

```python
from codomyrmex.relations.visualization import render_social_graph

graph = render_social_graph(crm)
# Returns {"title": ..., "node_count": ..., "nodes": [...]} with one node per contact
```

## Key Exports

| Export | Type | Purpose |
| --- | --- | --- |
| `Contact` | Dataclass | External entity with name, email, tags, metadata, and interaction history |
| `Interaction` | Dataclass | Record of a communication event with type (e.g. `"email"`), notes, and timestamp |
| `ContactManager` | Class | Contact storage engine with tagging, interaction logging, and search |
| `visualization.render_social_graph()` | Function | Graph definition (nodes per contact) of the social network |

## PAI Algorithm Phase Mapping

| Phase | Relations Module Contribution |
| --- | --- |
| **OBSERVE** | Interaction history provides observability into communication patterns |
| **PLAN** | Contact tags and search help identify stakeholders for planning |
| **EXECUTE** | `add_interaction()` records communication events during execution |
| **VERIFY** | Social graph summaries verify relationship network topology |
| **LEARN** | Interaction history and tagging patterns support relationship analytics |

## Architecture Role

**Application Layer** -- Domain-specific CRM module. Renders its own graph summaries in `relations.visualization` (no dependency on `data_visualization`). Has no upward dependencies from other modules.

## Navigation

- **Self**: [PAI.md](PAI.md)
- **Parent**: [../PAI.md](../PAI.md) -- Source-level PAI module map
- **Root Bridge**: [../../../PAI.md](../../../PAI.md) -- Authoritative PAI system bridge doc
- **Siblings**: [README.md](README.md) | [AGENTS.md](AGENTS.md) | [SPEC.md](SPEC.md) | [API_SPECIFICATION.md](API_SPECIFICATION.md)

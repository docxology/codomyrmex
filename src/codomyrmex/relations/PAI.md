# Personal AI Infrastructure -- Relations Module

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

The Relations module is the **social relationship management engine** for the Codomyrmex ecosystem. It provides CRM capabilities including contact management with tagging, interaction history logging across multiple communication channels (email, call, meeting, social media), search, and social graph visualization.

## PAI Capabilities

### Contact Management

Create contacts and log interactions:

```python
from codomyrmex.relations.crm import Contact, Interaction, InteractionType, CRM

crm = CRM()
contact = Contact(name="Jane Doe", email="jane@example.com")
contact.add_tag("partner")
contact.log_interaction(Interaction(type=InteractionType.EMAIL, summary="Initial outreach"))
crm.add_contact(contact)

results = crm.search("jane")  # Case-insensitive search by name or email
```

### Social Graph Visualization

Render contact networks as Mermaid diagrams:

```python
from codomyrmex.relations.visualization import render_social_graph

diagram = render_social_graph(crm)
# Returns MermaidDiagram with contact nodes
```

## Key Exports

| Export | Type | Purpose |
|--------|------|---------|
| `Contact` | Dataclass | External entity with name, email, phone, tags, and interaction history |
| `Interaction` | Dataclass | Record of a communication event with type, summary, and timestamp |
| `InteractionType` | Enum | Communication channels: EMAIL, CALL, MEETING, SOCIAL_MEDIA |
| `CRM` | Class | Contact storage engine with search and retrieval |
| `render_social_graph()` | Function | Mermaid diagram of the social contact network |

## PAI Algorithm Phase Mapping

| Phase | Relations Module Contribution |
|-------|------------------------------|
| **OBSERVE** | Interaction history provides observability into communication patterns |
| **PLAN** | Contact tags and search help identify stakeholders for planning |
| **EXECUTE** | `log_interaction()` records communication events during execution |
| **VERIFY** | Social graph visualization verifies relationship network topology |
| **LEARN** | Interaction history and tagging patterns support relationship analytics |

## MCP Tools

One tool is auto-discovered via `@mcp_tool` and available through the PAI MCP bridge:

| Tool | Description | Trust Level | Category |
|------|-------------|-------------|----------|
| `relations_score_strength` | Score the relationship strength between two entities given interaction history | Safe | relations |

## Architecture Role

**Application Layer** -- Domain-specific CRM module. Depends on the `visualization` module for Mermaid diagram rendering. Has no upward dependencies from other modules.

## Navigation

- **Self**: [PAI.md](PAI.md)
- **Parent**: [../PAI.md](../PAI.md) -- Source-level PAI module map
- **Root Bridge**: [../../../PAI.md](../../../PAI.md) -- Authoritative PAI system bridge doc
- **Siblings**: [README.md](README.md) | [AGENTS.md](AGENTS.md) | [SPEC.md](SPEC.md) | [API_SPECIFICATION.md](API_SPECIFICATION.md)

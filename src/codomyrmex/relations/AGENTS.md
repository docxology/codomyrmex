# Agent Instructions for `codomyrmex.relations`

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

## Context

The Relations module provides CRM (Contact Relationship Management), social network analysis, and Universal Object Reference (UOR) capabilities for tracking entities and their relationships.

## Usage Guidelines

1. **Importing**: Import from the module root.

   ```python
   from codomyrmex.relations import Contact, ContactManager, Interaction, SocialGraph, GraphMetrics
   ```

2. **Contact Management**: Use `ContactManager` for all CRUD operations. Always record `Interaction` events when engaging with contacts.

3. **Social Graph**: Use `SocialGraph` for modeling entity relationships. `GraphMetrics` provides centrality, clustering, and connectivity analysis.

4. **UOR**: Universal Object References enable bidirectional linking between entities across different modules (contacts ↔ projects, projects ↔ tasks).

5. **Zero-Mock Policy**: Tests must use real `ContactManager` instances — no mocking of storage or graph operations.

## Key Files

| File | Purpose |
|------|---------|
| `crm.py` | Contact, ContactManager, Interaction |
| `network_analysis.py` | SocialGraph, GraphMetrics |
| `uor.py` | Universal Object Reference |

## Navigation

- [README.md](README.md) | [SPEC.md](SPEC.md) | [PAI.md](PAI.md) | [Parent](../AGENTS.md)

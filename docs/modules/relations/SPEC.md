# Relations — Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

## Purpose

CRM, social network analysis, and Universal Object Reference (UOR) for tracking entities and their relationships.

## Functional Requirements

### CRM

| Interface | Signature | Description |
|-----------|-----------|-------------|
| `Contact(name, role, ...)` | Constructor | Create contact record |
| `ContactManager.add(contact)` | `→ None` | Add contact to store |
| `ContactManager.search(query)` | `→ list[Contact]` | Search contacts |
| `Interaction(contact, type, timestamp)` | Constructor | Record interaction event |

### Network Analysis

| Interface | Signature | Description |
|-----------|-----------|-------------|
| `SocialGraph()` | Constructor | Create empty social graph |
| `graph.add_relationship(a, b, type)` | `→ None` | Add relationship edge |
| `GraphMetrics(graph)` | Constructor | Compute graph metrics |
| `metrics.centrality()` | `→ dict[str, float]` | Node centrality scores |

### UOR

- Bidirectional entity references across module boundaries
- Supports Contact ↔ Project, Project ↔ Task linking

## Navigation

- [README.md](README.md) | [AGENTS.md](AGENTS.md) | [PAI.md](PAI.md) | [Parent](../SPEC.md)

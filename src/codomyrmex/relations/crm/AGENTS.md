# CRM Agentic Context

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose

Contact relationship management with tagging, interaction history, and search. Agents use this submodule to track contacts and their interactions over time.

## Key Components

| Component | Type | Role |
|-----------|------|------|
| `ContactManager` | Class | Central registry -- add, remove, search, tag contacts |
| `Contact` | Dataclass | Name, email, company, tags, metadata, timestamps |
| `Interaction` | Dataclass | Type (email/meeting/call/note), summary, timestamp per contact |

## Operating Contracts

- `add_contact(name, email, ...)` returns a `Contact` with a generated UUID.
- `search(query)` performs case-insensitive substring match on name and email.
- `add_tag` / `remove_tag` mutate the contact's tag set in place.
- `add_interaction(contact_id, interaction_type, summary)` appends to the contact's history list.
- `get_interactions(contact_id)` returns interactions newest-first by default.
- Contact IDs are `uuid4` strings; passing an unknown ID raises `KeyError`.

## Integration Points

- Parent module `relations` provides `relations_score_strength` MCP tool.
- Uses `logging_monitoring.get_logger` for structured logging.

## Navigation

- [README.md](README.md) | [SPEC.md](SPEC.md) | [PAI.md](PAI.md)
- Parent: [relations](../README.md)

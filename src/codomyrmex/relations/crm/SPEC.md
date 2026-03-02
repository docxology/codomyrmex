# CRM -- Technical Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Lightweight contact relationship manager providing CRUD operations, tagging, and interaction tracking. All data is held in-memory via Python dicts and lists.

## Architecture

```
ContactManager (dict[str, Contact])
  +-- add_contact() -> Contact
  +-- get_contact() -> Contact
  +-- remove_contact()
  +-- search(query) -> list[Contact]
  +-- add_tag() / remove_tag()
  +-- add_interaction() -> Interaction
  +-- get_interactions() -> list[Interaction]
```

## Key Classes

### Contact

| Field | Type | Notes |
|-------|------|-------|
| `id` | `str` | UUID4, auto-generated |
| `name` | `str` | Required |
| `email` | `str` | Required |
| `company` | `str` | Optional, defaults `""` |
| `tags` | `set[str]` | Mutable tag collection |
| `metadata` | `dict` | Arbitrary key-value pairs |
| `created_at` | `datetime` | Set on creation |
| `updated_at` | `datetime` | Set on creation, not auto-updated |

### ContactManager Methods

| Method | Returns | Description |
|--------|---------|-------------|
| `add_contact(name, email, company, tags, metadata)` | `Contact` | Create and store a new contact |
| `get_contact(contact_id)` | `Contact` | Lookup by ID; raises `KeyError` |
| `remove_contact(contact_id)` | `None` | Delete by ID; raises `KeyError` |
| `search(query)` | `list[Contact]` | Case-insensitive substring on name/email |
| `add_tag(contact_id, tag)` | `None` | Add tag to contact's tag set |
| `remove_tag(contact_id, tag)` | `None` | Remove tag; raises `KeyError` if absent |
| `add_interaction(contact_id, type, summary)` | `Interaction` | Append timestamped interaction |
| `get_interactions(contact_id, sort_desc)` | `list[Interaction]` | Retrieve sorted interaction history |

## Dependencies

- `uuid`, `datetime` (stdlib)
- `codomyrmex.logging_monitoring`

## Constraints

- In-memory only -- no persistence layer.
- No validation on email format.

## Navigation

- [README.md](README.md) | [AGENTS.md](AGENTS.md) | [PAI.md](PAI.md)
- Parent: [relations](../README.md)

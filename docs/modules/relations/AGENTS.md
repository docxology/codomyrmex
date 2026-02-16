# Relations Module — Agent Coordination

## Purpose

Relations Module for Codomyrmex.

Provides CRM contact management, social network analysis,
and graph metrics.

## Key Capabilities

- **`Contact`** — External entity representation
- **`Interaction`** — Record of communication
- **`Deal`** — Business opportunity tracking
- `crm/` — Contact management
- `social_media/` — Platform integration
- `network_analysis/` — Social graph processing

## Agent Usage Patterns

```python
from codomyrmex.relations import Contact, Interaction

contact = Contact(name="Jane Doe", email="jane@example.com")
contact.log(Interaction(type="email", summary="Introductory call"))
```

## Key Components

| Export | Type |
|--------|------|
| `Contact` | Public API |
| `ContactManager` | Public API |
| `GraphMetrics` | Public API |
| `Interaction` | Public API |
| `SocialGraph` | Public API |

## Source Files

| File | Description |
|------|-------------|
| `crm.py` | Record of a communication event. |
| `visualization.py` | Generates a mermaid diagram of social connections. |

## Submodules

- `crm/` — Crm
- `network_analysis/` — Network Analysis
- `social_media/` — Social Media

## Integration Points

- **Source**: [src/codomyrmex/relations/](../../../src/codomyrmex/relations/)
- **Spec**: [SPEC.md](SPEC.md)
- **PAI**: [PAI.md](PAI.md)

## Testing Guidelines

```bash
uv run python -m pytest src/codomyrmex/tests/ -k relations -v
```

- Always use real, functional tests — no mocks (Zero-Mock policy)
- Verify all changes pass existing tests before submitting

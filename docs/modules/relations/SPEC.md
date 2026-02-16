# Relations — Functional Specification

**Module**: `codomyrmex.relations`  
**Version**: v0.1.0  
**Status**: Active

## 1. Overview

Relations Module for Codomyrmex.

Provides CRM contact management, social network analysis,
and graph metrics.

## 2. Architecture

### Source Files

| File | Purpose |
|------|--------|
| `crm.py` | Record of a communication event. |
| `visualization.py` | Generates a mermaid diagram of social connections. |

### Submodule Structure

- `crm/` — Crm
- `network_analysis/` — Network Analysis
- `social_media/` — Social Media

## 3. Dependencies

No internal Codomyrmex dependencies.

## 4. Public API

### Exports (`__all__`)

- `Contact`
- `ContactManager`
- `GraphMetrics`
- `Interaction`
- `SocialGraph`

## 5. Testing

```bash
uv run python -m pytest src/codomyrmex/tests/ -k relations -v
```

All tests follow the Zero-Mock policy.

## 6. References

- [README.md](README.md) — Human-readable documentation
- [AGENTS.md](AGENTS.md) — Agent coordination guide
- [Source Code](../../../src/codomyrmex/relations/)

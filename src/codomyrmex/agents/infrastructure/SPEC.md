# Infrastructure — Functional Specification

**Module**: `codomyrmex.agents.infrastructure`
**Status**: Active

## 1. Overview

Infrastructure agent for cloud operations.

## 2. Architecture

### Components

| Component | Type | Description |
|-----------|------|-------------|
| `InfrastructureAgent` | Class | Agent specialized for cloud infrastructure operations. |
| `Tool` | Class | Lightweight tool descriptor for agent registries. |
| `CloudToolFactory` | Class | Generates Tool objects from cloud client methods. |

## 3. API Usage

```python
from codomyrmex.agents.infrastructure import InfrastructureAgent
```

## 4. Dependencies

See `src/codomyrmex/agents/infrastructure/__init__.py` for import dependencies.

## 5. Testing

```bash
uv run python -m pytest src/codomyrmex/tests/ -k infrastructure -v
```

## References

- [README.md](README.md)
- [AGENTS.md](AGENTS.md)
- [Parent: Agents](../SPEC.md)

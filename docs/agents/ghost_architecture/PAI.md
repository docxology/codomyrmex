# Ghost Architecture — PAI Bridge

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

This document describes how the `ghost_architecture` submodule integrates with the Codomyrmex Personal AI Infrastructure (PAI).

---

## Module Role in PAI

The Ghost Architecture is a **research prototype** module within the `agents/` layer. It provides a continual-learning transformer that can be used as a foundation for any agent requiring compositional task transfer without forgetting.

| PAI Integration Point | Status |
|---|---|
| Git submodule tracked in `.gitmodules` | ✅ Active |
| Zero-Mock test suite (18 tests) | ✅ Active |
| `docs/agents/ghost_architecture/` documentation | ✅ Active |
| MCP tool exposure | ⬜ Planned |
| Codomyrmex `__init__.py` package export | ⬜ Planned |
| Telemetry / event emission | ⬜ Planned |

---

## Consumption Pattern

```python
import sys, os
sys.path.insert(0, 'src/codomyrmex/agents/ghost_architecture')
from config import GhostConfig
from model import GhostTransformer

config = GhostConfig(prime=97, operations=['add'], num_modules=40)
model = GhostTransformer(config)
logits = model(x, task='add')
```

---

## Agent Operational Guidelines

1. **Configuration first** — never instantiate the model with hard-coded values; always use `GhostConfig`.
2. **Continual extension** — use `model.add_head('new_task')` + `model.freeze_task_head('old_task')` to grow without forgetting.
3. **Checkpoint safety** — always use `GhostTransformer.load_with_migration()` to load checkpoints.
4. **No mock testing** — run all tests with real `torch.Tensor` inputs on CPU.

---

## Planned MCP Tool Exposure

When productized, the following tools are candidates for MCP exposure:

| Proposed Tool | Description |
|---|---|
| `ghost_forward` | Run a single forward pass and return logits + routing info |
| `ghost_add_task` | Register a new task head at runtime |
| `ghost_load_checkpoint` | Load and migrate a checkpoint from disk |

---

## Navigation

- **Source SPEC.md**: [SPEC.md](../../../src/codomyrmex/agents/ghost_architecture/SPEC.md)
- **Source PAI.md**: [PAI.md](../../../src/codomyrmex/agents/ghost_architecture/PAI.md)
- **Docs README**: [README.md](README.md)
- **Parent PAI.md**: [docs/agents/PAI.md](../PAI.md)

# Ghost Architecture — Functional Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

This is the documentation-layer SPEC for `ghost_architecture`. For the authoritative technical specification see the source-level [`SPEC.md`](../../../src/codomyrmex/agents/ghost_architecture/SPEC.md).

---

## Overview

The Ghost Architecture is a modular continual-learning transformer that:

- Prevents catastrophic forgetting via **per-task positional embeddings**
- Uses a **frozen Fourier manifold** as the shared deterministic embedding
- Crystallizes trained modules into **frozen "ghosts"** usable by future tasks
- Routes inputs via **sparse top-K signature matching** — a lightweight thalamus

---

## Quick Reference

| Property | Value |
|---|---|
| Default `num_modules` | 40 |
| Default `hidden_dim` | 64 |
| Default `num_heads` | 2 |
| Default `num_layers` | 2 |
| Default `top_k` | 6 |
| Default `vocab_size` / `num_classes` | 97 (prime) |
| Checkpoint migration | Automatic via `load_with_migration()` |

---

## Component Summary

| Component | File | Role |
|---|---|---|
| `GhostTransformer` | `model.py` | Full model: embed → route → fuse → classify |
| `Router` | `router.py` | Top-K signature-based routing |
| `NeuromodulationState` | `router.py` | Dopamine-inspired adaptive exploration |
| `ModuleBank` | `module_bank.py` | Parallel module execution + fusion |
| `TransformerModule` | `module.py` | Single 2-layer transformer unit |
| `GhostConfig` | `config.py` | Top-level hyperparameter container |

---

## Key Constraints & Invariants

- `top_k ≤ num_modules` (enforced by `__post_init__`)
- `hidden_dim % num_heads == 0` (enforced by `__post_init__`)
- No shared trainable weights across tasks
- `tok_emb` is frozen after manifold pre-training
- Crystallized modules cannot be unfrozen (gradient hooks)

---

## Test Suite

All 18 tests are in [`src/codomyrmex/tests/agents/test_ghost_architecture.py`](../../../src/codomyrmex/tests/agents/test_ghost_architecture.py).

```bash
uv run pytest src/codomyrmex/tests/agents/test_ghost_architecture.py -v
# 18 passed
```

See the [source SPEC.md](../../../src/codomyrmex/agents/ghost_architecture/SPEC.md) for the full test coverage table.

---

## Navigation

- **Source SPEC.md**: [`src/codomyrmex/agents/ghost_architecture/SPEC.md`](../../../src/codomyrmex/agents/ghost_architecture/SPEC.md)
- **Source PAI.md**: [`src/codomyrmex/agents/ghost_architecture/PAI.md`](../../../src/codomyrmex/agents/ghost_architecture/PAI.md)
- **Full README**: [`README.md`](README.md)
- **Parent Docs**: [`docs/agents/SPEC.md`](../SPEC.md)

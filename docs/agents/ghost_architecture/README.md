# Ghost Architecture — docs/agents/ghost_architecture/

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

The [Ghost Architecture](../../../src/codomyrmex/agents/ghost_architecture/) is a modular continual-learning transformer where frozen (crystallized) modules from prior tasks act as callable "ghost" primitives. New tasks are solved by routing through this shared bank, without catastrophic forgetting.

Forked from [modular-crystallizing-transformer](https://github.com/B-Smith-92/modular-crystallizing-transformer) with one key improvement: **per-task positional embeddings** that eliminate the forgetting vector.

---

## Architecture

```
Input (a, b)
    ↓
┌─────────────────────────────────┐
│  FROZEN FOURIER MANIFOLD        │
│  tok_emb: DFT of Z/pZ          │
│  Shared, deterministic, frozen  │
└─────────────────────────────────┘
    ↓
┌─────────────────────────────────┐
│  PER-TASK ROUTING               │
│  pos_embs[task]  ← THE FIX     │
│  task_emb, sig_proj, route_proj │
│  Top-K sparse selection         │
└─────────────────────────────────┘
    ↓
┌─────────────────────────────────┐
│  MODULE BANK (40 modules)       │
│  2-layer transformers, dim 64   │
│  Crystallized = frozen "ghosts" │
└─────────────────────────────────┘
    ↓
┌─────────────────────────────────┐
│  PER-TASK OUTPUT                │
│  fusion_proj → head → logits    │
└─────────────────────────────────┘
```

### Component Isolation Table

| Component | Scope |
|-----------|-------|
| `tok_emb` | Shared but **frozen** (Fourier manifold) |
| `pos_embs[task]` | **Per-task** (the core fix) |
| `sig_projs[task]` | Per-task |
| `route_projs[task]` | Per-task |
| `fusion_projs[task]` | Per-task |
| `heads[task]` | Per-task |
| `task_emb` | Per-task (gradient hooks zero frozen rows) |
| Module bank | Shared, but crystallized modules are **frozen** |

---

## Source Files

| File | Purpose |
|------|---------|
| [`config.py`](../../../src/codomyrmex/agents/ghost_architecture/config.py) | All hyperparameters as dataclasses |
| [`model.py`](../../../src/codomyrmex/agents/ghost_architecture/model.py) | `GhostTransformer` — full model with per-task `pos_embs` |
| [`module.py`](../../../src/codomyrmex/agents/ghost_architecture/module.py) | Single transformer module (2-layer, dim 64) |
| [`module_bank.py`](../../../src/codomyrmex/agents/ghost_architecture/module_bank.py) | Parallel module execution + weighted fusion |
| [`router.py`](../../../src/codomyrmex/agents/ghost_architecture/router.py) | Signature-based routing + neuromodulation |
| [`train_manifold.py`](../../../src/codomyrmex/agents/ghost_architecture/train_manifold.py) | Fourier embedding initialization |
| [`train.py`](../../../src/codomyrmex/agents/ghost_architecture/train.py) | Single-operation training with grok detection + crystallization |
| [`train_continual.py`](../../../src/codomyrmex/agents/ghost_architecture/train_continual.py) | Continual learning with multi-timescale dynamics |
| [`visualize.py`](../../../src/codomyrmex/agents/ghost_architecture/visualize.py) | Training curves, module heatmaps, embedding geometry |
| [`visualize_architecture.py`](../../../src/codomyrmex/agents/ghost_architecture/visualize_architecture.py) | Architecture diagrams |
| [`sweep.py`](../../../src/codomyrmex/agents/ghost_architecture/sweep.py) | Systematic multi-seed evaluation |
| [`run_overnight.py`](../../../src/codomyrmex/agents/ghost_architecture/run_overnight.py) | Full pipeline: standalone → transfer → cross-training |

---

## Configuration

All configuration lives in [`config.py`](../../../src/codomyrmex/agents/ghost_architecture/config.py) as dataclasses:

| Config Class | Purpose |
|---|---|
| `GhostConfig` | Top-level: module bank, routing, crystallization, neuromodulation |
| `ModuleConfig` | Single module dimensions: `hidden_dim=64`, `num_heads=2`, `num_layers=2` |
| `RouterConfig` | Signature routing: `top_k=6`, `temperature=1.0`, `signature_dim=32` |
| `CrystallizationConfig` | Selective freezing after grokking |
| `NeuromodulationConfig` | Dopamine-inspired adaptive routing |
| `ManifoldConfig` | Fourier manifold pre-training |
| `TrainingConfig` | LR, batch size, eval intervals, grok detection threshold |

---

## Key API

### `GhostTransformer`

```python
from ghost_architecture.model import GhostTransformer
from ghost_architecture.config import GhostConfig

config = GhostConfig(
    prime=97,              # sets vocab_size=97, num_classes=97
    operations=['add'],
    num_modules=40,
)
model = GhostTransformer(config)
logits = model(x, task='add')          # (B, num_classes)
logits, info = model(x, task='add', return_routing=True)  # with routing details
```

### `model.add_head(task)` — Continual Learning

Register a new task head without training previous tasks:

```python
model.add_head('mul')
# train only mul-tagged parameters...
model.freeze_task_head('mul')  # crystallize when done
```

### `model.load_with_migration()` — Checkpoint Loading

```python
model = GhostTransformer.load_with_migration(config, 'runs/ghost_train/latest/model_final.pt')
```

---

## Training Pipeline

```bash
# 1. Fourier manifold (instant, deterministic)
python train_manifold.py --prime 97 --hidden_dim 64

# 2. Train addition (~9k epochs to grok)
python train.py --operation add \
  --manifold_embeddings ./runs/manifold_embeddings/latest/manifold_embeddings.pt

# 3. Train multiplication on top of addition (no forgetting)
python train_continual.py --operation mul --existing_ops add \
  --checkpoint ./runs/ghost_train/latest/model_final.pt \
  --manifold_embeddings ./runs/manifold_embeddings/latest/manifold_embeddings.pt

# 4. Full overnight evaluation (27 runs)
python run_overnight.py
```

---

## Testing

Tests are in [`src/codomyrmex/tests/agents/test_ghost_architecture.py`](../../../src/codomyrmex/tests/agents/test_ghost_architecture.py).

```bash
uv run pytest src/codomyrmex/tests/agents/test_ghost_architecture.py -v
```

| Test | Description |
|---|---|
| `test_ghost_config_defaults` | Validates default hyperparameter values |
| `test_ghost_transformer_instantiation` | Verifies per-task isolation: pos_embs, heads exist for each task |
| `test_ghost_forward_pass` | Real forward pass with synthetic inputs, checks output shape |
| `test_ghost_routing_info` | Validates routing info dict contains all expected keys |
| `test_ghost_add_head` | Dynamically adds a new task head after construction |
| `test_ghost_freeze_task_head` | Freezing a task head zeros its parameters' requires_grad |
| `test_ghost_continuous_learning` | Two tasks co-exist with no forgetting (shape regression test) |
| `test_neuromodulation_state` | NeuromodulationState update and bonus generation |

---

## Navigation

- **Source Code**: [`src/codomyrmex/agents/ghost_architecture/`](../../../src/codomyrmex/agents/ghost_architecture/)
- **Tests**: [`src/codomyrmex/tests/agents/test_ghost_architecture.py`](../../../src/codomyrmex/tests/agents/test_ghost_architecture.py)
- **Upstream**: [https://github.com/B-Smith-92/ghost-architecture](https://github.com/B-Smith-92/ghost-architecture)
- **Parent Index**: [docs/agents/README.md](../README.md)
- **Project Root**: [README.md](../../../README.md)

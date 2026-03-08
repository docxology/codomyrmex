# DPO Module

**Version**: v1.1.9 | **Status**: Active | **Last Updated**: March 2026

## Overview

The `dpo` module implements Direct Preference Optimization from Rafailov et al. (2023). DPO directly optimizes a language model policy from human preference pairs (winner vs loser responses) without fitting a separate reward model. The loss function uses the implicit reward defined as beta times the log-ratio between the policy and a frozen reference model. Pure Python and NumPy -- no PyTorch dependency.

## Architecture

The module is contained in a single `loss.py` file providing:

- **`compute_log_probs()`** -- per-token log probability extraction from logits
- **`compute_dpo_loss()`** -- the core DPO loss with implicit reward computation
- **`DPOLoss`** -- stateful wrapper with loss history tracking

The DPO loss formula is:

```
Loss = -log(sigmoid(beta * (reward_w - reward_l)))
where reward = beta * (log_pi(y|x) - log_ref(y|x))
```

## Key Exports

| Export | Module | Description |
|--------|--------|-------------|
| `DPOLoss` | `loss.py` | Stateful DPO loss with running history tracking |
| `compute_dpo_loss` | `loss.py` | Core DPO loss computation returning loss, rewards, accuracy |
| `compute_log_probs` | `loss.py` | Per-token log probabilities from logits with ignore_index support |

## Quick Start

```python
import numpy as np
from codomyrmex.dpo import compute_dpo_loss, DPOLoss

# Simulated log probabilities (batch=4)
policy_w = np.array([-1.2, -0.8, -1.5, -0.9])   # policy on winners
policy_l = np.array([-2.1, -1.9, -2.3, -1.8])   # policy on losers
ref_w = np.array([-1.3, -1.0, -1.4, -1.1])      # reference on winners
ref_l = np.array([-2.0, -1.8, -2.2, -1.7])      # reference on losers

result = compute_dpo_loss(policy_w, policy_l, ref_w, ref_l, beta=0.1)
print(f"DPO loss: {result['loss']:.4f}")
print(f"Accuracy: {result['accuracy']:.2%}")  # fraction where winner preferred

# Stateful usage with history
dpo = DPOLoss(beta=0.1)
result = dpo(policy_w, policy_l, ref_w, ref_l)
print(f"Loss history: {dpo.history}")
```

## Loss Output

The `compute_dpo_loss` function returns a dictionary with:

- `loss` -- scalar DPO loss value
- `rewards_w` -- implicit rewards for winning responses
- `rewards_l` -- implicit rewards for losing responses
- `accuracy` -- fraction where winner has higher implicit reward than loser
- `beta` -- KL penalty coefficient used

## MCP Tools

This module exposes MCP tools via `mcp_tools.py` and is auto-discovered by the PAI MCP bridge.

## PAI Integration

| Phase | Usage |
|-------|-------|
| BUILD | Alignment training without a reward model |
| VERIFY | Monitor preference accuracy during training |

## Testing

```bash
uv run pytest src/codomyrmex/tests/unit/dpo/ -v
```

## Module Files

| File | Purpose |
|------|---------|
| `__init__.py` | Public exports: DPOLoss, compute_dpo_loss, compute_log_probs |
| `loss.py` | DPO loss implementation with log-prob extraction |
| `mcp_tools.py` | MCP tool definitions for PAI bridge |

## Related Modules

- [distillation](../distillation/) -- Alternative model training via teacher-student
- [logit_processor](../logit_processor/) -- Sampling strategies for DPO-aligned models
- [slm](../slm/) -- Small language models that can be DPO-aligned

## Navigation

- **AGENTS**: [AGENTS.md](AGENTS.md)
- **SPEC**: [SPEC.md](SPEC.md)
- **Source**: [`src/codomyrmex/dpo/`](../../../src/codomyrmex/dpo/)
- **Parent**: [Module Documentation](../README.md)
- **Root**: [docs/](../../README.md)

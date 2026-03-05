# Softmax Optimization Module

**Version**: v1.1.4 | **Status**: Active | **Last Updated**: March 2026

## Overview

The `softmax_opt` module provides numerically stable and memory-efficient softmax implementations. It includes the standard max-subtraction softmax, a numerically precise log-softmax via the log-sum-exp trick, the online softmax algorithm used in Flash Attention (single-pass computation), and a safe softmax with epsilon-guarded denominator for masked attention. Pure Python and NumPy -- no PyTorch dependency.

## Architecture

The module is contained in `kernel.py` with four softmax variants:

- **`softmax()`** -- standard numerically stable softmax with temperature scaling
- **`log_softmax()`** -- log-sum-exp trick for precision in cross-entropy and KL divergence
- **`online_softmax()`** -- single-pass algorithm maintaining running (max, normalizer) statistics, the key insight behind Flash Attention's memory efficiency
- **`safe_softmax()`** -- epsilon-guarded denominator for attention masks with all-masked rows

## Key Exports

| Export | Module | Description |
|--------|--------|-------------|
| `softmax` | `kernel.py` | Numerically stable softmax with optional temperature scaling |
| `log_softmax` | `kernel.py` | Log-softmax via log-sum-exp trick (no precision loss) |
| `online_softmax` | `kernel.py` | Single-pass online algorithm (Flash Attention style) |
| `safe_softmax` | `kernel.py` | Epsilon-guarded softmax for masked attention |

## Quick Start

```python
import numpy as np
from codomyrmex.softmax_opt import softmax, log_softmax, online_softmax, safe_softmax

logits = np.random.randn(4, 1000)  # (batch, vocab_size)

# Standard softmax with temperature
probs = softmax(logits, temperature=0.8)
print(f"Sum: {probs.sum(axis=-1)}")  # [1.0, 1.0, 1.0, 1.0]

# Log-softmax for cross-entropy loss
log_probs = log_softmax(logits)
print(f"Max log prob: {log_probs.max():.4f}")  # <= 0

# Online softmax (single-pass, O(1) extra memory per row)
probs_online = online_softmax(logits)
print(f"Max diff from standard: {np.max(np.abs(probs - probs_online)):.2e}")

# Safe softmax for masked attention
masked_logits = np.full((4, 10), -1e9)  # all masked out
safe_probs = safe_softmax(masked_logits)  # no NaN/division-by-zero
```

## Algorithm Comparison

| Variant | Passes | Memory | Use Case |
|---------|--------|--------|----------|
| `softmax` | 2 (max, sum) | O(N) | General purpose |
| `log_softmax` | 2 (max, sum) | O(N) | Cross-entropy, KL divergence |
| `online_softmax` | 1 | O(1) per row | Flash Attention, streaming |
| `safe_softmax` | 2 (max, sum) | O(N) | Masked attention (prevents NaN) |

The online softmax maintains running max `m` and normalizer `d` in a single pass:
```
m_new = max(m, x_i)
d_new = d * exp(m - m_new) + exp(x_i - m_new)
```

## MCP Tools

This module exposes MCP tools via `mcp_tools.py` and is auto-discovered by the PAI MCP bridge.

## PAI Integration

| Phase | Usage |
|-------|-------|
| BUILD | Numerically stable probability computation in custom models |
| VERIFY | Compare softmax implementations for correctness and performance |

## Testing

```bash
uv run pytest src/codomyrmex/tests/unit/softmax_opt/ -v
```

## Module Files

| File | Purpose |
|------|---------|
| `__init__.py` | Public exports: softmax, log_softmax, online_softmax, safe_softmax |
| `kernel.py` | All four softmax implementations |
| `mcp_tools.py` | MCP tool definitions for PAI bridge |

## Related Modules

- [neural](../neural/) -- Transformer attention uses softmax extensively
- [matmul_kernel](../matmul_kernel/) -- Companion kernel optimization module
- [logit_processor](../logit_processor/) -- Uses softmax for probability computation
- [autograd](../autograd/) -- Autograd softmax with backward pass

## Navigation

- **AGENTS**: [AGENTS.md](AGENTS.md)
- **SPEC**: [SPEC.md](SPEC.md)
- **Source**: [`src/codomyrmex/softmax_opt/`](../../../src/codomyrmex/softmax_opt/)
- **Parent**: [Module Documentation](../README.md)
- **Root**: [docs/](../../README.md)

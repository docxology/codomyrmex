"""MCP tools for the Small Language Model module."""

from typing import Any

import numpy as np

from codomyrmex.model_context_protocol.decorators import mcp_tool


@mcp_tool(category="slm")
def slm_generate(
    prompt_tokens: list[int] | None = None,
    max_new_tokens: int = 10,
    vocab_size: int = 100,
    d_model: int = 32,
    n_heads: int = 2,
    n_layers: int = 1,
    seed: int = 42,
) -> dict[str, Any]:
    """Generate tokens from a tiny language model.

    Args:
        prompt_tokens: List of integer token IDs for the prompt (default: [1, 2, 3])
        max_new_tokens: Number of new tokens to generate
        vocab_size: Vocabulary size
        d_model: Model dimension
        n_heads: Number of attention heads
        n_layers: Number of transformer layers
        seed: Random seed for reproducibility

    Returns:
        dict with: prompt, generated, full_sequence, vocab_size, model_params
    """
    from .model import SLM, SLMConfig

    if prompt_tokens is None:
        prompt_tokens = [1, 2, 3]

    np.random.seed(seed)

    config = SLMConfig(
        vocab_size=vocab_size,
        d_model=d_model,
        n_heads=n_heads,
        n_layers=n_layers,
        d_ff=d_model * 4,
        max_seq_len=128,
    )
    model = SLM(config)
    full_seq = model.generate(prompt_tokens, max_new_tokens=max_new_tokens)

    return {
        "prompt": prompt_tokens,
        "generated": full_seq[len(prompt_tokens) :],
        "full_sequence": full_seq,
        "vocab_size": vocab_size,
        "model_params": {
            "d_model": d_model,
            "n_heads": n_heads,
            "n_layers": n_layers,
        },
        "status": "success",
    }


@mcp_tool(category="slm")
def slm_forward(
    batch_size: int = 1,
    seq_len: int = 8,
    vocab_size: int = 100,
    d_model: int = 32,
    n_heads: int = 2,
    n_layers: int = 1,
    seed: int = 42,
) -> dict[str, Any]:
    """Run a forward pass through the SLM and return logit statistics.

    Args:
        batch_size: Number of sequences in the batch
        seq_len: Length of each sequence
        vocab_size: Vocabulary size
        d_model: Model dimension
        n_heads: Number of attention heads
        n_layers: Number of transformer layers
        seed: Random seed for reproducibility

    Returns:
        dict with: output_shape, logit_mean, logit_std, logit_min, logit_max
    """
    from .model import SLM, SLMConfig

    np.random.seed(seed)

    config = SLMConfig(
        vocab_size=vocab_size,
        d_model=d_model,
        n_heads=n_heads,
        n_layers=n_layers,
        d_ff=d_model * 4,
        max_seq_len=128,
    )
    model = SLM(config)
    token_ids = np.random.randint(0, vocab_size, (batch_size, seq_len))
    logits = model.forward(token_ids)

    return {
        "output_shape": list(logits.shape),
        "logit_mean": float(np.mean(logits)),
        "logit_std": float(np.std(logits)),
        "logit_min": float(np.min(logits)),
        "logit_max": float(np.max(logits)),
        "status": "success",
    }

"""MCP tools for logit processing and token sampling."""

from __future__ import annotations

import numpy as np

from codomyrmex.model_context_protocol.decorators import mcp_tool

from .processor import greedy_decode, sample_token


@mcp_tool(category="logit_processor")
def process_logits(
    logits: list[float],
    temperature: float = 1.0,
    top_k: int = 0,
    top_p: float = 1.0,
    repetition_penalty: float = 1.0,
    previous_tokens: list[int] | None = None,
    seed: int | None = None,
) -> dict:
    """Apply sampling strategies to language model logits.

    Args:
        logits: Raw logit values from language model.
        temperature: Scaling factor (>1=diverse, <1=focused, 1=unchanged).
        top_k: Keep only top-k tokens (0=disabled).
        top_p: Nucleus sampling threshold (1.0=disabled).
        repetition_penalty: Penalize repeated tokens (1.0=disabled, >1.0=penalize).
        previous_tokens: Previously generated token IDs for repetition penalty.
        seed: Random seed for reproducibility.

    Returns:
        dict with: sampled_token, greedy_token, top5_tokens (list of {id, prob}), entropy.
    """
    x = np.array(logits, dtype=np.float64)

    sampled = sample_token(
        x,
        temperature=temperature,
        top_k=top_k,
        top_p=top_p,
        repetition_penalty=repetition_penalty,
        input_ids=previous_tokens or [],
        seed=seed,
    )
    greedy = greedy_decode(x)

    # Top-5 probabilities for inspection
    probs = np.exp(x - np.max(x))
    probs /= probs.sum()
    top5_idx = np.argsort(probs)[-5:][::-1]
    top5 = [{"id": int(i), "prob": float(probs[i])} for i in top5_idx]

    entropy = float(-np.sum(probs * np.log(probs + 1e-30)))

    return {
        "status": "success",
        "sampled_token": sampled,
        "greedy_token": greedy,
        "top5_tokens": top5,
        "entropy": entropy,
    }

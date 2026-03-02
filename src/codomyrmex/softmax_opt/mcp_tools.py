import numpy as np

from codomyrmex.model_context_protocol.decorators import mcp_tool

from .kernel import log_softmax, online_softmax, softmax


@mcp_tool(category="softmax_opt")
def compute_softmax(logits: list[float], temperature: float = 1.0, variant: str = "standard") -> dict:
    """Compute softmax probabilities from logits.

    Args:
        logits: Raw unnormalized scores
        temperature: Temperature scaling (>1 = more uniform, <1 = more peaked)
        variant: "standard", "log", or "online"

    Returns:
        dict with: probabilities (list), log_probs (list), entropy (float), max_prob (float)
    """
    x = np.array(logits, dtype=np.float64)

    if variant == "log":
        log_probs = log_softmax(x)
        probs = np.exp(log_probs)
    elif variant == "online":
        probs = online_softmax(x)
        log_probs = np.log(probs + 1e-30)
    else:
        probs = softmax(x, temperature=temperature)
        log_probs = np.log(probs + 1e-30)

    entropy = float(-np.sum(probs * log_probs))
    return {
        "status": "success",
        "probabilities": probs.tolist(),
        "log_probs": log_probs.tolist(),
        "entropy": entropy,
        "max_prob": float(np.max(probs)),
        "sum_check": float(np.sum(probs)),
    }

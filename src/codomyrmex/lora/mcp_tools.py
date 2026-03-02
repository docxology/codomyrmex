"""MCP tools for the LoRA module."""

import numpy as np

from codomyrmex.model_context_protocol.decorators import mcp_tool


@mcp_tool(category="lora")
def lora_apply(weight_shape: list, rank: int = 4, alpha: float = 8.0) -> dict:
    """Apply LoRA to a weight matrix of given shape.

    Args:
        weight_shape: [d, k] shape of the weight matrix
        rank: LoRA rank r (must be < min(d, k))
        alpha: LoRA scaling alpha

    Returns:
        dict with: weight_shape, rank, scaling, delta_rank, parameter_reduction_pct
    """
    from .lora import LoRAConfig, apply_lora

    d, k = weight_shape
    W = np.random.randn(d, k) * 0.01
    layer = apply_lora(W, rank=rank, alpha=alpha)

    total_params = d * k
    lora_params = rank * k + d * rank
    reduction = (1 - lora_params / total_params) * 100

    return {
        "status": "success",
        "weight_shape": weight_shape,
        "rank": rank,
        "scaling": layer.config.scaling,
        "lora_params": lora_params,
        "total_params": total_params,
        "parameter_reduction_pct": round(reduction, 1),
        "delta_shape": [d, k],
    }

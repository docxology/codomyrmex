"""
MCP tools for the peft module.

Exposes parameter-efficient fine-tuning information and adapter creation
through the Model Context Protocol.
"""

from __future__ import annotations

from codomyrmex.model_context_protocol.decorators import mcp_tool

from .adapters import IA3Adapter, LoRAAdapter, PrefixTuningAdapter


@mcp_tool(category="peft")
def peft_create_adapter(
    method: str, d_model: int, rank: int = 4, alpha: float = 8.0
) -> dict:
    """Create a PEFT adapter and return its parameter statistics.

    Args:
        method: One of "lora", "prefix", "ia3"
        d_model: Model hidden dimension
        rank: LoRA rank (only used for lora method)
        alpha: LoRA alpha scaling (only used for lora method)

    Returns:
        dict with keys: method (str), trainable_params (int),
        full_finetune_params (int), reduction_factor (float)
    """
    full_params = d_model * d_model  # approximate single-layer full params

    if method == "lora":
        adapter = LoRAAdapter(d_in=d_model, d_out=d_model, rank=rank, alpha=alpha)
    elif method == "prefix":
        adapter = PrefixTuningAdapter(d_model=d_model)
    elif method == "ia3":
        adapter = IA3Adapter(d_model=d_model)
    else:
        raise ValueError(
            f"Unknown PEFT method: {method!r}. Supported: lora, prefix, ia3"
        )

    trainable = adapter.trainable_params
    return {
        "method": method,
        "trainable_params": trainable,
        "full_finetune_params": full_params,
        "reduction_factor": (
            round(full_params / trainable, 2) if trainable > 0 else float("inf")
        ),
    }


@mcp_tool(category="peft")
def peft_compare_methods(d_model: int, rank: int = 4) -> dict:
    """Compare all PEFT methods for a given model dimension.

    Args:
        d_model: Model hidden dimension
        rank: LoRA rank for comparison

    Returns:
        dict mapping method name to trainable_params count
    """
    lora = LoRAAdapter(d_in=d_model, d_out=d_model, rank=rank)
    prefix = PrefixTuningAdapter(d_model=d_model)
    ia3 = IA3Adapter(d_model=d_model)

    full_params = d_model * d_model

    return {
        "full_finetune": full_params,
        "lora": lora.trainable_params,
        "prefix": prefix.trainable_params,
        "ia3": ia3.trainable_params,
    }

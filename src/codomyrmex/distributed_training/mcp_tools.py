"""MCP tools for the distributed training module."""

import numpy as np

from codomyrmex.model_context_protocol.decorators import mcp_tool


@mcp_tool(category="distributed_training")
def fsdp_simulate_step(
    param_size: int = 1024,
    world_size: int = 4,
    learning_rate: float = 0.01,
    seed: int = 42,
) -> dict:
    """Simulate one FSDP distributed training step.

    Args:
        param_size: Number of model parameters
        world_size: Number of simulated GPU devices
        learning_rate: SGD learning rate
        seed: Random seed for reproducibility

    Returns:
        dict with: shard_sizes, param_norm_before, param_norm_after, grad_norm
    """
    from .fsdp import simulate_fsdp_step

    np.random.seed(seed)

    params = np.random.randn(param_size) * 0.1
    gradients = [np.random.randn(param_size) * 0.01 for _ in range(world_size)]

    param_norm_before = float(np.linalg.norm(params))
    new_params, shards = simulate_fsdp_step(
        params, gradients, world_size, learning_rate
    )
    param_norm_after = float(np.linalg.norm(new_params))
    mean_grad = np.mean(gradients, axis=0)
    grad_norm = float(np.linalg.norm(mean_grad))

    return {
        "status": "success",
        "world_size": world_size,
        "param_size": param_size,
        "shard_sizes": [len(s.param_shard) for s in shards],
        "param_norm_before": round(param_norm_before, 4),
        "param_norm_after": round(param_norm_after, 4),
        "grad_norm": round(grad_norm, 4),
        "learning_rate": learning_rate,
    }

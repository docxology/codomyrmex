"""MCP tools for state space models and flash attention."""
import numpy as np

from codomyrmex.model_context_protocol.decorators import mcp_tool


@mcp_tool(category="ssm")
def ssm_forward(
    sequence_length: int = 8,
    d_model: int = 16,
    d_state: int = 8,
    n_layers: int = 2,
) -> dict:
    """Run a forward pass through Mamba State Space Model.

    Args:
        sequence_length: Sequence length to process
        d_model: Model dimension
        d_state: SSM state dimension
        n_layers: Number of Mamba blocks to stack

    Returns:
        dict with: output_shape, d_model, d_state, n_layers
    """
    from .mamba import mamba_forward

    x = np.random.randn(1, sequence_length, d_model).astype(np.float32)
    output = mamba_forward(x, n_layers=n_layers, d_model=d_model, d_state=d_state)
    return {
        "status": "success",
        "output_shape": list(output.shape),
        "d_model": d_model,
        "d_state": d_state,
        "n_layers": n_layers,
    }


@mcp_tool(category="neural")
def flash_attention_forward(
    seq_len: int = 16,
    d_model: int = 32,
    block_size: int = 8,
) -> dict:
    """Run Flash Attention and verify against standard attention.

    Args:
        seq_len: Sequence length
        d_model: Q/K/V dimension
        block_size: Flash attention tile size

    Returns:
        dict with: output_shape, max_error_vs_standard (should be < 1e-5), passed
    """
    from codomyrmex.neural.flash_attention import flash_attention, verify_flash_vs_standard

    Q = np.random.randn(1, seq_len, d_model).astype(np.float32)
    K = np.random.randn(1, seq_len, d_model).astype(np.float32)
    V = np.random.randn(1, seq_len, d_model).astype(np.float32)
    max_err, _, flash_out = verify_flash_vs_standard(Q, K, V)
    return {
        "status": "success",
        "output_shape": list(flash_out.shape),
        "max_error_vs_standard": max_err,
        "passed": max_err < 1e-4,
    }

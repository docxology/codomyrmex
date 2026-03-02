"""MCP tools for neural network primitives."""
import numpy as np

from codomyrmex.model_context_protocol.decorators import mcp_tool


@mcp_tool(category="neural")
def transformer_encode(
    sequence_length: int = 8,
    d_model: int = 64,
    n_heads: int = 4,
    n_layers: int = 2,
) -> dict:
    """Run a forward pass through a randomly-initialized Transformer encoder.

    Args:
        sequence_length: Number of tokens in the sequence
        d_model: Model dimension (must be divisible by n_heads)
        n_heads: Number of attention heads
        n_layers: Number of transformer blocks

    Returns:
        dict with: output_shape, d_model, n_heads, n_layers, sequence_length
    """
    from .transformer import TransformerEncoder

    batch_size = 1
    encoder = TransformerEncoder(
        n_layers=n_layers, d_model=d_model, n_heads=n_heads, d_ff=d_model * 4
    )
    x = np.random.randn(batch_size, sequence_length, d_model).astype(np.float32)
    output = encoder(x)
    return {
        "status": "success",
        "output_shape": list(output.shape),
        "d_model": d_model,
        "n_heads": n_heads,
        "n_layers": n_layers,
        "sequence_length": sequence_length,
    }


@mcp_tool(category="neural")
def attention_forward(
    seq_len: int = 6,
    d_model: int = 32,
    n_heads: int = 4,
) -> dict:
    """Run multi-head attention on random inputs.

    Args:
        seq_len: Sequence length
        d_model: Model dimension
        n_heads: Number of attention heads

    Returns:
        dict with: output_shape, attention_weights_shape, d_k (head dimension)
    """
    from .attention import MultiHeadAttention

    mha = MultiHeadAttention(d_model, n_heads)
    x = np.random.randn(1, seq_len, d_model).astype(np.float32)
    output, weights = mha(x, x, x)
    return {
        "status": "success",
        "output_shape": list(output.shape),
        "attention_weights_shape": list(weights.shape),
        "d_k": d_model // n_heads,
    }

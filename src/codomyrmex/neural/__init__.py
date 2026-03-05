"""Neural network primitives -- Transformer, attention, activations from scratch."""

from .activations import gelu, relu, swish
from .attention import MultiHeadAttention, scaled_dot_product_attention
from .flash_attention import flash_attention, verify_flash_vs_standard
from .layers import Embedding, FeedForward, LayerNorm, PositionalEncoding
from .transformer import TransformerBlock, TransformerDecoder, TransformerEncoder

__all__ = [
    "Embedding",
    "FeedForward",
    "LayerNorm",
    "MultiHeadAttention",
    "PositionalEncoding",
    "TransformerBlock",
    "TransformerDecoder",
    "TransformerEncoder",
    "flash_attention",
    "gelu",
    "relu",
    "scaled_dot_product_attention",
    "swish",
    "verify_flash_vs_standard",
]

"""Transformer encoder and decoder blocks from 'Attention Is All You Need'."""
from __future__ import annotations

import typing


import numpy as np

from .attention import MultiHeadAttention
from .layers import Embedding, FeedForward, LayerNorm, PositionalEncoding


class TransformerBlock:
    """Single transformer encoder block: self-attn + FFN, both with residual + LayerNorm.

    Pre-LN variant (more stable for training):
        output = x + Attn(LN(x))
        output = output + FFN(LN(output))
    """

    def __init__(self, d_model: int, n_heads: int, d_ff: int, dropout: float = 0.0):
        """Initialize TransformerBlock."""
        self.self_attn = MultiHeadAttention(d_model, n_heads, dropout)
        self.ffn = FeedForward(d_model, d_ff)
        self.ln1 = LayerNorm(d_model)
        self.ln2 = LayerNorm(d_model)

    def forward(self, x: np.ndarray, mask: np.ndarray | None = None) -> np.ndarray:
        """Forward pass through one transformer block.

        Args:
            x: (batch, seq, d_model)
            mask: Optional attention mask

        Returns:
            (batch, seq, d_model)

        """
        # Self-attention with residual (pre-LN)
        normed = self.ln1(x)
        attn_out, _ = self.self_attn(normed, normed, normed, mask)
        x = x + attn_out
        # FFN with residual (pre-LN)
        x = x + self.ffn(self.ln2(x))
        return x

    def __call__(self, x: np.ndarray, mask: np.ndarray | None = None) -> np.ndarray:
        """Make TransformerBlock callable."""
        return self.forward(x, mask)


class TransformerEncoder:
    """Stack of N TransformerBlocks for encoding sequences.

    Optionally includes token embedding and sinusoidal positional encoding
    when vocab_size > 0.
    """

    def __init__(
        self,
        n_layers: int,
        d_model: int,
        n_heads: int,
        d_ff: int,
        vocab_size: int = 0,
        max_len: int = 512,
        dropout: float = 0.0,
    ):
        """Initialize TransformerEncoder."""
        self.d_model = d_model
        self.embedding = Embedding(vocab_size, d_model) if vocab_size > 0 else None
        self.pos_enc = PositionalEncoding(d_model, max_len)
        self.layers = [
            TransformerBlock(d_model, n_heads, d_ff, dropout) for _ in range(n_layers)
        ]
        self.ln = LayerNorm(d_model)

    def forward(self, x: np.ndarray, mask: np.ndarray | None = None) -> np.ndarray:
        """Forward pass through the encoder stack.

        Args:
            x: (batch, seq) int token ids OR (batch, seq, d_model) float embeddings
            mask: Optional attention mask

        Returns:
            (batch, seq, d_model) encoded representations

        """
        if x.ndim == 2 and self.embedding is not None:
            x = self.embedding(x)  # (batch, seq, d_model)
        x = self.pos_enc(x)
        for layer in self.layers:
            x = layer(x, mask)
        return self.ln(x)

    def __call__(self, x: np.ndarray, mask: np.ndarray | None = None) -> np.ndarray:
        """Make TransformerEncoder callable."""
        return self.forward(x, mask)


class TransformerDecoder:
    """Transformer decoder with masked self-attention and cross-attention to encoder output.

    Each layer applies:
        1. Masked self-attention (causal)
        2. Cross-attention to encoder memory
        3. Position-wise FFN
    All with pre-LN residual connections.
    """

    def __init__(self, n_layers: int, d_model: int, n_heads: int, d_ff: int):
        """Initialize TransformerDecoder."""
        self.layers: list[dict[str, typing.Any]] = []
        for _ in range(n_layers):
            self.layers.append(
                {
                    "self_attn": MultiHeadAttention(d_model, n_heads),
                    "cross_attn": MultiHeadAttention(d_model, n_heads),
                    "ffn": FeedForward(d_model, d_ff),
                    "ln1": LayerNorm(d_model),
                    "ln2": LayerNorm(d_model),
                    "ln3": LayerNorm(d_model),
                }
            )
        self.ln = LayerNorm(d_model)
        self.d_model = d_model

    def forward(
        self,
        tgt: np.ndarray,
        memory: np.ndarray,
        tgt_mask: np.ndarray | None = None,
        memory_mask: np.ndarray | None = None,
    ) -> np.ndarray:
        """Forward pass through the decoder stack.

        Args:
            tgt: (batch, tgt_seq, d_model) decoder input
            memory: (batch, src_seq, d_model) encoder output
            tgt_mask: Optional causal mask for self-attention
            memory_mask: Optional mask for cross-attention

        Returns:
            (batch, tgt_seq, d_model) decoded representations

        """
        x = tgt
        for layer in self.layers:
            # Masked self-attention
            normed1 = layer["ln1"](x)
            attn1, _ = layer["self_attn"](
                normed1, normed1, normed1, tgt_mask
            )
            x = x + attn1
            # Cross-attention to encoder memory
            attn2, _ = layer["cross_attn"](
                layer["ln2"](x), memory, memory, memory_mask
            )
            x = x + attn2
            # FFN
            x = typing.cast(
                np.ndarray,
                x
                + typing.cast(
                    np.ndarray,
                    layer["ffn"](
                        layer["ln3"](x)
                    ),
                ),
            )
        return self.ln(x)

    def __call__(
        self,
        tgt: np.ndarray,
        memory: np.ndarray,
        tgt_mask: np.ndarray | None = None,
        memory_mask: np.ndarray | None = None,
    ) -> np.ndarray:
        """Make TransformerDecoder callable."""
        return self.forward(tgt, memory, tgt_mask, memory_mask)

"""Multi-head attention mechanism from 'Attention Is All You Need' (Vaswani et al. 2017)."""
from __future__ import annotations

import numpy as np
from typing import Optional


def scaled_dot_product_attention(
    Q: np.ndarray,
    K: np.ndarray,
    V: np.ndarray,
    mask: Optional[np.ndarray] = None,
) -> tuple[np.ndarray, np.ndarray]:
    """Scaled dot-product attention.

    Attention(Q, K, V) = softmax(Q @ K^T / sqrt(d_k)) @ V

    Args:
        Q: Queries, shape (..., seq_len_q, d_k)
        K: Keys,    shape (..., seq_len_k, d_k)
        V: Values,  shape (..., seq_len_k, d_v)
        mask: Boolean mask, True = attend, False = mask out.
              Shape (..., seq_len_q, seq_len_k)

    Returns:
        output: shape (..., seq_len_q, d_v)
        weights: Attention weights, shape (..., seq_len_q, seq_len_k)
    """
    d_k = Q.shape[-1]
    scores = Q @ K.swapaxes(-2, -1) / np.sqrt(d_k)  # (..., seq_q, seq_k)

    if mask is not None:
        scores = np.where(mask, scores, -1e9)

    # Numerically stable softmax
    scores_max = np.max(scores, axis=-1, keepdims=True)
    exp_scores = np.exp(scores - scores_max)
    weights = exp_scores / (np.sum(exp_scores, axis=-1, keepdims=True) + 1e-9)

    output = weights @ V  # (..., seq_q, d_v)
    return output, weights


class MultiHeadAttention:
    """Multi-head attention from 'Attention Is All You Need'.

    Splits d_model into n_heads parallel attention heads,
    each attending to different representation subspaces.

    MultiHead(Q, K, V) = Concat(head_1, ..., head_h) @ W_O
    where head_i = Attention(Q @ W_Qi, K @ W_Ki, V @ W_Vi)
    """

    def __init__(self, d_model: int, n_heads: int, dropout: float = 0.0):
        if d_model % n_heads != 0:
            raise AssertionError(
                f"d_model ({d_model}) must be divisible by n_heads ({n_heads})"
            )
        self.d_model = d_model
        self.n_heads = n_heads
        self.d_k = d_model // n_heads
        self.dropout = dropout

        # Xavier-style initialization for weight matrices
        scale = np.sqrt(2.0 / (d_model + d_model))
        self.W_Q = np.random.randn(d_model, d_model) * scale
        self.W_K = np.random.randn(d_model, d_model) * scale
        self.W_V = np.random.randn(d_model, d_model) * scale
        self.W_O = np.random.randn(d_model, d_model) * scale

        self.b_Q = np.zeros(d_model)
        self.b_K = np.zeros(d_model)
        self.b_V = np.zeros(d_model)
        self.b_O = np.zeros(d_model)

    def forward(
        self,
        query: np.ndarray,
        key: np.ndarray,
        value: np.ndarray,
        mask: Optional[np.ndarray] = None,
    ) -> tuple[np.ndarray, np.ndarray]:
        """Forward pass of multi-head attention.

        Args:
            query: (batch, seq_q, d_model)
            key:   (batch, seq_k, d_model)
            value: (batch, seq_k, d_model)
            mask:  Optional attention mask

        Returns:
            output: (batch, seq_q, d_model)
            weights: (batch, n_heads, seq_q, seq_k)
        """
        batch_size, seq_len_q, _ = query.shape
        _, seq_len_k, _ = key.shape

        # Linear projections
        Q = query @ self.W_Q + self.b_Q  # (batch, seq_q, d_model)
        K = key @ self.W_K + self.b_K  # (batch, seq_k, d_model)
        V = value @ self.W_V + self.b_V  # (batch, seq_k, d_model)

        # Split into heads: (batch, n_heads, seq, d_k)
        Q = Q.reshape(batch_size, seq_len_q, self.n_heads, self.d_k).transpose(
            0, 2, 1, 3
        )
        K = K.reshape(batch_size, seq_len_k, self.n_heads, self.d_k).transpose(
            0, 2, 1, 3
        )
        V = V.reshape(batch_size, seq_len_k, self.n_heads, self.d_k).transpose(
            0, 2, 1, 3
        )

        # Expand mask for multi-head: (batch, 1, seq_q, seq_k)
        if mask is not None and mask.ndim == 3:
            mask = mask[:, np.newaxis, :, :]

        attn_output, attn_weights = scaled_dot_product_attention(Q, K, V, mask)
        # attn_output: (batch, n_heads, seq_q, d_k)

        # Concatenate heads: (batch, seq_q, d_model)
        attn_output = attn_output.transpose(0, 2, 1, 3).reshape(
            batch_size, seq_len_q, self.d_model
        )

        # Output projection
        output = attn_output @ self.W_O + self.b_O

        return output, attn_weights

    def __call__(self, query, key, value, mask=None):
        """Make MultiHeadAttention callable."""
        return self.forward(query, key, value, mask)

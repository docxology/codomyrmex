"""Small Language Model (GPT-2 architecture) built from scratch with NumPy.

Architecture:
- Token embedding + sinusoidal positional encoding
- N decoder-only transformer blocks (pre-LN, causal self-attention)
- Language model head (d_model -> vocab_size)
- Greedy autoregressive generation
"""

from dataclasses import dataclass
from typing import Any

import numpy as np


@dataclass
class SLMConfig:
    """Configuration for the Small Language Model."""

    vocab_size: int = 1000
    d_model: int = 64
    n_heads: int = 4
    n_layers: int = 2
    d_ff: int = 256
    max_seq_len: int = 128
    dropout: float = 0.0


def causal_mask(seq_len: int) -> np.ndarray:
    """Upper triangular causal mask: True = can attend, False = masked.

    Args:
        seq_len: Sequence length

    Returns:
        Boolean mask of shape (seq_len, seq_len), lower triangular True
    """
    mask = np.tril(np.ones((seq_len, seq_len), dtype=bool))
    return mask


class SLM:
    """Small Language Model (GPT-2 architecture).

    Architecture:
    - Token embedding + positional encoding
    - N decoder-only transformer blocks (pre-LN, causal self-attention)
    - Language model head (d_model -> vocab_size)
    """

    def __init__(self, config: SLMConfig | None = None) -> None:
        self.config = config or SLMConfig()
        c = self.config

        # Embeddings
        scale = np.sqrt(1.0 / c.d_model)
        self.token_embed = np.random.randn(c.vocab_size, c.d_model) * scale

        # Positional encoding (sinusoidal)
        pe = np.zeros((c.max_seq_len, c.d_model))
        pos = np.arange(c.max_seq_len)[:, np.newaxis]
        div = np.exp(np.arange(0, c.d_model, 2) * (-np.log(10000.0) / c.d_model))
        pe[:, 0::2] = np.sin(pos * div)
        pe[:, 1::2] = np.cos(pos * div[: c.d_model // 2])
        self.pos_enc = pe

        # Import neural building blocks -- fall back to inline if not available
        from typing import Any

        MultiHeadAttention: Any
        FeedForward: Any
        LayerNorm: Any
        try:
            from codomyrmex.neural.attention import MultiHeadAttention
            from codomyrmex.neural.layers import FeedForward, LayerNorm
        except ImportError:
            MultiHeadAttention = _InlineMultiHeadAttention
            FeedForward = _InlineFeedForward
            LayerNorm = _InlineLayerNorm

        # Transformer blocks
        self.blocks = []
        for _ in range(c.n_layers):
            self.blocks.append(
                {
                    "attn": MultiHeadAttention(c.d_model, c.n_heads),
                    "ffn": FeedForward(c.d_model, c.d_ff),
                    "ln1": LayerNorm(c.d_model),
                    "ln2": LayerNorm(c.d_model),
                }
            )

        # Final layer norm and LM head
        self.ln_f = LayerNorm(c.d_model)
        self.lm_head = np.random.randn(c.d_model, c.vocab_size) * scale

    def forward(self, token_ids: np.ndarray) -> Any:
        """Forward pass through the transformer.

        Args:
            token_ids: (batch, seq) integer token IDs

        Returns:
            logits: (batch, seq, vocab_size)
        """
        batch, seq = token_ids.shape
        if seq > self.config.max_seq_len:
            raise ValueError(
                f"Sequence length {seq} exceeds max_seq_len {self.config.max_seq_len}"
            )

        # Embed + positional encode
        x = self.token_embed[token_ids] * np.sqrt(self.config.d_model)
        x = x + self.pos_enc[:seq][np.newaxis, :, :]

        # Causal mask: (seq, seq) bool
        mask = causal_mask(seq)

        # Transformer blocks (pre-LN style)
        for block in self.blocks:
            ln1_out = block["ln1"](x)
            attn_out, _ = block["attn"](ln1_out, ln1_out, ln1_out, mask)
            x = x + attn_out
            x = x + block["ffn"](block["ln2"](x))

        x = self.ln_f(x)
        logits = x @ self.lm_head  # (batch, seq, vocab_size)
        return logits

    def generate(self, prompt_ids: list[int], max_new_tokens: int = 20) -> list[int]:
        """Greedy autoregressive generation.

        Args:
            prompt_ids: List of initial token IDs
            max_new_tokens: Number of tokens to generate

        Returns:
            Full sequence including prompt and generated tokens
        """
        context = list(prompt_ids)
        for _ in range(max_new_tokens):
            ids = np.array([context[-self.config.max_seq_len :]])
            logits = self.forward(ids)
            next_token = int(np.argmax(logits[0, -1, :]))
            context.append(next_token)
        return context

    def __call__(self, x: np.ndarray) -> Any:
        """Make SLM callable.

        Args:
            x: Input token IDs.

        Returns:
            Logits tensor.
        """
        return self.forward(x)


# ---------------------------------------------------------------------------
# Inline fallback implementations (used if codomyrmex.neural not available)
# ---------------------------------------------------------------------------


class _InlineLayerNorm:
    """Inline LayerNorm fallback."""

    def __init__(self, d_model: int, eps: float = 1e-6) -> None:
        """Initialize inline layer norm.

        Args:
            d_model: The model dimension.
            eps: Epsilon value for numerical stability.
        """
        self.gamma = np.ones(d_model)
        self.beta = np.zeros(d_model)
        self.eps = eps

    def __call__(self, x: np.ndarray) -> Any:
        """Forward pass.

        Args:
            x: Input tensor.

        Returns:
            Normalized tensor.
        """
        mean = np.mean(x, axis=-1, keepdims=True)
        var = np.var(x, axis=-1, keepdims=True)
        return self.gamma * (x - mean) / np.sqrt(var + self.eps) + self.beta


class _InlineFeedForward:
    """Inline FeedForward fallback."""

    def __init__(self, d_model: int, d_ff: int) -> None:
        """Initialize inline feed forward.

        Args:
            d_model: The model dimension.
            d_ff: The feed forward hidden dimension.
        """
        scale = np.sqrt(2.0 / d_model)
        self.W1 = np.random.randn(d_model, d_ff) * scale
        self.b1 = np.zeros(d_ff)
        self.W2 = np.random.randn(d_ff, d_model) * scale
        self.b2 = np.zeros(d_model)

    def __call__(self, x: np.ndarray) -> Any:
        """Forward pass.

        Args:
            x: Input tensor.

        Returns:
            Output tensor.
        """
        h = np.maximum(0, x @ self.W1 + self.b1)  # ReLU instead of GELU
        return h @ self.W2 + self.b2


class _InlineMultiHeadAttention:
    """Inline MultiHeadAttention fallback."""

    def __init__(self, d_model: int, n_heads: int) -> None:
        """Initialize inline multi-head attention.

        Args:
            d_model: The model dimension.
            n_heads: Number of attention heads.
        """
        self.d_model = d_model
        self.n_heads = n_heads
        self.d_k = d_model // n_heads
        scale = np.sqrt(2.0 / (d_model + d_model))
        self.W_Q = np.random.randn(d_model, d_model) * scale
        self.W_K = np.random.randn(d_model, d_model) * scale
        self.W_V = np.random.randn(d_model, d_model) * scale
        self.W_O = np.random.randn(d_model, d_model) * scale

    def __call__(
        self,
        query: np.ndarray,
        key: np.ndarray,
        value: np.ndarray,
        mask: np.ndarray | None = None,
    ) -> tuple[Any, Any]:
        """Forward pass.

        Args:
            query: Query tensor.
            key: Key tensor.
            value: Value tensor.
            mask: Optional attention mask.

        Returns:
            Output tensor and attention weights.
        """
        batch, seq_q, _ = query.shape
        _, seq_k, _ = key.shape
        Q = (
            (query @ self.W_Q)
            .reshape(batch, seq_q, self.n_heads, self.d_k)
            .transpose(0, 2, 1, 3)
        )
        K = (
            (key @ self.W_K)
            .reshape(batch, seq_k, self.n_heads, self.d_k)
            .transpose(0, 2, 1, 3)
        )
        V = (
            (value @ self.W_V)
            .reshape(batch, seq_k, self.n_heads, self.d_k)
            .transpose(0, 2, 1, 3)
        )
        scores = Q @ K.swapaxes(-2, -1) / np.sqrt(self.d_k)
        if mask is not None:
            scores = np.where(mask, scores, -1e9)
        exp_s = np.exp(scores - np.max(scores, axis=-1, keepdims=True))
        weights = exp_s / (np.sum(exp_s, axis=-1, keepdims=True) + 1e-9)
        out = (weights @ V).transpose(0, 2, 1, 3).reshape(batch, seq_q, self.d_model)
        return out @ self.W_O, weights

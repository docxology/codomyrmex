"""Core neural network layers: LayerNorm, FeedForward, PositionalEncoding, Embedding."""

import numpy as np


class LayerNorm:
    """Layer normalization: normalize across feature dim, learn scale and shift.

    Ba, Kiros & Hinton 2016 -- 'Layer Normalization'.
    """

    def __init__(self, d_model: int, eps: float = 1e-6):
        self.d_model = d_model
        self.eps = eps
        self.gamma = np.ones(d_model)  # scale
        self.beta = np.zeros(d_model)  # shift

    def forward(self, x: np.ndarray) -> np.ndarray:
        """Normalize input across last dimension.

        Args:
            x: (..., d_model)

        Returns:
            Normalized tensor (..., d_model)
        """
        mean = np.mean(x, axis=-1, keepdims=True)
        var = np.var(x, axis=-1, keepdims=True)
        x_norm = (x - mean) / np.sqrt(var + self.eps)
        return self.gamma * x_norm + self.beta

    def __call__(self, x):
        """Make LayerNorm callable."""
        return self.forward(x)


class FeedForward:
    """Position-wise feed-forward network: two linear layers with GELU in between.

    FFN(x) = GELU(x @ W1 + b1) @ W2 + b2
    """

    def __init__(self, d_model: int, d_ff: int):
        self.d_model = d_model
        self.d_ff = d_ff
        scale = np.sqrt(2.0 / d_model)
        self.W1 = np.random.randn(d_model, d_ff) * scale
        self.b1 = np.zeros(d_ff)
        self.W2 = np.random.randn(d_ff, d_model) * scale
        self.b2 = np.zeros(d_model)

    def forward(self, x: np.ndarray) -> np.ndarray:
        """Forward pass: x -> linear -> GELU -> linear.

        Args:
            x: (..., d_model)

        Returns:
            (..., d_model)
        """
        from .activations import gelu

        h = gelu(x @ self.W1 + self.b1)
        return h @ self.W2 + self.b2

    def __call__(self, x):
        """Make FeedForward callable."""
        return self.forward(x)


class PositionalEncoding:
    """Sinusoidal positional encoding from Vaswani et al. 2017.

    PE(pos, 2i)   = sin(pos / 10000^(2i/d_model))
    PE(pos, 2i+1) = cos(pos / 10000^(2i/d_model))
    """

    def __init__(self, d_model: int, max_len: int = 5000):
        self.d_model = d_model
        pe = np.zeros((max_len, d_model))
        position = np.arange(max_len)[:, np.newaxis]
        div_term = np.exp(np.arange(0, d_model, 2) * (-np.log(10000.0) / d_model))
        pe[:, 0::2] = np.sin(position * div_term)
        pe[:, 1::2] = np.cos(position * div_term[: d_model // 2])
        self.pe = pe  # (max_len, d_model)

    def forward(self, x: np.ndarray) -> np.ndarray:
        """Add positional encoding to input embeddings.

        Args:
            x: (batch, seq, d_model)

        Returns:
            (batch, seq, d_model) with positional encoding added
        """
        seq_len = x.shape[1]
        return x + self.pe[:seq_len][np.newaxis, :, :]

    def __call__(self, x):
        """Make PositionalEncoding callable."""
        return self.forward(x)


class Embedding:
    """Token embedding lookup table with scaling.

    Scales embeddings by sqrt(d_model) following Vaswani et al. 2017.
    """

    def __init__(self, vocab_size: int, d_model: int):
        self.vocab_size = vocab_size
        self.d_model = d_model
        self.weight = np.random.randn(vocab_size, d_model) * np.sqrt(1.0 / d_model)

    def forward(self, token_ids: np.ndarray) -> np.ndarray:
        """Look up token embeddings.

        Args:
            token_ids: (batch, seq) of integer token indices

        Returns:
            (batch, seq, d_model) scaled embeddings
        """
        return self.weight[token_ids] * np.sqrt(self.d_model)

    def __call__(self, x):
        """Make Embedding callable."""
        return self.forward(x)

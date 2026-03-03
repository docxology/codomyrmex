"""Mamba (Gu & Dao 2023) -- selective state space model implementation."""

from __future__ import annotations

import numpy as np


class SelectiveSSM:
    """Selective State Space Model (S6) -- the core of Mamba.

    Unlike S4 which has time-invariant A, B, C matrices, Mamba makes
    B, C, and Delta INPUT-DEPENDENT (selective), allowing the model
    to selectively focus on or ignore different parts of the input.

    State equation (discretized):
        h_t = A_bar_t * h_{t-1} + B_bar_t * x_t
        y_t = C_t * h_t

    where A_bar_t = exp(Delta_t * A)  (zero-order hold discretization)
          B_bar_t = Delta_t * B_t      (simplified)

    A is initialized with HiPPO-like structure:
        A[n,n] = -(n+1) for n=0..N-1 (diagonal)
    """

    def __init__(self, d_model: int, d_state: int = 16, dt_rank: int = None):
        """Initialize selective SSM parameters.

        Args:
            d_model: Input/output dimension
            d_state: SSM state dimension N
            dt_rank: Rank for Delta projection (default: ceil(d_model / 16))
        """
        self.d_model = d_model
        self.d_state = d_state
        self.dt_rank = dt_rank or max(1, d_model // 16)

        # A matrix: (d_model, d_state) -- negative to ensure stability
        # HiPPO initialization: diagonal of -(1, 2, ..., N)
        self.A_log = np.log(
            np.tile(np.arange(1, d_state + 1, dtype=np.float64), (d_model, 1))
        )

        # D: skip connection (direct path, like a residual scalar)
        self.D = np.ones(d_model)

        # Projections for selective parameters (input-dependent)
        # B, C: (batch, seq, d_state) -- projected from input
        # Delta (dt): (batch, seq, d_model) -- projected from input, then softplus
        scale = np.sqrt(1.0 / d_model)
        self.W_B = np.random.randn(d_model, d_state) * scale  # x -> B
        self.W_C = np.random.randn(d_model, d_state) * scale  # x -> C
        self.W_dt = np.random.randn(d_model, self.dt_rank) * scale  # x -> dt
        self.W_dt_proj = (
            np.random.randn(self.dt_rank, d_model) * scale
        )  # dt rank -> d_model
        self.b_dt = np.ones(d_model) * 0.01  # small positive bias

    def forward(self, x: np.ndarray) -> np.ndarray:
        """Selective SSM forward pass (sequential scan).

        Args:
            x: (batch, seq_len, d_model)

        Returns:
            y: (batch, seq_len, d_model)
        """
        batch, seq_len, d_model = x.shape
        d_state = self.d_state

        # Compute input-dependent parameters
        B = x @ self.W_B  # (batch, seq, d_state)
        C = x @ self.W_C  # (batch, seq, d_state)

        # Delta: softplus(W_dt_proj @ W_dt @ x + b)
        dt_raw = (x @ self.W_dt) @ self.W_dt_proj + self.b_dt  # (batch, seq, d_model)
        dt = np.log1p(np.exp(dt_raw))  # softplus, ensures positivity

        # Discretize A: A_bar = exp(-exp(A_log) * dt) per timestep
        # A shape: (d_model, d_state); dt shape: (batch, seq, d_model)
        A = -np.exp(self.A_log)  # (d_model, d_state), all negative

        # Sequential scan
        h = np.zeros((batch, d_model, d_state))  # hidden state
        y = np.zeros((batch, seq_len, d_model))

        for t in range(seq_len):
            x_t = x[:, t, :]  # (batch, d_model)
            B_t = B[:, t, :]  # (batch, d_state)
            C_t = C[:, t, :]  # (batch, d_state)
            dt_t = dt[:, t, :]  # (batch, d_model)

            # Discretize A for this step: A_bar = exp(diag(dt) * A)
            # (batch, d_model, d_state)
            dt_A = dt_t[:, :, np.newaxis] * A[np.newaxis, :, :]
            A_bar = np.exp(dt_A)  # (batch, d_model, d_state)

            # B_bar = dt * B: (batch, d_model, d_state)
            B_bar = dt_t[:, :, np.newaxis] * B_t[:, np.newaxis, :]  # broadcast

            # State update: h = A_bar * h + B_bar * x_t
            h = A_bar * h + B_bar * x_t[:, :, np.newaxis]

            # Output: y_t = C * h summed over state dim + D * x
            y_t = np.einsum("bds,bs->bd", h, C_t) + self.D * x_t
            y[:, t, :] = y_t

        return y


class MambaBlock:
    """Mamba block: selective SSM with input projection, conv, and output projection.

    Architecture:
        x -> split -> [SSM path] + [gate path] -> merge -> output
        SSM path: linear -> conv1d -> silu -> SSM
        gate path: linear -> silu
        merge: element-wise multiply (gated output)
        output: linear projection back to d_model
    """

    def __init__(
        self,
        d_model: int,
        d_inner: int = None,
        d_state: int = 16,
        d_conv: int = 4,
    ):
        """Initialize Mamba block.

        Args:
            d_model: Input dimension
            d_inner: Expanded inner dimension (default 2 * d_model)
            d_state: SSM state dimension
            d_conv: Causal conv1d kernel size
        """
        self.d_model = d_model
        self.d_inner = d_inner or 2 * d_model
        self.d_state = d_state
        self.d_conv = d_conv

        scale = np.sqrt(1.0 / d_model)

        # Input projection: d_model -> 2 * d_inner (x and z in the paper)
        self.in_proj = np.random.randn(d_model, 2 * self.d_inner) * scale

        # Causal conv1d: acts on d_inner channels with kernel size d_conv
        self.conv_weight = np.random.randn(self.d_inner, 1, d_conv) * 0.01  # depthwise
        self.conv_bias = np.zeros(self.d_inner)

        # SSM
        self.ssm = SelectiveSSM(self.d_inner, d_state)

        # Output projection: d_inner -> d_model
        self.out_proj = np.random.randn(self.d_inner, d_model) * scale

    def _causal_conv1d(self, x: np.ndarray) -> np.ndarray:
        """Causal depthwise conv1d: (batch, seq, d) -> (batch, seq, d)."""
        batch, seq, d = x.shape
        k = self.d_conv
        # Pad left with k-1 zeros for causality
        padded = np.pad(x, ((0, 0), (k - 1, 0), (0, 0)))  # (batch, seq+k-1, d)
        out = np.zeros_like(x)
        for i in range(seq):
            window = padded[:, i : i + k, :]  # (batch, k, d)
            # Depthwise: weight is (d, 1, k), apply per-channel
            for c in range(d):
                out[:, i, c] = (
                    np.sum(window[:, :, c] * self.conv_weight[c, 0, :], axis=-1)
                    + self.conv_bias[c]
                )
        return out

    def _silu(self, x: np.ndarray) -> np.ndarray:
        """SiLU activation: x * sigmoid(x)."""
        return x * (1.0 / (1.0 + np.exp(-np.clip(x, -500, 500))))

    def forward(self, x: np.ndarray) -> np.ndarray:
        """Forward pass through MambaBlock.

        Args:
            x: (batch, seq, d_model)

        Returns:
            (batch, seq, d_model)
        """
        # Input projection: split into x_path and gate
        proj = x @ self.in_proj  # (batch, seq, 2*d_inner)
        x_path, z = proj[..., : self.d_inner], proj[..., self.d_inner :]

        # SSM path
        x_path = self._causal_conv1d(x_path)
        x_path = self._silu(x_path)
        y = self.ssm.forward(x_path)

        # Gated output
        y = y * self._silu(z)

        # Output projection
        return y @ self.out_proj

    def __call__(self, x: np.ndarray) -> np.ndarray:
        """Make MambaBlock callable."""
        return self.forward(x)


def mamba_forward(
    x: np.ndarray,
    n_layers: int = 2,
    d_model: int = None,
    d_state: int = 16,
) -> np.ndarray:
    """Stack multiple Mamba blocks with residual connections.

    Args:
        x: (batch, seq, d_model)
        n_layers: Number of stacked Mamba blocks
        d_model: Model dimension (inferred from x if None)
        d_state: SSM state dimension

    Returns:
        (batch, seq, d_model) -- output after all layers
    """
    if d_model is None:
        d_model = x.shape[-1]
    layers = [MambaBlock(d_model, d_state=d_state) for _ in range(n_layers)]
    for layer in layers:
        x = x + layer(x)  # residual connection
    return x

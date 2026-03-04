"""Flash Attention (Dao et al. 2022) -- memory-efficient attention via tiled online softmax."""

from __future__ import annotations

import numpy as np


def flash_attention(
    Q: np.ndarray,
    K: np.ndarray,
    V: np.ndarray,
    block_size: int = 64,
    causal: bool = False,
) -> np.ndarray:
    """Flash Attention: memory-efficient attention via tiled online softmax.

    Standard attention requires O(N^2) memory (the full attention matrix).
    Flash Attention requires only O(N) memory by processing in tiles.

    Algorithm (simplified Dao et al. 2022):
    For each query tile Q_i:
        Initialize: O_i = 0, l_i = 0, m_i = -inf
        For each key/value tile K_j, V_j:
            S_ij = Q_i @ K_j^T / sqrt(d_k)   # tile attention scores
            if causal: mask future positions
            m_ij = max(S_ij, axis=-1)          # tile max
            m_new = max(m_i, m_ij)             # new running max
            P_ij = exp(S_ij - m_new)           # re-scaled exp
            l_new = exp(m_i - m_new) * l_i + sum(P_ij)  # new normalizer
            O_i = (exp(m_i - m_new) * l_i * O_i + P_ij @ V_j) / l_new
            m_i, l_i = m_new, l_new
    Return O_i (normalized output)

    # CUDA_ACCELERATE: GPU version uses shared memory tiles for L1 cache hits

    Args:
        Q: (batch, n_heads, seq_q, d_k) OR (batch, seq_q, d_k) for single-head
        K: (batch, n_heads, seq_k, d_k)
        V: (batch, n_heads, seq_k, d_v)
        block_size: Tile size (default 64, like Flash Attention paper)
        causal: If True, mask future keys (for decoder self-attention)

    Returns:
        output: Same shape as Q, but last dim = d_v

    """
    orig_ndim = Q.ndim
    if orig_ndim == 3:  # (batch, seq, d) -> add head dim
        Q = Q[:, np.newaxis, :, :]
        K = K[:, np.newaxis, :, :]
        V = V[:, np.newaxis, :, :]

    batch, n_heads, seq_q, d_k = Q.shape
    _, _, seq_k, d_v = V.shape
    scale = 1.0 / np.sqrt(d_k)

    out = np.zeros((batch, n_heads, seq_q, d_v))

    # Process Q in tiles
    for q_start in range(0, seq_q, block_size):
        q_end = min(q_start + block_size, seq_q)
        Q_block = Q[:, :, q_start:q_end, :]  # (batch, heads, bq, d_k)
        bq = q_end - q_start

        # Running statistics for this Q-tile
        m_i = np.full((batch, n_heads, bq), float("-inf"))
        l_i = np.zeros((batch, n_heads, bq))
        O_i = np.zeros((batch, n_heads, bq, d_v))

        # Process K/V in tiles
        for k_start in range(0, seq_k, block_size):
            k_end = min(k_start + block_size, seq_k)
            K_block = K[:, :, k_start:k_end, :]  # (batch, heads, bk, d_k)
            V_block = V[:, :, k_start:k_end, :]  # (batch, heads, bk, d_v)

            # Attention scores for this tile: (batch, heads, bq, bk)
            S = Q_block @ K_block.swapaxes(-2, -1) * scale

            # Causal masking: query at position q_start+i cannot attend to keys > q_start+i
            if causal:
                q_indices = np.arange(q_start, q_end)[:, np.newaxis]
                k_indices = np.arange(k_start, k_end)[np.newaxis, :]
                causal_mask = q_indices >= k_indices  # (bq, bk)
                S = np.where(
                    causal_mask[np.newaxis, np.newaxis, :, :], S, float("-inf")
                )

            # Online softmax update
            m_ij = np.max(S, axis=-1)  # (batch, heads, bq) - tile max
            m_new = np.maximum(m_i, m_ij)  # new running max

            exp_S = np.exp(S - m_new[..., np.newaxis])  # (batch, heads, bq, bk)
            l_ij = np.sum(exp_S, axis=-1)  # (batch, heads, bq)

            # Rescale existing accumulator and add new contribution
            rescale = np.exp(m_i - m_new)  # (batch, heads, bq)
            l_new = rescale * l_i + l_ij

            O_i = (
                rescale[..., np.newaxis] * l_i[..., np.newaxis] * O_i + exp_S @ V_block
            ) / (l_new[..., np.newaxis] + 1e-9)

            m_i = m_new
            l_i = l_new

        out[:, :, q_start:q_end, :] = O_i

    if orig_ndim == 3:
        out = out[:, 0, :, :]

    return out


def verify_flash_vs_standard(
    Q: np.ndarray, K: np.ndarray, V: np.ndarray
) -> tuple[float, np.ndarray, np.ndarray]:
    """Verify Flash Attention output matches standard attention.

    Returns:
        (max_abs_error, standard_output, flash_output)

    """
    from codomyrmex.neural.attention import scaled_dot_product_attention

    # Standard attention (reference)
    ref_out, _ = scaled_dot_product_attention(Q, K, V)

    # Flash attention
    flash_out = flash_attention(Q, K, V)

    max_err = float(np.max(np.abs(ref_out - flash_out)))
    return max_err, ref_out, flash_out

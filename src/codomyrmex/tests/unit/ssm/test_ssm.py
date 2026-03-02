"""Tests for Mamba SSM and Flash Attention implementations."""
import pytest
import numpy as np

from codomyrmex.ssm import MambaBlock, SelectiveSSM, mamba_forward


class TestSelectiveSSM:
    @pytest.mark.unit
    def test_output_shape(self):
        ssm = SelectiveSSM(d_model=16, d_state=8)
        x = np.random.randn(2, 10, 16).astype(np.float32)
        y = ssm.forward(x)
        assert y.shape == (2, 10, 16)

    @pytest.mark.unit
    def test_causal_property(self):
        """Output at t should not change if we modify future inputs."""
        ssm = SelectiveSSM(d_model=8, d_state=4)
        x = np.random.randn(1, 5, 8).astype(np.float32)
        y1 = ssm.forward(x)

        # Modify only future positions (t > 2)
        x2 = x.copy()
        x2[:, 3:, :] = np.random.randn(1, 2, 8)
        y2 = ssm.forward(x2)

        # First 3 outputs should be identical (causal)
        np.testing.assert_allclose(y1[:, :3, :], y2[:, :3, :], atol=1e-5)

    @pytest.mark.unit
    def test_state_is_finite(self):
        ssm = SelectiveSSM(d_model=16, d_state=8)
        x = np.random.randn(1, 20, 16).astype(np.float32)
        y = ssm.forward(x)
        assert not np.any(np.isnan(y))
        assert not np.any(np.isinf(y))

    @pytest.mark.unit
    def test_dt_rank_default(self):
        """dt_rank defaults to d_model // 16, minimum 1."""
        ssm = SelectiveSSM(d_model=8, d_state=4)
        assert ssm.dt_rank == 1  # 8 // 16 = 0, clamped to 1

        ssm2 = SelectiveSSM(d_model=64, d_state=4)
        assert ssm2.dt_rank == 4  # 64 // 16 = 4

    @pytest.mark.unit
    def test_batch_independence(self):
        """Each batch element should be processed independently."""
        ssm = SelectiveSSM(d_model=8, d_state=4)
        x1 = np.random.randn(1, 5, 8).astype(np.float32)
        x2 = np.random.randn(1, 5, 8).astype(np.float32)

        # Process separately
        y1 = ssm.forward(x1)
        y2 = ssm.forward(x2)

        # Process together as batch
        x_batch = np.concatenate([x1, x2], axis=0)
        y_batch = ssm.forward(x_batch)

        np.testing.assert_allclose(y_batch[0:1], y1, atol=1e-6)
        np.testing.assert_allclose(y_batch[1:2], y2, atol=1e-6)


class TestMambaBlock:
    @pytest.mark.unit
    def test_output_shape(self):
        block = MambaBlock(d_model=16, d_state=8)
        x = np.random.randn(1, 8, 16).astype(np.float32)
        out = block(x)
        assert out.shape == (1, 8, 16)

    @pytest.mark.unit
    def test_output_finite(self):
        block = MambaBlock(d_model=8)
        x = np.random.randn(1, 5, 8).astype(np.float32)
        out = block(x)
        assert not np.any(np.isnan(out))

    @pytest.mark.unit
    def test_callable_equals_forward(self):
        block = MambaBlock(d_model=8, d_state=4)
        x = np.random.randn(1, 4, 8).astype(np.float32)
        out_call = block(x)
        out_forward = block.forward(x)
        np.testing.assert_array_equal(out_call, out_forward)

    @pytest.mark.unit
    def test_default_d_inner(self):
        block = MambaBlock(d_model=16)
        assert block.d_inner == 32  # 2 * d_model

    @pytest.mark.unit
    def test_custom_d_inner(self):
        block = MambaBlock(d_model=16, d_inner=48)
        assert block.d_inner == 48

    @pytest.mark.unit
    def test_silu_activation(self):
        """SiLU(x) = x * sigmoid(x), should be ~0 at x=0, ~x at large x."""
        block = MambaBlock(d_model=8)
        x_zero = np.zeros((1, 1, 1))
        assert block._silu(x_zero).item() == pytest.approx(0.0, abs=1e-7)

        x_large = np.array([[[10.0]]])
        silu_val = block._silu(x_large).item()
        assert silu_val == pytest.approx(10.0, abs=0.01)  # sigmoid(10) ~ 1


class TestMambaForward:
    @pytest.mark.unit
    def test_stacked_shape_preserved(self):
        x = np.random.randn(1, 6, 16).astype(np.float32)
        out = mamba_forward(x, n_layers=2)
        assert out.shape == x.shape

    @pytest.mark.unit
    def test_single_layer(self):
        x = np.random.randn(1, 4, 8).astype(np.float32)
        out = mamba_forward(x, n_layers=1, d_model=8)
        assert out.shape == x.shape
        assert not np.any(np.isnan(out))

    @pytest.mark.unit
    def test_inferred_d_model(self):
        """d_model should be inferred from input shape when not specified."""
        x = np.random.randn(1, 4, 32).astype(np.float32)
        out = mamba_forward(x, n_layers=1)
        assert out.shape == x.shape


class TestFlashAttention:
    @pytest.mark.unit
    def test_output_matches_standard(self):
        from codomyrmex.neural.flash_attention import verify_flash_vs_standard

        Q = np.random.randn(1, 8, 16).astype(np.float32)
        K = np.random.randn(1, 8, 16).astype(np.float32)
        V = np.random.randn(1, 8, 16).astype(np.float32)
        max_err, _, _ = verify_flash_vs_standard(Q, K, V)
        assert max_err < 1e-3, f"Flash attention error too large: {max_err}"

    @pytest.mark.unit
    def test_flash_output_shape(self):
        from codomyrmex.neural.flash_attention import flash_attention

        Q = np.random.randn(1, 10, 16).astype(np.float32)
        K = np.random.randn(1, 10, 16).astype(np.float32)
        V = np.random.randn(1, 10, 16).astype(np.float32)
        out = flash_attention(Q, K, V, block_size=4)
        assert out.shape == (1, 10, 16)

    @pytest.mark.unit
    def test_flash_causal_mask(self):
        from codomyrmex.neural.flash_attention import flash_attention

        seq = 8
        Q = np.random.randn(1, seq, 16).astype(np.float32)
        K = np.random.randn(1, seq, 16).astype(np.float32)
        V = np.random.randn(1, seq, 16).astype(np.float32)
        out = flash_attention(Q, K, V, causal=True)
        assert out.shape == (1, seq, 16)
        assert not np.any(np.isnan(out))

    @pytest.mark.unit
    def test_flash_multihead_shape(self):
        """Test 4D input (batch, heads, seq, d_k)."""
        from codomyrmex.neural.flash_attention import flash_attention

        Q = np.random.randn(2, 4, 8, 16).astype(np.float32)
        K = np.random.randn(2, 4, 8, 16).astype(np.float32)
        V = np.random.randn(2, 4, 8, 16).astype(np.float32)
        out = flash_attention(Q, K, V, block_size=4)
        assert out.shape == (2, 4, 8, 16)

    @pytest.mark.unit
    def test_flash_block_size_one(self):
        """Edge case: block_size=1 processes one element at a time."""
        from codomyrmex.neural.flash_attention import flash_attention

        Q = np.random.randn(1, 4, 8).astype(np.float32)
        K = np.random.randn(1, 4, 8).astype(np.float32)
        V = np.random.randn(1, 4, 8).astype(np.float32)
        out = flash_attention(Q, K, V, block_size=1)
        assert out.shape == (1, 4, 8)
        assert not np.any(np.isnan(out))

    @pytest.mark.unit
    def test_flash_causal_first_token(self):
        """First token in causal mode should only attend to itself."""
        from codomyrmex.neural.flash_attention import flash_attention

        np.random.seed(42)
        seq = 4
        d = 8
        Q = np.random.randn(1, seq, d).astype(np.float32)
        K = np.random.randn(1, seq, d).astype(np.float32)
        V = np.random.randn(1, seq, d).astype(np.float32)

        out = flash_attention(Q, K, V, causal=True, block_size=2)

        # First token output should equal V[0] (only attends to itself)
        # softmax of single element = 1.0
        np.testing.assert_allclose(out[0, 0, :], V[0, 0, :], atol=1e-5)

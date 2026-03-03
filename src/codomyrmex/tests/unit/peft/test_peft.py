"""
Unit tests for the peft module.

Tests cover:
- LoRA adapter: zero init, output shape, parameter count
- Prefix Tuning: token prepending, output shape
- IA3: ones initialization, rescaling modes
- Parameter efficiency comparison
- MCP tool interface
"""

import numpy as np
import pytest

from codomyrmex.peft import IA3Adapter, LoRAAdapter, PEFTConfig, PrefixTuningAdapter

# ---------------------------------------------------------------------------
# LoRA Adapter
# ---------------------------------------------------------------------------


class TestLoRAAdapter:
    """LoRA low-rank adaptation tests."""

    @pytest.mark.unit
    def test_lora_b_zero_init(self):
        """Initial LoRA output should be zero because B is initialized to zeros."""
        adapter = LoRAAdapter(d_in=64, d_out=64, rank=4, alpha=8.0)
        x = np.random.randn(2, 10, 64)
        output = adapter.adapt(x)
        np.testing.assert_array_almost_equal(output, np.zeros_like(output))

    @pytest.mark.unit
    def test_lora_with_base_output(self):
        """With B=0, adapt(x, base_output) should return base_output unchanged."""
        adapter = LoRAAdapter(d_in=64, d_out=64, rank=4)
        x = np.random.randn(2, 10, 64)
        base = np.random.randn(2, 10, 64)
        output = adapter.adapt(x, base_output=base)
        np.testing.assert_array_almost_equal(output, base)

    @pytest.mark.unit
    def test_lora_nonzero_b_produces_output(self):
        """When B is non-zero, LoRA should produce non-zero delta."""
        adapter = LoRAAdapter(d_in=32, d_out=32, rank=4)
        adapter.b_matrix = np.random.randn(32, 4) * 0.01  # override zero init
        x = np.random.randn(1, 5, 32)
        output = adapter.adapt(x)
        assert not np.allclose(output, 0.0)

    @pytest.mark.unit
    def test_lora_output_shape(self):
        """LoRA output should match (batch, seq, d_out)."""
        adapter = LoRAAdapter(d_in=64, d_out=128, rank=8)
        x = np.random.randn(3, 12, 64)
        output = adapter.adapt(x)
        assert output.shape == (3, 12, 128)

    @pytest.mark.unit
    def test_lora_trainable_params(self):
        """Trainable params = rank * d_in + d_out * rank."""
        adapter = LoRAAdapter(d_in=512, d_out=512, rank=4)
        assert adapter.trainable_params == 4 * 512 + 512 * 4  # 4096

    @pytest.mark.unit
    def test_lora_scaling_factor(self):
        """Scaling should be alpha/rank."""
        adapter = LoRAAdapter(d_in=64, d_out=64, rank=4, alpha=16.0)
        assert adapter.scaling == 16.0 / 4  # 4.0

    @pytest.mark.unit
    def test_lora_a_shape(self):
        """A matrix should be (rank, d_in)."""
        adapter = LoRAAdapter(d_in=128, d_out=64, rank=8)
        assert adapter.a_matrix.shape == (8, 128)

    @pytest.mark.unit
    def test_lora_b_shape(self):
        """B matrix should be (d_out, rank)."""
        adapter = LoRAAdapter(d_in=128, d_out=64, rank=8)
        assert adapter.b_matrix.shape == (64, 8)


# ---------------------------------------------------------------------------
# Prefix Tuning Adapter
# ---------------------------------------------------------------------------


class TestPrefixTuningAdapter:
    """Prefix tuning virtual token tests."""

    @pytest.mark.unit
    def test_prefix_prepends_tokens(self):
        """Output sequence length should be n_prefix + input seq_len."""
        adapter = PrefixTuningAdapter(d_model=64, n_prefix=10, n_layers=2)
        x = np.random.randn(2, 20, 64)  # batch=2, seq=20, dim=64
        output = adapter.adapt(x, layer_idx=0)
        assert output.shape == (2, 30, 64)  # 10 prefix + 20 original

    @pytest.mark.unit
    def test_prefix_preserves_original(self):
        """Original tokens should be preserved after prefix."""
        adapter = PrefixTuningAdapter(d_model=32, n_prefix=5, n_layers=1)
        x = np.random.randn(1, 10, 32)
        output = adapter.adapt(x, layer_idx=0)
        np.testing.assert_array_equal(output[:, 5:, :], x)

    @pytest.mark.unit
    def test_prefix_different_layers(self):
        """Different layer indices should use different prefix vectors."""
        adapter = PrefixTuningAdapter(d_model=32, n_prefix=5, n_layers=4)
        x = np.random.randn(1, 10, 32)
        out0 = adapter.adapt(x, layer_idx=0)
        out1 = adapter.adapt(x, layer_idx=1)
        # Prefix portions should differ
        assert not np.array_equal(out0[:, :5, :], out1[:, :5, :])

    @pytest.mark.unit
    def test_prefix_trainable_params(self):
        """Trainable params = 2 * n_layers * n_prefix * d_model."""
        adapter = PrefixTuningAdapter(d_model=256, n_prefix=10, n_layers=6)
        expected = 2 * 6 * 10 * 256  # 30720
        assert adapter.trainable_params == expected

    @pytest.mark.unit
    def test_prefix_keys_shape(self):
        adapter = PrefixTuningAdapter(d_model=64, n_prefix=8, n_layers=3)
        assert adapter.prefix_keys.shape == (3, 8, 64)

    @pytest.mark.unit
    def test_prefix_values_shape(self):
        adapter = PrefixTuningAdapter(d_model=64, n_prefix=8, n_layers=3)
        assert adapter.prefix_values.shape == (3, 8, 64)

    @pytest.mark.unit
    def test_prefix_batch_dimension(self):
        """Prefix should be tiled across batch dimension."""
        adapter = PrefixTuningAdapter(d_model=16, n_prefix=3, n_layers=1)
        x = np.random.randn(4, 5, 16)
        output = adapter.adapt(x)
        assert output.shape[0] == 4  # batch preserved


# ---------------------------------------------------------------------------
# IA3 Adapter
# ---------------------------------------------------------------------------


class TestIA3Adapter:
    """IA3 element-wise rescaling tests."""

    @pytest.mark.unit
    def test_ia3_ones_init_no_change(self):
        """IA3 initialized with ones should not change input."""
        adapter = IA3Adapter(d_model=64)
        x = np.random.randn(2, 10, 64)
        output_keys = adapter.adapt(x, mode="keys")
        np.testing.assert_array_equal(output_keys, x)

    @pytest.mark.unit
    def test_ia3_ones_init_values(self):
        """Values mode with ones should not change input."""
        adapter = IA3Adapter(d_model=64)
        x = np.random.randn(2, 10, 64)
        output = adapter.adapt(x, mode="values")
        np.testing.assert_array_equal(output, x)

    @pytest.mark.unit
    def test_ia3_ones_init_ffn(self):
        """FFN mode with ones should not change input."""
        adapter = IA3Adapter(d_model=64, d_ff=256)
        x = np.random.randn(2, 10, 256)
        output = adapter.adapt(x, mode="ffn")
        np.testing.assert_array_equal(output, x)

    @pytest.mark.unit
    def test_ia3_nonzero_scaling(self):
        """Non-unit scaling should change output."""
        adapter = IA3Adapter(d_model=32)
        adapter.l_k = np.full(32, 2.0)
        x = np.random.randn(1, 5, 32)
        output = adapter.adapt(x, mode="keys")
        np.testing.assert_array_almost_equal(output, x * 2.0)

    @pytest.mark.unit
    def test_ia3_trainable_params(self):
        """Trainable params = d_model + d_model + d_ff."""
        adapter = IA3Adapter(d_model=256, d_ff=1024)
        assert adapter.trainable_params == 256 + 256 + 1024  # 1536

    @pytest.mark.unit
    def test_ia3_default_d_ff(self):
        """Default d_ff should be 4 * d_model."""
        adapter = IA3Adapter(d_model=128)
        assert adapter.d_ff == 512

    @pytest.mark.unit
    def test_ia3_unknown_mode_passthrough(self):
        """Unknown mode should return input unchanged."""
        adapter = IA3Adapter(d_model=32)
        x = np.random.randn(1, 5, 32)
        output = adapter.adapt(x, mode="unknown")
        np.testing.assert_array_equal(output, x)


# ---------------------------------------------------------------------------
# Parameter Efficiency Comparison
# ---------------------------------------------------------------------------


class TestParameterEfficiency:
    """Cross-method parameter count comparison."""

    @pytest.mark.unit
    def test_trainable_params_reduction(self):
        """All PEFT methods should have fewer params than full fine-tuning."""
        d_model = 512
        full_params = d_model * d_model  # 262144

        lora = LoRAAdapter(d_in=d_model, d_out=d_model, rank=4)
        prefix = PrefixTuningAdapter(d_model=d_model, n_prefix=10, n_layers=2)
        ia3 = IA3Adapter(d_model=d_model)

        assert lora.trainable_params < full_params
        assert prefix.trainable_params < full_params
        assert ia3.trainable_params < full_params

    @pytest.mark.unit
    def test_ia3_most_efficient(self):
        """IA3 should be more parameter-efficient than LoRA for typical dims."""
        d_model = 512
        lora = LoRAAdapter(d_in=d_model, d_out=d_model, rank=4)
        ia3 = IA3Adapter(d_model=d_model)
        assert ia3.trainable_params < lora.trainable_params

    @pytest.mark.unit
    def test_lora_scales_with_rank(self):
        """Higher rank means more trainable parameters."""
        low = LoRAAdapter(d_in=256, d_out=256, rank=2)
        high = LoRAAdapter(d_in=256, d_out=256, rank=16)
        assert high.trainable_params > low.trainable_params


# ---------------------------------------------------------------------------
# PEFTConfig
# ---------------------------------------------------------------------------


class TestPEFTConfig:
    """PEFTConfig dataclass tests."""

    @pytest.mark.unit
    def test_default_config(self):
        config = PEFTConfig()
        assert config.method == "lora"
        assert config.rank == 4
        assert config.alpha == 8.0
        assert config.num_virtual_tokens == 10

    @pytest.mark.unit
    def test_custom_config(self):
        config = PEFTConfig(method="ia3", rank=8, alpha=16.0)
        assert config.method == "ia3"
        assert config.rank == 8

"""
Unit tests for the LoRA (Low-Rank Adaptation) module.

Tests cover:
- LoRAConfig scaling property
- B initialization to zero (initial delta = 0)
- Forward pass matches formula: output = base + B @ A * scaling
- Merge produces W_0 + delta
- Merged forward equals unmerged forward
- Rank of delta <= r
- Parameter count reduction
- apply_lora and merge_lora convenience functions
- MCP tool interface
"""

import numpy as np
import pytest

from codomyrmex.lora import LoRAConfig, LoRALayer, apply_lora, merge_lora

# ---------------------------------------------------------------------------
# LoRAConfig
# ---------------------------------------------------------------------------


class TestLoRAConfig:
    """Tests for LoRAConfig dataclass."""

    @pytest.mark.unit
    def test_default_config(self):
        config = LoRAConfig()
        assert config.rank == 4
        assert config.alpha == 8.0
        assert config.dropout == 0.0
        assert config.target_modules == []

    @pytest.mark.unit
    def test_scaling_property(self):
        config = LoRAConfig(rank=4, alpha=8.0)
        assert config.scaling == 2.0

    @pytest.mark.unit
    def test_scaling_with_different_values(self):
        config = LoRAConfig(rank=8, alpha=16.0)
        assert config.scaling == 2.0

        config2 = LoRAConfig(rank=2, alpha=1.0)
        assert config2.scaling == 0.5


# ---------------------------------------------------------------------------
# LoRALayer initialization
# ---------------------------------------------------------------------------


class TestLoRALayerInit:
    """Tests for LoRALayer initialization."""

    @pytest.mark.unit
    def test_B_initialized_to_zero(self):
        """B must be zero so initial LoRA delta is zero."""
        np.random.seed(42)
        W = np.random.randn(64, 32)
        layer = LoRALayer(W)
        np.testing.assert_array_equal(layer.B, np.zeros((64, layer.config.rank)))

    @pytest.mark.unit
    def test_initial_delta_is_zero(self):
        """Since B=0, B @ A * scaling should be zero."""
        np.random.seed(42)
        W = np.random.randn(64, 32)
        layer = LoRALayer(W)
        delta = layer.get_delta()
        np.testing.assert_allclose(delta, np.zeros_like(delta), atol=1e-15)

    @pytest.mark.unit
    def test_A_shape(self):
        W = np.random.randn(64, 32)
        config = LoRAConfig(rank=8)
        layer = LoRALayer(W, config)
        assert layer.A.shape == (8, 32)

    @pytest.mark.unit
    def test_B_shape(self):
        W = np.random.randn(64, 32)
        config = LoRAConfig(rank=8)
        layer = LoRALayer(W, config)
        assert layer.B.shape == (64, 8)

    @pytest.mark.unit
    def test_W0_is_copy(self):
        """W_0 should be a copy, not a reference."""
        W = np.random.randn(16, 8)
        layer = LoRALayer(W)
        W[0, 0] = 999.0
        assert layer.W_0[0, 0] != 999.0


# ---------------------------------------------------------------------------
# LoRALayer forward pass
# ---------------------------------------------------------------------------


class TestLoRALayerForward:
    """Tests for LoRALayer forward computation."""

    @pytest.mark.unit
    def test_lora_output_matches_formula(self):
        """output = x @ W_0^T + x @ A^T @ B^T * scaling."""
        np.random.seed(42)
        d, k, r = 16, 8, 4
        W = np.random.randn(d, k)
        config = LoRAConfig(rank=r, alpha=8.0)
        layer = LoRALayer(W, config)

        # set B to non-zero for meaningful test
        layer.B = np.random.randn(d, r) * 0.1

        x = np.random.randn(3, k)  # batch of 3

        # Manual calculation
        base = x @ layer.W_0.T
        lora_delta = x @ layer.A.T @ layer.B.T * config.scaling
        expected = base + lora_delta

        actual = layer.forward(x)
        np.testing.assert_allclose(actual, expected, atol=1e-12)

    @pytest.mark.unit
    def test_initial_forward_equals_base(self):
        """With B=0, forward should equal base W_0 multiplication."""
        np.random.seed(42)
        W = np.random.randn(16, 8)
        layer = LoRALayer(W)
        x = np.random.randn(5, 8)

        base = x @ W.T
        actual = layer.forward(x)
        np.testing.assert_allclose(actual, base, atol=1e-12)

    @pytest.mark.unit
    def test_call_delegates_to_forward(self):
        np.random.seed(42)
        W = np.random.randn(16, 8)
        layer = LoRALayer(W)
        x = np.random.randn(2, 8)
        np.testing.assert_array_equal(layer(x), layer.forward(x))


# ---------------------------------------------------------------------------
# Merge / unmerge
# ---------------------------------------------------------------------------


class TestLoRAMerge:
    """Tests for merge and unmerge operations."""

    @pytest.mark.unit
    def test_merge_changes_W0(self):
        """After merge, W_0 should be W_0_original + delta."""
        np.random.seed(42)
        d, k, r = 16, 8, 4
        W = np.random.randn(d, k)
        config = LoRAConfig(rank=r, alpha=8.0)
        layer = LoRALayer(W, config)
        layer.B = np.random.randn(d, r) * 0.1

        W0_before = layer.W_0.copy()
        delta = layer.get_delta()
        layer.merge()

        np.testing.assert_allclose(layer.W_0, W0_before + delta, atol=1e-12)

    @pytest.mark.unit
    def test_merged_forward_equals_unmerged(self):
        """Merged and unmerged should give identical output."""
        np.random.seed(42)
        d, k, r = 32, 16, 4
        W = np.random.randn(d, k)
        config = LoRAConfig(rank=r, alpha=8.0)
        layer = LoRALayer(W, config)
        layer.B = np.random.randn(d, r) * 0.1

        x = np.random.randn(5, k)
        unmerged_output = layer.forward(x)

        layer.merge()
        merged_output = layer.forward(x)

        np.testing.assert_allclose(merged_output, unmerged_output, atol=1e-10)

    @pytest.mark.unit
    def test_merge_is_idempotent(self):
        """Calling merge twice should not change the result."""
        np.random.seed(42)
        W = np.random.randn(16, 8)
        layer = LoRALayer(W)
        layer.B = np.random.randn(16, 4) * 0.1

        layer.merge()
        W_after_first = layer.W_0.copy()
        layer.merge()
        np.testing.assert_array_equal(layer.W_0, W_after_first)

    @pytest.mark.unit
    def test_unmerge_restores_weights(self):
        np.random.seed(42)
        W = np.random.randn(16, 8)
        original_W = W.copy()
        layer = LoRALayer(W)
        layer.B = np.random.randn(16, 4) * 0.1
        layer.merge()

        layer.unmerge(original_W)
        np.testing.assert_allclose(layer.W_0, original_W, atol=1e-15)
        assert not layer._merged


# ---------------------------------------------------------------------------
# Rank and parameter count
# ---------------------------------------------------------------------------


class TestLoRARankAndParams:
    """Tests for rank preservation and parameter efficiency."""

    @pytest.mark.unit
    def test_rank_preserved(self):
        """rank(B @ A) <= r."""
        np.random.seed(42)
        d, k, r = 64, 32, 4
        W = np.random.randn(d, k)
        config = LoRAConfig(rank=r)
        layer = LoRALayer(W, config)
        layer.B = np.random.randn(d, r) * 0.1

        assert layer.effective_rank <= r

    @pytest.mark.unit
    def test_parameter_count_reduction(self):
        """LoRA params = r*k + d*r should be much less than d*k."""
        d, k, r = 1024, 512, 4
        total_params = d * k  # 524288
        lora_params = r * k + d * r  # 2048 + 4096 = 6144
        assert lora_params < total_params
        reduction_pct = (1 - lora_params / total_params) * 100
        assert reduction_pct > 95  # >95% reduction for these dimensions

    @pytest.mark.unit
    def test_effective_rank_zero_at_init(self):
        """Initial effective rank should be 0 since B=0."""
        np.random.seed(42)
        W = np.random.randn(16, 8)
        layer = LoRALayer(W)
        assert layer.effective_rank == 0


# ---------------------------------------------------------------------------
# Convenience functions
# ---------------------------------------------------------------------------


class TestConvenienceFunctions:
    """Tests for apply_lora and merge_lora."""

    @pytest.mark.unit
    def test_apply_lora_returns_layer(self):
        W = np.random.randn(16, 8)
        layer = apply_lora(W, rank=2, alpha=4.0)
        assert isinstance(layer, LoRALayer)
        assert layer.config.rank == 2
        assert layer.config.alpha == 4.0

    @pytest.mark.unit
    def test_merge_lora_returns_merged_weight(self):
        np.random.seed(42)
        W = np.random.randn(16, 8)
        layer = apply_lora(W, rank=4, alpha=8.0)
        layer.B = np.random.randn(16, 4) * 0.1

        merged_W = merge_lora(layer)
        assert merged_W.shape == W.shape
        assert layer._merged  # side effect: layer is now merged


# ---------------------------------------------------------------------------
# MCP tool
# ---------------------------------------------------------------------------


class TestMCPTool:
    """Tests for LoRA MCP tool interface."""

    @pytest.mark.unit
    def test_lora_apply_tool(self):
        from codomyrmex.lora.mcp_tools import lora_apply

        result = lora_apply(weight_shape=[256, 128], rank=8, alpha=16.0)
        assert result["status"] == "success"
        assert result["rank"] == 8
        assert result["scaling"] == 2.0
        assert result["lora_params"] == 8 * 128 + 256 * 8  # 3072
        assert result["total_params"] == 256 * 128  # 32768
        assert result["parameter_reduction_pct"] > 90

    @pytest.mark.unit
    def test_lora_apply_tool_has_mcp_metadata(self):
        from codomyrmex.lora.mcp_tools import lora_apply

        assert hasattr(lora_apply, "_mcp_tool")
        assert lora_apply._mcp_tool["category"] == "lora"

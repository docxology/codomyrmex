"""
Unit tests for the Small Language Model (SLM) module.

Tests cover:
- Output shape (batch, seq, vocab) for forward pass
- Causal mask is lower triangular
- Greedy decode returns correct length list
- Logits are finite
- Config defaults
- Sequence length validation
- MCP tool interface
"""

import numpy as np
import pytest

from codomyrmex.slm import SLM, SLMConfig, causal_mask


# ---------------------------------------------------------------------------
# causal_mask
# ---------------------------------------------------------------------------


class TestCausalMask:
    """Tests for the causal attention mask."""

    @pytest.mark.unit
    def test_causal_mask_shape(self):
        """Causal mask should be (seq_len, seq_len)."""
        mask = causal_mask(10)
        assert mask.shape == (10, 10)

    @pytest.mark.unit
    def test_causal_mask_is_lower_triangular(self):
        """Causal mask should be True on and below the diagonal."""
        mask = causal_mask(5)
        expected = np.tril(np.ones((5, 5), dtype=bool))
        np.testing.assert_array_equal(mask, expected)

    @pytest.mark.unit
    def test_causal_mask_diagonal_is_true(self):
        """Diagonal elements should all be True (token can attend to itself)."""
        mask = causal_mask(8)
        for i in range(8):
            assert mask[i, i] is np.bool_(True)

    @pytest.mark.unit
    def test_causal_mask_upper_triangle_is_false(self):
        """Upper triangle (future tokens) should all be False."""
        mask = causal_mask(6)
        for i in range(6):
            for j in range(i + 1, 6):
                assert mask[i, j] is np.bool_(False)

    @pytest.mark.unit
    def test_causal_mask_size_one(self):
        """Size-1 mask should be [[True]]."""
        mask = causal_mask(1)
        assert mask.shape == (1, 1)
        assert mask[0, 0] is np.bool_(True)


# ---------------------------------------------------------------------------
# SLMConfig
# ---------------------------------------------------------------------------


class TestSLMConfig:
    """Tests for SLM configuration."""

    @pytest.mark.unit
    def test_default_config(self):
        config = SLMConfig()
        assert config.vocab_size == 1000
        assert config.d_model == 64
        assert config.n_heads == 4
        assert config.n_layers == 2
        assert config.d_ff == 256
        assert config.max_seq_len == 128

    @pytest.mark.unit
    def test_custom_config(self):
        config = SLMConfig(vocab_size=500, d_model=32, n_heads=2, n_layers=1)
        assert config.vocab_size == 500
        assert config.d_model == 32


# ---------------------------------------------------------------------------
# SLM Forward
# ---------------------------------------------------------------------------


class TestSLMForward:
    """Tests for SLM forward pass."""

    @pytest.mark.unit
    def test_forward_output_shape(self):
        """Output should be (batch, seq, vocab_size)."""
        np.random.seed(42)
        config = SLMConfig(vocab_size=100, d_model=32, n_heads=2, n_layers=1, d_ff=64)
        model = SLM(config)
        token_ids = np.random.randint(0, 100, (2, 5))
        logits = model.forward(token_ids)
        assert logits.shape == (2, 5, 100)

    @pytest.mark.unit
    def test_forward_single_token(self):
        """Should work with a single token sequence."""
        np.random.seed(42)
        config = SLMConfig(vocab_size=50, d_model=16, n_heads=2, n_layers=1, d_ff=32)
        model = SLM(config)
        token_ids = np.array([[7]])
        logits = model.forward(token_ids)
        assert logits.shape == (1, 1, 50)

    @pytest.mark.unit
    def test_forward_logits_are_finite(self):
        """All logit values should be finite (no NaN or Inf)."""
        np.random.seed(42)
        config = SLMConfig(vocab_size=50, d_model=16, n_heads=2, n_layers=1, d_ff=32)
        model = SLM(config)
        token_ids = np.random.randint(0, 50, (3, 10))
        logits = model.forward(token_ids)
        assert np.all(np.isfinite(logits))

    @pytest.mark.unit
    def test_forward_callable(self):
        """SLM should be callable (via __call__)."""
        np.random.seed(42)
        config = SLMConfig(vocab_size=50, d_model=16, n_heads=2, n_layers=1, d_ff=32)
        model = SLM(config)
        token_ids = np.random.randint(0, 50, (1, 4))
        logits = model(token_ids)
        assert logits.shape == (1, 4, 50)

    @pytest.mark.unit
    def test_forward_exceeds_max_seq_len_raises(self):
        """Should raise ValueError if sequence exceeds max_seq_len."""
        np.random.seed(42)
        config = SLMConfig(
            vocab_size=50, d_model=16, n_heads=2, n_layers=1, d_ff=32, max_seq_len=10
        )
        model = SLM(config)
        token_ids = np.random.randint(0, 50, (1, 15))  # 15 > 10
        with pytest.raises(ValueError, match="max_seq_len"):
            model.forward(token_ids)


# ---------------------------------------------------------------------------
# SLM Generate
# ---------------------------------------------------------------------------


class TestSLMGenerate:
    """Tests for SLM greedy generation."""

    @pytest.mark.unit
    def test_generate_returns_list(self):
        """Generate should return a list of integers."""
        np.random.seed(42)
        config = SLMConfig(vocab_size=50, d_model=16, n_heads=2, n_layers=1, d_ff=32)
        model = SLM(config)
        result = model.generate([1, 2, 3], max_new_tokens=5)
        assert isinstance(result, list)
        assert all(isinstance(t, int) for t in result)

    @pytest.mark.unit
    def test_generate_correct_length(self):
        """Generated sequence should be prompt_len + max_new_tokens."""
        np.random.seed(42)
        config = SLMConfig(vocab_size=50, d_model=16, n_heads=2, n_layers=1, d_ff=32)
        model = SLM(config)
        prompt = [1, 2, 3]
        max_new = 7
        result = model.generate(prompt, max_new_tokens=max_new)
        assert len(result) == len(prompt) + max_new

    @pytest.mark.unit
    def test_generate_preserves_prompt(self):
        """Generated sequence should start with the original prompt."""
        np.random.seed(42)
        config = SLMConfig(vocab_size=50, d_model=16, n_heads=2, n_layers=1, d_ff=32)
        model = SLM(config)
        prompt = [5, 10, 15]
        result = model.generate(prompt, max_new_tokens=3)
        assert result[:3] == prompt

    @pytest.mark.unit
    def test_generate_tokens_in_vocab_range(self):
        """All generated tokens should be in [0, vocab_size)."""
        np.random.seed(42)
        config = SLMConfig(vocab_size=50, d_model=16, n_heads=2, n_layers=1, d_ff=32)
        model = SLM(config)
        result = model.generate([1], max_new_tokens=20)
        assert all(0 <= t < 50 for t in result)

    @pytest.mark.unit
    def test_generate_deterministic_with_seed(self):
        """Same seed should produce same generation."""
        config = SLMConfig(vocab_size=50, d_model=16, n_heads=2, n_layers=1, d_ff=32)

        np.random.seed(42)
        model1 = SLM(config)
        out1 = model1.generate([1, 2], max_new_tokens=5)

        np.random.seed(42)
        model2 = SLM(config)
        out2 = model2.generate([1, 2], max_new_tokens=5)

        assert out1 == out2


# ---------------------------------------------------------------------------
# MCP Tools
# ---------------------------------------------------------------------------


class TestMCPTools:
    """Tests for SLM MCP tool interface."""

    @pytest.mark.unit
    def test_slm_generate_tool(self):
        from codomyrmex.slm.mcp_tools import slm_generate

        result = slm_generate(
            prompt_tokens=[1, 2, 3],
            max_new_tokens=5,
            vocab_size=50,
            d_model=16,
            n_heads=2,
            n_layers=1,
            seed=42,
        )
        assert result["status"] == "success"
        assert len(result["generated"]) == 5
        assert result["full_sequence"][:3] == [1, 2, 3]

    @pytest.mark.unit
    def test_slm_forward_tool(self):
        from codomyrmex.slm.mcp_tools import slm_forward

        result = slm_forward(
            batch_size=2,
            seq_len=4,
            vocab_size=50,
            d_model=16,
            n_heads=2,
            n_layers=1,
            seed=42,
        )
        assert result["status"] == "success"
        assert result["output_shape"] == [2, 4, 50]

    @pytest.mark.unit
    def test_slm_generate_tool_has_mcp_metadata(self):
        from codomyrmex.slm.mcp_tools import slm_generate

        assert hasattr(slm_generate, "_mcp_tool")
        assert slm_generate._mcp_tool["category"] == "slm"

    @pytest.mark.unit
    def test_slm_forward_tool_has_mcp_metadata(self):
        from codomyrmex.slm.mcp_tools import slm_forward

        assert hasattr(slm_forward, "_mcp_tool")
        assert slm_forward._mcp_tool["category"] == "slm"

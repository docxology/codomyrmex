"""Tests for the model_merger module."""

import pytest

try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False

if not HAS_NUMPY:
    pytest.skip("numpy not installed", allow_module_level=True)

try:
    from codomyrmex.model_merger import (
        ModelMerger,
        linear_interpolate,
        model_soup,
        slerp,
    )
    HAS_MODULE = True
except ImportError:
    HAS_MODULE = False

if not HAS_MODULE:
    pytest.skip("model_merger module not available", allow_module_level=True)


@pytest.mark.unit
class TestSlerp:
    """Test suite for SLERP interpolation."""

    def test_slerp_at_t0_equals_v0(self):
        """SLERP at t=0 returns v0."""
        v0 = np.array([1.0, 0.0, 0.0])
        v1 = np.array([0.0, 1.0, 0.0])
        result = slerp(v0, v1, t=0.0)
        np.testing.assert_allclose(result, v0, atol=1e-6)

    def test_slerp_at_t1_equals_v1(self):
        """SLERP at t=1 returns v1."""
        v0 = np.array([1.0, 0.0, 0.0])
        v1 = np.array([0.0, 1.0, 0.0])
        result = slerp(v0, v1, t=1.0)
        np.testing.assert_allclose(result, v1, atol=1e-6)

    def test_slerp_at_t05_between_v0_v1(self):
        """SLERP at t=0.5 is between v0 and v1 in norm."""
        v0 = np.array([1.0, 0.0])
        v1 = np.array([0.0, 1.0])
        result = slerp(v0, v1, t=0.5)

        # Result norm should be the midpoint of the two norms
        assert np.linalg.norm(result) == pytest.approx(1.0, abs=0.1)
        # Both components should be positive (interpolating between axes)
        assert result[0] > 0
        assert result[1] > 0

    def test_slerp_preserves_shape(self):
        """SLERP preserves input array shape."""
        v0 = np.random.randn(3, 4)
        v1 = np.random.randn(3, 4)
        result = slerp(v0, v1, t=0.5)
        assert result.shape == (3, 4)

    def test_slerp_parallel_vectors_fallback(self):
        """SLERP falls back to linear interp for parallel vectors."""
        v0 = np.array([1.0, 0.0, 0.0])
        v1 = np.array([2.0, 0.0, 0.0])
        result = slerp(v0, v1, t=0.5)
        # Should be ~1.5 in magnitude
        assert np.linalg.norm(result) == pytest.approx(1.5, abs=0.1)

    def test_slerp_magnitude_interpolation(self):
        """SLERP linearly interpolates magnitudes."""
        v0 = np.array([2.0, 0.0])
        v1 = np.array([0.0, 4.0])
        result = slerp(v0, v1, t=0.5)
        expected_norm = 0.5 * 2.0 + 0.5 * 4.0  # = 3.0
        assert np.linalg.norm(result) == pytest.approx(expected_norm, abs=0.1)


@pytest.mark.unit
class TestLinearInterpolate:
    """Test suite for linear parameter interpolation."""

    def test_linear_interpolate_midpoint(self):
        """Linear interpolation at alpha=0.5 gives midpoint."""
        params_a = {"w": np.array([0.0, 0.0])}
        params_b = {"w": np.array([2.0, 4.0])}
        merged = linear_interpolate(params_a, params_b, alpha=0.5)
        np.testing.assert_allclose(merged["w"], [1.0, 2.0])

    def test_linear_interpolate_alpha_0(self):
        """Alpha=0 returns params_a."""
        params_a = {"w": np.array([1.0, 2.0])}
        params_b = {"w": np.array([3.0, 4.0])}
        merged = linear_interpolate(params_a, params_b, alpha=0.0)
        np.testing.assert_allclose(merged["w"], [1.0, 2.0])

    def test_linear_interpolate_alpha_1(self):
        """Alpha=1 returns params_b."""
        params_a = {"w": np.array([1.0, 2.0])}
        params_b = {"w": np.array([3.0, 4.0])}
        merged = linear_interpolate(params_a, params_b, alpha=1.0)
        np.testing.assert_allclose(merged["w"], [3.0, 4.0])

    def test_missing_key_in_b_preserves_a(self):
        """Keys only in params_a are copied unchanged."""
        params_a = {"w1": np.array([1.0]), "w2": np.array([2.0])}
        params_b = {"w1": np.array([3.0])}
        merged = linear_interpolate(params_a, params_b, alpha=0.5)
        np.testing.assert_allclose(merged["w1"], [2.0])
        np.testing.assert_allclose(merged["w2"], [2.0])

    def test_multiple_keys(self):
        """Interpolation works across multiple parameter keys."""
        params_a = {"layer1": np.zeros(3), "layer2": np.ones(2)}
        params_b = {"layer1": np.ones(3), "layer2": np.full(2, 3.0)}
        merged = linear_interpolate(params_a, params_b, alpha=0.5)
        np.testing.assert_allclose(merged["layer1"], [0.5, 0.5, 0.5])
        np.testing.assert_allclose(merged["layer2"], [2.0, 2.0])


@pytest.mark.unit
class TestModelSoup:
    """Test suite for model soup (weighted averaging)."""

    def test_model_soup_uniform_average(self):
        """Uniform soup averages all models equally."""
        dicts = [
            {"w": np.array([0.0, 0.0])},
            {"w": np.array([2.0, 4.0])},
            {"w": np.array([4.0, 8.0])},
        ]
        result = model_soup(dicts)
        np.testing.assert_allclose(result["w"], [2.0, 4.0])

    def test_model_soup_weighted(self):
        """Weighted soup respects provided weights."""
        dicts = [
            {"w": np.array([0.0])},
            {"w": np.array([10.0])},
        ]
        result = model_soup(dicts, weights=[1.0, 3.0])
        # (0.0 * 0.25 + 10.0 * 0.75) = 7.5
        np.testing.assert_allclose(result["w"], [7.5])

    def test_model_soup_single_model(self):
        """Soup of one model returns that model."""
        dicts = [{"w": np.array([1.0, 2.0, 3.0])}]
        result = model_soup(dicts)
        np.testing.assert_allclose(result["w"], [1.0, 2.0, 3.0])

    def test_model_soup_empty_raises(self):
        """Empty model list raises ValueError."""
        with pytest.raises(ValueError, match="at least one"):
            model_soup([])

    def test_model_soup_2d_params(self):
        """Soup works with 2D parameter arrays (weight matrices)."""
        dicts = [
            {"w": np.zeros((2, 3))},
            {"w": np.ones((2, 3))},
        ]
        result = model_soup(dicts)
        np.testing.assert_allclose(result["w"], np.full((2, 3), 0.5))


@pytest.mark.unit
class TestModelMerger:
    """Test suite for ModelMerger class."""

    def test_slerp_method(self):
        """ModelMerger with slerp method produces valid merge."""
        merger = ModelMerger(method="slerp")
        params_a = {"w": np.array([1.0, 0.0])}
        params_b = {"w": np.array([0.0, 1.0])}
        merged = merger.merge(params_a, params_b, alpha=0.5)
        assert "w" in merged
        assert merged["w"].shape == (2,)

    def test_linear_method(self):
        """ModelMerger with linear method produces midpoint."""
        merger = ModelMerger(method="linear")
        params_a = {"w": np.array([0.0, 0.0])}
        params_b = {"w": np.array([2.0, 4.0])}
        merged = merger.merge(params_a, params_b, alpha=0.5)
        np.testing.assert_allclose(merged["w"], [1.0, 2.0])

    def test_unknown_method_raises(self):
        """Unknown merge method raises ValueError."""
        merger = ModelMerger(method="unknown")
        with pytest.raises(ValueError, match="Unknown merge method"):
            merger.merge({"w": np.zeros(1)}, {"w": np.ones(1)})

    def test_missing_key_preserved(self):
        """Keys only in params_a are preserved in merge."""
        merger = ModelMerger(method="slerp")
        params_a = {"w1": np.array([1.0]), "w2": np.array([2.0])}
        params_b = {"w1": np.array([3.0])}
        merged = merger.merge(params_a, params_b, alpha=0.5)
        assert "w1" in merged
        assert "w2" in merged
        np.testing.assert_allclose(merged["w2"], [2.0])


@pytest.mark.unit
class TestModelMergerMCPTools:
    """Test MCP tool wrappers for model_merger."""

    def test_merge_models_slerp(self):
        """MCP merge_models with slerp returns success."""
        from codomyrmex.model_merger.mcp_tools import merge_models
        result = merge_models(
            params_a={"w": [1.0, 0.0]},
            params_b={"w": [0.0, 1.0]},
            method="slerp",
            alpha=0.5,
        )
        assert result["status"] == "success"
        assert "w" in result["keys"]

    def test_create_model_soup(self):
        """MCP create_model_soup returns success."""
        from codomyrmex.model_merger.mcp_tools import create_model_soup
        result = create_model_soup(
            param_dicts=[
                {"w": [0.0, 0.0]},
                {"w": [2.0, 4.0]},
            ],
        )
        assert result["status"] == "success"
        assert result["n_models"] == 2

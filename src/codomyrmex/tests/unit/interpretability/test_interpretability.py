"""Tests for the interpretability module (Sparse Autoencoders)."""

import pytest

try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False

if not HAS_NUMPY:
    pytest.skip("numpy not installed", allow_module_level=True)

try:
    from codomyrmex.interpretability import SparseAutoencoder, train_sae, analyze_features
    HAS_MODULE = True
except ImportError:
    HAS_MODULE = False

if not HAS_MODULE:
    pytest.skip("interpretability module not available", allow_module_level=True)


@pytest.mark.unit
class TestSparseAutoencoderInit:
    """Test SAE initialization."""

    def test_dimensions(self):
        """SAE stores correct input and feature dimensions."""
        sae = SparseAutoencoder(d_input=16, d_features=64)
        assert sae.d_input == 16
        assert sae.d_features == 64

    def test_weight_shapes(self):
        """Encoder and decoder weight matrices have correct shapes."""
        sae = SparseAutoencoder(d_input=8, d_features=32)
        assert sae.W_enc.shape == (32, 8)
        assert sae.W_dec.shape == (8, 32)
        assert sae.b_enc.shape == (32,)
        assert sae.b_dec.shape == (8,)

    def test_decoder_normalized(self):
        """Decoder columns have approximately unit norm after init."""
        sae = SparseAutoencoder(d_input=16, d_features=64)
        norms = np.linalg.norm(sae.W_dec, axis=0)
        np.testing.assert_allclose(norms, 1.0, atol=1e-6)

    def test_lambda_l1_stored(self):
        """L1 penalty coefficient is stored."""
        sae = SparseAutoencoder(d_input=4, d_features=8, lambda_l1=0.01)
        assert sae.lambda_l1 == 0.01


@pytest.mark.unit
class TestSparseAutoencoderEncodeDecode:
    """Test SAE encode and decode operations."""

    def test_encode_shape(self):
        """Encode produces (batch, d_features) output."""
        np.random.seed(42)
        sae = SparseAutoencoder(d_input=8, d_features=32)
        x = np.random.randn(10, 8)
        features = sae.encode(x)
        assert features.shape == (10, 32)

    def test_encode_produces_nonnegative(self):
        """ReLU activation ensures all feature values are >= 0."""
        np.random.seed(42)
        sae = SparseAutoencoder(d_input=8, d_features=32)
        x = np.random.randn(10, 8)
        features = sae.encode(x)
        assert np.all(features >= 0)

    def test_encode_produces_sparse_features(self):
        """Encoded features should be mostly zero (sparse)."""
        np.random.seed(42)
        sae = SparseAutoencoder(d_input=8, d_features=64)
        x = np.random.randn(50, 8)
        features = sae.encode(x)
        sparsity = np.mean(features == 0)
        # With overcomplete representation, expect some sparsity
        assert sparsity > 0.1

    def test_decode_shape(self):
        """Decode produces (batch, d_input) output."""
        np.random.seed(42)
        sae = SparseAutoencoder(d_input=8, d_features=32)
        features = np.random.randn(10, 32)
        features = np.maximum(0, features)  # Simulate ReLU
        reconstruction = sae.decode(features)
        assert reconstruction.shape == (10, 8)

    def test_forward_returns_both(self):
        """Forward returns (reconstruction, features) tuple."""
        np.random.seed(42)
        sae = SparseAutoencoder(d_input=8, d_features=32)
        x = np.random.randn(10, 8)
        reconstruction, features = sae.forward(x)
        assert reconstruction.shape == (10, 8)
        assert features.shape == (10, 32)


@pytest.mark.unit
class TestSparseAutoencoderLoss:
    """Test SAE loss computation."""

    def test_loss_returns_all_components(self):
        """Loss dict contains all expected keys."""
        np.random.seed(42)
        sae = SparseAutoencoder(d_input=8, d_features=32, lambda_l1=1e-3)
        x = np.random.randn(20, 8)
        loss = sae.loss(x)

        assert "total_loss" in loss
        assert "reconstruction_loss" in loss
        assert "sparsity_loss" in loss
        assert "mean_active_features" in loss
        assert "sparsity_ratio" in loss

    def test_total_loss_is_sum(self):
        """Total loss equals reconstruction + sparsity."""
        np.random.seed(42)
        sae = SparseAutoencoder(d_input=8, d_features=32, lambda_l1=1e-3)
        x = np.random.randn(20, 8)
        loss = sae.loss(x)

        expected = loss["reconstruction_loss"] + loss["sparsity_loss"]
        assert loss["total_loss"] == pytest.approx(expected, rel=1e-6)

    def test_reconstruction_loss_nonnegative(self):
        """MSE reconstruction loss is always >= 0."""
        np.random.seed(42)
        sae = SparseAutoencoder(d_input=8, d_features=32)
        x = np.random.randn(20, 8)
        loss = sae.loss(x)
        assert loss["reconstruction_loss"] >= 0

    def test_sparsity_loss_nonnegative(self):
        """L1 sparsity loss is always >= 0."""
        np.random.seed(42)
        sae = SparseAutoencoder(d_input=8, d_features=32, lambda_l1=1e-3)
        x = np.random.randn(20, 8)
        loss = sae.loss(x)
        assert loss["sparsity_loss"] >= 0

    def test_sparsity_ratio_bounded(self):
        """Sparsity ratio is between 0 and 1."""
        np.random.seed(42)
        sae = SparseAutoencoder(d_input=8, d_features=32)
        x = np.random.randn(20, 8)
        loss = sae.loss(x)
        assert 0 <= loss["sparsity_ratio"] <= 1


@pytest.mark.unit
class TestSparseAutoencoderTraining:
    """Test SAE training step."""

    def test_train_step_returns_loss(self):
        """Train step returns loss dict."""
        np.random.seed(42)
        sae = SparseAutoencoder(d_input=8, d_features=32, lambda_l1=1e-3)
        x = np.random.randn(20, 8)
        loss = sae.train_step(x, lr=1e-3)
        assert "total_loss" in loss

    def test_decoder_stays_normalized(self):
        """Decoder columns remain unit norm after training."""
        np.random.seed(42)
        sae = SparseAutoencoder(d_input=8, d_features=32)
        x = np.random.randn(20, 8)
        sae.train_step(x, lr=1e-3)
        norms = np.linalg.norm(sae.W_dec, axis=0)
        np.testing.assert_allclose(norms, 1.0, atol=1e-6)

    def test_multiple_steps_change_weights(self):
        """Multiple training steps modify SAE weights."""
        np.random.seed(42)
        sae = SparseAutoencoder(d_input=8, d_features=32)
        x = np.random.randn(50, 8)
        b_enc_before = sae.b_enc.copy()

        for _ in range(10):
            sae.train_step(x, lr=1e-2)

        # Encoder bias should change after training
        assert not np.allclose(sae.b_enc, b_enc_before)


@pytest.mark.unit
class TestTrainSAE:
    """Test the train_sae convenience function."""

    def test_train_sae_returns_sae(self):
        """train_sae returns a SparseAutoencoder instance."""
        np.random.seed(42)
        activations = np.random.randn(100, 8)
        sae = train_sae(activations, d_features=32, n_steps=10, seed=42)
        assert isinstance(sae, SparseAutoencoder)
        assert sae.d_input == 8
        assert sae.d_features == 32

    def test_train_sae_default_overcomplete(self):
        """Default d_features is 4x d_input."""
        np.random.seed(42)
        activations = np.random.randn(50, 10)
        sae = train_sae(activations, n_steps=5, seed=42)
        assert sae.d_features == 40

    def test_train_sae_deterministic(self):
        """Same seed produces same trained SAE."""
        activations = np.random.randn(50, 8)
        sae1 = train_sae(activations.copy(), d_features=16, n_steps=10, seed=99)
        sae2 = train_sae(activations.copy(), d_features=16, n_steps=10, seed=99)
        np.testing.assert_allclose(sae1.b_enc, sae2.b_enc, atol=1e-10)


@pytest.mark.unit
class TestAnalyzeFeatures:
    """Test feature analysis."""

    def test_analyze_returns_expected_keys(self):
        """analyze_features returns all expected keys."""
        np.random.seed(42)
        sae = SparseAutoencoder(d_input=8, d_features=32)
        activations = np.random.randn(50, 8)
        analysis = analyze_features(sae, activations)

        assert "d_features" in analysis
        assert "mean_active_features" in analysis
        assert "sparsity_ratio" in analysis
        assert "top_features" in analysis

    def test_top_features_sorted_by_frequency(self):
        """Top features are sorted by descending activation frequency."""
        np.random.seed(42)
        sae = SparseAutoencoder(d_input=8, d_features=32)
        activations = np.random.randn(100, 8)
        analysis = analyze_features(sae, activations)

        freqs = [f["activation_freq"] for f in analysis["top_features"]]
        assert freqs == sorted(freqs, reverse=True)

    def test_top_features_limited_to_10(self):
        """Top features list is capped at 10."""
        np.random.seed(42)
        sae = SparseAutoencoder(d_input=8, d_features=64)
        activations = np.random.randn(50, 8)
        analysis = analyze_features(sae, activations)
        assert len(analysis["top_features"]) <= 10

    def test_sparsity_ratio_bounded(self):
        """Sparsity ratio is between 0 and 1."""
        np.random.seed(42)
        sae = SparseAutoencoder(d_input=8, d_features=32)
        activations = np.random.randn(50, 8)
        analysis = analyze_features(sae, activations)
        assert 0 <= analysis["sparsity_ratio"] <= 1

    def test_feature_id_is_integer(self):
        """Feature IDs in top_features are integers."""
        np.random.seed(42)
        sae = SparseAutoencoder(d_input=8, d_features=32)
        activations = np.random.randn(50, 8)
        analysis = analyze_features(sae, activations)
        for f in analysis["top_features"]:
            assert isinstance(f["feature_id"], int)


@pytest.mark.unit
class TestInterpretabilityMCPTools:
    """Test MCP tool wrappers for interpretability."""

    def test_sae_train_tool(self):
        """MCP sae_train returns success with loss metrics."""
        from codomyrmex.interpretability.mcp_tools import sae_train
        result = sae_train(d_input=8, d_features=16, n_samples=50, n_steps=5, seed=42)
        assert result["status"] == "success"
        assert result["d_input"] == 8
        assert result["d_features"] == 16
        assert "final_loss" in result

    def test_sae_analyze_tool(self):
        """MCP sae_analyze returns feature analysis."""
        from codomyrmex.interpretability.mcp_tools import sae_analyze
        result = sae_analyze(d_input=8, d_features=16, n_samples=50, seed=42)
        assert result["status"] == "success"
        assert "top_features" in result

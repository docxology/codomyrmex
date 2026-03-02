"""
Unit tests for the Knowledge Distillation module.

Tests cover:
- Soft labels sum to one
- Temperature softens distribution (higher T -> lower max prob)
- KL loss is approximately zero for identical logits
- Distillation loss contains expected components
- DistillationLoss stateful class
- MCP tool interface
"""

import numpy as np
import pytest

from codomyrmex.distillation import DistillationLoss, distillation_loss, soft_labels

# ---------------------------------------------------------------------------
# soft_labels
# ---------------------------------------------------------------------------


class TestSoftLabels:
    """Tests for temperature-scaled softmax (soft labels)."""

    @pytest.mark.unit
    def test_soft_labels_sum_to_one(self):
        """Probabilities along the last axis should sum to 1."""
        logits = np.random.randn(4, 10)
        probs = soft_labels(logits, temperature=4.0)
        sums = np.sum(probs, axis=-1)
        np.testing.assert_allclose(sums, np.ones(4), atol=1e-6)

    @pytest.mark.unit
    def test_soft_labels_sum_to_one_3d(self):
        """Should work for 3D input (batch, seq, vocab)."""
        logits = np.random.randn(2, 3, 8)
        probs = soft_labels(logits, temperature=2.0)
        sums = np.sum(probs, axis=-1)
        np.testing.assert_allclose(sums, np.ones((2, 3)), atol=1e-6)

    @pytest.mark.unit
    def test_temperature_softens_distribution(self):
        """Higher temperature -> lower max probability (softer)."""
        logits = np.array([[5.0, 1.0, 0.5, 0.1]])

        probs_low_T = soft_labels(logits, temperature=1.0)
        probs_high_T = soft_labels(logits, temperature=10.0)

        max_low = np.max(probs_low_T)
        max_high = np.max(probs_high_T)
        assert max_high < max_low

    @pytest.mark.unit
    def test_temperature_1_is_standard_softmax(self):
        """At T=1, soft_labels should match standard softmax."""
        logits = np.array([[1.0, 2.0, 3.0]])
        probs = soft_labels(logits, temperature=1.0)

        # Manual softmax
        exp_logits = np.exp(logits - np.max(logits, axis=-1, keepdims=True))
        expected = exp_logits / np.sum(exp_logits, axis=-1, keepdims=True)
        np.testing.assert_allclose(probs, expected, atol=1e-7)

    @pytest.mark.unit
    def test_all_probabilities_positive(self):
        logits = np.random.randn(3, 5)
        probs = soft_labels(logits, temperature=4.0)
        assert np.all(probs > 0)


# ---------------------------------------------------------------------------
# distillation_loss
# ---------------------------------------------------------------------------


class TestDistillationLoss:
    """Tests for the knowledge distillation loss function."""

    @pytest.mark.unit
    def test_kl_loss_zero_identical(self):
        """KL(p || p) should be approximately 0."""
        logits = np.random.randn(4, 10)
        result = distillation_loss(
            student_logits=logits,
            teacher_logits=logits,
            temperature=4.0,
            alpha=1.0,  # Only distillation loss
        )
        # KL divergence between identical distributions should be ~0
        np.testing.assert_allclose(result["distillation_loss"], 0.0, atol=1e-4)

    @pytest.mark.unit
    def test_distillation_loss_components_present(self):
        """Result dict should contain all expected keys."""
        teacher = np.random.randn(4, 10) * 3.0
        student = teacher + np.random.randn(4, 10) * 0.5
        labels = np.argmax(teacher, axis=-1)

        result = distillation_loss(student, teacher, labels, temperature=4.0, alpha=0.7)
        assert "total_loss" in result
        assert "distillation_loss" in result
        assert "ce_loss" in result
        assert "teacher_accuracy" in result
        assert "temperature" in result
        assert "alpha" in result

    @pytest.mark.unit
    def test_total_loss_combines_kl_and_ce(self):
        """total = alpha * kl + (1-alpha) * ce."""
        np.random.seed(42)
        teacher = np.random.randn(4, 10) * 3.0
        student = teacher + np.random.randn(4, 10)
        labels = np.argmax(teacher, axis=-1)
        alpha = 0.7

        result = distillation_loss(student, teacher, labels, temperature=4.0, alpha=alpha)
        expected_total = alpha * result["distillation_loss"] + (1 - alpha) * result["ce_loss"]
        np.testing.assert_allclose(result["total_loss"], expected_total, atol=1e-10)

    @pytest.mark.unit
    def test_alpha_1_means_only_distillation(self):
        """With alpha=1.0, total_loss = distillation_loss."""
        teacher = np.random.randn(4, 10) * 3.0
        student = teacher + np.random.randn(4, 10)
        labels = np.argmax(teacher, axis=-1)

        result = distillation_loss(student, teacher, labels, temperature=4.0, alpha=1.0)
        np.testing.assert_allclose(
            result["total_loss"], result["distillation_loss"], atol=1e-10
        )

    @pytest.mark.unit
    def test_alpha_0_means_only_ce(self):
        """With alpha=0.0, total_loss = ce_loss."""
        np.random.seed(42)
        teacher = np.random.randn(4, 10) * 3.0
        student = teacher + np.random.randn(4, 10)
        labels = np.argmax(teacher, axis=-1)

        result = distillation_loss(student, teacher, labels, temperature=4.0, alpha=0.0)
        np.testing.assert_allclose(
            result["total_loss"], result["ce_loss"], atol=1e-10
        )

    @pytest.mark.unit
    def test_no_labels_ce_is_zero(self):
        """Without true_labels, ce_loss should be 0."""
        teacher = np.random.randn(4, 10)
        student = np.random.randn(4, 10)

        result = distillation_loss(student, teacher, temperature=4.0, alpha=0.5)
        assert result["ce_loss"] == 0.0

    @pytest.mark.unit
    def test_teacher_accuracy_correct(self):
        """Teacher accuracy should match argmax predictions vs labels."""
        np.random.seed(42)
        teacher = np.random.randn(10, 5) * 5.0
        student = np.random.randn(10, 5)
        labels = np.argmax(teacher, axis=-1)  # Teacher predicts perfectly

        result = distillation_loss(student, teacher, labels, temperature=4.0, alpha=0.7)
        assert result["teacher_accuracy"] == 1.0

    @pytest.mark.unit
    def test_kl_loss_non_negative(self):
        """KL divergence should be >= 0."""
        np.random.seed(42)
        teacher = np.random.randn(8, 10)
        student = np.random.randn(8, 10)

        result = distillation_loss(student, teacher, temperature=4.0, alpha=1.0)
        assert result["distillation_loss"] >= -1e-7


# ---------------------------------------------------------------------------
# DistillationLoss class
# ---------------------------------------------------------------------------


class TestDistillationLossClass:
    """Tests for the DistillationLoss stateful wrapper."""

    @pytest.mark.unit
    def test_default_params(self):
        loss_fn = DistillationLoss()
        assert loss_fn.temperature == 4.0
        assert loss_fn.alpha == 0.7

    @pytest.mark.unit
    def test_callable_returns_dict(self):
        loss_fn = DistillationLoss(temperature=2.0, alpha=0.5)
        teacher = np.random.randn(3, 6)
        student = np.random.randn(3, 6)
        result = loss_fn(student, teacher)
        assert isinstance(result, dict)
        assert "total_loss" in result


# ---------------------------------------------------------------------------
# MCP tool
# ---------------------------------------------------------------------------


class TestMCPTool:
    """Tests for distillation MCP tool interface."""

    @pytest.mark.unit
    def test_distillation_compute_loss_tool(self):
        from codomyrmex.distillation.mcp_tools import distillation_compute_loss

        result = distillation_compute_loss(
            num_classes=10, batch_size=4, temperature=4.0, alpha=0.7, seed=42
        )
        assert result["status"] == "success"
        assert "total_loss" in result
        assert "distillation_loss" in result

    @pytest.mark.unit
    def test_distillation_tool_has_mcp_metadata(self):
        from codomyrmex.distillation.mcp_tools import distillation_compute_loss

        assert hasattr(distillation_compute_loss, "_mcp_tool")
        assert distillation_compute_loss._mcp_tool["category"] == "distillation"

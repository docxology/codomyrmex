"""Zero-mock unit tests for softmax_opt MCP tools."""

import numpy as np
import pytest

from codomyrmex.softmax_opt.mcp_tools import compute_softmax


@pytest.mark.unit
def test_compute_softmax_standard() -> None:
    logits = [1.0, 2.0, 3.0]
    result = compute_softmax(logits=logits)

    assert result["status"] == "success"
    assert "probabilities" in result
    assert "log_probs" in result
    assert "entropy" in result
    assert "max_prob" in result
    assert "sum_check" in result

    # Check probabilities sum to 1
    assert abs(result["sum_check"] - 1.0) < 1e-6
    # Max probability should correspond to the largest logit
    assert result["max_prob"] == max(result["probabilities"])
    # 3.0 is the highest, so its probability should be the max
    assert result["probabilities"][2] == result["max_prob"]


@pytest.mark.unit
def test_compute_softmax_log_variant() -> None:
    logits = [1.0, 2.0, 3.0]
    result = compute_softmax(logits=logits, variant="log")

    assert result["status"] == "success"
    assert abs(result["sum_check"] - 1.0) < 1e-6
    # For standard and log, outputs should essentially match
    result_standard = compute_softmax(logits=logits, variant="standard")
    np.testing.assert_allclose(
        result["probabilities"], result_standard["probabilities"], rtol=1e-5
    )
    np.testing.assert_allclose(
        result["log_probs"], result_standard["log_probs"], rtol=1e-5
    )


@pytest.mark.unit
def test_compute_softmax_online_variant() -> None:
    logits = [100.0, 101.0, 99.0]
    result = compute_softmax(logits=logits, variant="online")

    assert result["status"] == "success"
    assert abs(result["sum_check"] - 1.0) < 1e-6
    # Compare with standard variant
    result_standard = compute_softmax(logits=logits, variant="standard")
    np.testing.assert_allclose(
        result["probabilities"], result_standard["probabilities"], rtol=1e-5
    )
    np.testing.assert_allclose(
        result["log_probs"], result_standard["log_probs"], rtol=1e-5
    )


@pytest.mark.unit
def test_compute_softmax_temperature() -> None:
    logits = [1.0, 2.0, 3.0]

    result_cold = compute_softmax(logits=logits, temperature=0.1)  # Peaked
    result_hot = compute_softmax(logits=logits, temperature=10.0)  # Uniform

    assert result_cold["max_prob"] > result_hot["max_prob"]
    assert result_cold["entropy"] < result_hot["entropy"]
    assert abs(result_cold["sum_check"] - 1.0) < 1e-6
    assert abs(result_hot["sum_check"] - 1.0) < 1e-6


@pytest.mark.unit
def test_compute_softmax_invalid_logits() -> None:
    # Test with incompatible type to naturally trigger an error instead of using mocks.
    with pytest.raises((ValueError, TypeError)):
        compute_softmax(logits=["not", "a", "number"])

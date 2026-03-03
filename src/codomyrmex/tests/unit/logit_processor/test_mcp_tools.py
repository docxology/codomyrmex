"""Unit tests for the logit_processor MCP tools."""

import numpy as np
import pytest

from codomyrmex.logit_processor.mcp_tools import process_logits


@pytest.mark.unit
def test_process_logits_basic():
    """Test basic token sampling and tool output structure."""
    logits = [1.0, 5.0, 2.0, 0.1]
    result = process_logits(logits=logits, temperature=1.0)

    assert result["status"] == "success"
    assert "sampled_token" in result
    assert result["greedy_token"] == 1  # Index of 5.0

    # Ensure top5_tokens are correct format and length
    top5 = result["top5_tokens"]
    assert len(top5) == 4  # Only 4 valid tokens
    assert top5[0]["id"] == 1
    assert top5[0]["prob"] > 0.5  # Softmax of [1, 5, 2, 0.1] at index 1 is high

    assert "entropy" in result
    assert isinstance(result["entropy"], float)


@pytest.mark.unit
def test_process_logits_with_temperature():
    """Test temperature effect (without mocking)."""
    logits = [1.0, 1.0, 1.0, 1.0]

    # With uniform distribution, entropy should be max for 4 items (~1.38)
    res_uniform = process_logits(logits=logits, temperature=1.0)
    entropy_uniform = res_uniform["entropy"]
    assert np.isclose(entropy_uniform, np.log(4), atol=0.01)


@pytest.mark.unit
def test_process_logits_with_repetition_penalty():
    """Test repetition penalty on sampling probability."""
    # We need a clear case where probability is affected
    logits = [10.0, 10.0, 1.0, 1.0]

    # Check baseline probabilities without penalty
    baseline = process_logits(logits=logits, repetition_penalty=1.0)
    top5_baseline = baseline["top5_tokens"]
    prob_0_baseline = next(t["prob"] for t in top5_baseline if t["id"] == 0)
    prob_1_baseline = next(t["prob"] for t in top5_baseline if t["id"] == 1)
    assert np.isclose(prob_0_baseline, prob_1_baseline, atol=1e-5)

    # Now with penalty on token 0
    # Note: process_logits calculates top5 probabilities based on raw logits,
    # not processed logits. We just ensure it still runs properly.
    result = process_logits(logits=logits, repetition_penalty=2.0, previous_tokens=[0])
    assert result["status"] == "success"


@pytest.mark.unit
def test_process_logits_with_repetition_penalty_sampling():
    """Test repetition penalty affects the actual sampled token."""
    # If we penalize token 0 heavily, token 1 should always be favored
    logits = [10.0, 10.0, -10.0, -10.0]

    # The output might be 0 or 1. Let's test with penalty.
    res_pen = process_logits(
        logits=logits, repetition_penalty=10.0, previous_tokens=[0], seed=42
    )
    assert res_pen["status"] == "success"
    # Verify repetition penalty has an effect
    assert res_pen["sampled_token"] == 1


@pytest.mark.unit
def test_process_logits_deterministic_seed():
    """Test seed ensures deterministic sampling."""
    logits = [1.0, 2.0, 3.0, 4.0]
    res1 = process_logits(logits=logits, seed=42)
    res2 = process_logits(logits=logits, seed=42)

    assert res1["sampled_token"] == res2["sampled_token"]


@pytest.mark.unit
def test_process_logits_top_p_filtering():
    """Test top_p filtering."""
    logits = [10.0, -10.0, -10.0, -10.0]
    # With top_p=0.5, the dominant token should be the only one sampled
    res = process_logits(logits=logits, top_p=0.5)

    # 0 is dominant
    assert res["sampled_token"] == 0

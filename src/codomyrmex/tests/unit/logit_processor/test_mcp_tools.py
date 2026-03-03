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
    # We use a case where token 0 and 1 are equally likely, and penalty shifts balance.
    logits = [10.0, 10.0, -10.0, -10.0]

    # Check baseline without penalty, check process runs.
    baseline = process_logits(logits=logits, repetition_penalty=1.0)
    assert baseline["status"] == "success"

    # Now apply a heavy penalty to token 0.
    # Since they were tied, token 1 should now become the sampled token deterministically.
    res_pen = process_logits(
        logits=logits, repetition_penalty=10.0, previous_tokens=[0], seed=42
    )
    assert res_pen["status"] == "success"
    # Verify repetition penalty has an effect on the actual sampled token
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

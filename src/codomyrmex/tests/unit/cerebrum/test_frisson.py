"""Tests for Frisson/Surprise Signals."""

import pytest

from codomyrmex.cerebrum.mcp_tools import evaluate_surprise_signal


@pytest.mark.unit
class TestFrissonSignal:
    def test_low_surprise(self):
        """Should return MONITOR recommendation for few observations."""
        observation = {"drift": 0.1}
        result = evaluate_surprise_signal(observation, threshold=5.0)
        assert result["status"] == "success"
        assert result["recommendation"] == "MONITOR"
        assert result["free_energy"] < 5.0

    def test_high_surprise(self):
        """Should return DEPLOY_SWARM for many/rare observations."""
        # More observations increase the complexity/error sum in this model
        observation = {f"anomaly_{i}": 0.9 for i in range(10)}
        result = evaluate_surprise_signal(observation, threshold=5.0)
        assert result["status"] == "success"
        assert result["recommendation"] == "DEPLOY_SWARM"
        assert result["free_energy"] > 5.0

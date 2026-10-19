"""Synthetic public-behavior controls for recording after enrollment."""

import pytest

from codomyrmex.identity.biocognitive import BioCognitiveVerifier


@pytest.mark.parametrize("initial_size", [0, 10, 100, 150])
def test_enrolled_window_adapts_without_retaining_old_samples(initial_size):
    verifier = BioCognitiveVerifier()
    baseline = [0.0] * initial_size
    verifier.enroll("synthetic", "decision_latency", baseline)
    baseline[:] = [500.0] * initial_size
    for _ in range(max(100, initial_size)):
        verifier.record_metric("synthetic", "decision_latency", 1.0)
    assert verifier.verify("synthetic", "decision_latency", 1.0)
    assert not verifier.verify("synthetic", "decision_latency", 0.0)


def test_large_enrollment_preserves_legacy_adaptation_capacity():
    verifier = BioCognitiveVerifier()
    verifier.enroll("synthetic", "decision_latency", [0.0] * 150)
    for _ in range(100):
        verifier.record_metric("synthetic", "decision_latency", 1.0)
    # The original append/pop policy retains 50 initial samples here.
    assert verifier.verify("synthetic", "decision_latency", 0.0)


def test_recorded_window_without_enrollment_adapts():
    verifier = BioCognitiveVerifier()
    for value in [0.0] * 100 + [1.0] * 100:
        verifier.record_metric("synthetic", "decision_latency", value)
    assert verifier.verify("synthetic", "decision_latency", 1.0)
    assert not verifier.verify("synthetic", "decision_latency", 0.0)

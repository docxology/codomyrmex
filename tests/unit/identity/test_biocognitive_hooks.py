"""Tests for bio-cognitive verification hooks — heartbeat, EEG, and multi-modal.

Zero-mock policy: all tests use real numpy computations and real signal
data generated deterministically (no random seeds needed for the chosen
test signals).
"""

from __future__ import annotations

import math

import pytest

from codomyrmex.identity.biocognitive import (
    EEG_BANDS,
    BioCognitiveVerifier,
    EEGFrequencyAnalyzer,
    HeartbeatValidator,
    analyze_eeg_bands,
    verify_biocognitive,
    verify_heartbeat_intervals,
)

try:
    import numpy as np

    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False


# ── Helpers ────────────────────────────────────────────────────────────


def _sine_wave(
    freq: float, duration_s: float = 1.0, rate: float = 256.0
) -> list[float]:
    """Generate a pure sine wave at *freq* Hz."""
    n = int(duration_s * rate)
    return [math.sin(2 * math.pi * freq * t / rate) for t in range(n)]


def _composite_eeg(
    freqs: list[float], duration_s: float = 2.0, rate: float = 256.0
) -> list[float]:
    """Generate a sum of sine waves at the given frequencies."""
    n = int(duration_s * rate)
    return [sum(math.sin(2 * math.pi * f * t / rate) for f in freqs) for t in range(n)]


def _normal_heartbeat(
    mean_ms: float = 800.0, count: int = 30, jitter: float = 20.0
) -> list[float]:
    """Generate realistic RR intervals with small variation."""
    return [
        float(mean_ms + ((i * 37) % 100 - 50) * (jitter / 50)) for i in range(count)
    ]


# ── EEG band definitions ───────────────────────────────────────────────


@pytest.mark.unit
class TestEEGBands:
    """Tests for the EEG_BANDS constant."""

    def test_all_five_bands_present(self):
        assert set(EEG_BANDS.keys()) == {"delta", "theta", "alpha", "beta", "gamma"}

    def test_band_ranges_are_contiguous(self):
        bands = list(EEG_BANDS.values())
        for i in range(len(bands) - 1):
            assert bands[i][1] == bands[i + 1][0], f"Gap between band {i} and {i + 1}"

    def test_delta_is_lowest(self):
        assert EEG_BANDS["delta"][0] == 0.5

    def test_gamma_is_highest(self):
        assert EEG_BANDS["gamma"][1] == 100.0


# ── HeartbeatValidator ──────────────────────────────────────────────────


@pytest.mark.unit
@pytest.mark.skipif(not HAS_NUMPY, reason="numpy not installed")
class TestHeartbeatValidator:
    """Tests for the HeartbeatValidator class."""

    def test_compute_metrics_basic(self):
        validator = HeartbeatValidator()
        intervals = [800.0, 810.0, 790.0, 805.0, 800.0, 810.0, 790.0, 805.0]
        metrics = validator.get_metrics(intervals)
        assert "rmssd" in metrics
        assert "sdnn" in metrics
        assert "mean_hr" in metrics
        assert metrics["rmssd"] > 0
        assert metrics["sdnn"] > 0
        assert metrics["mean_hr"] > 0

    def test_mean_hr_calculation(self):
        validator = HeartbeatValidator()
        # 800ms intervals → 60000/800 = 75 bpm
        intervals = [800.0] * 10
        metrics = validator.get_metrics(intervals)
        assert abs(metrics["mean_hr"] - 75.0) < 0.1

    def test_enroll_and_verify_matching(self):
        validator = HeartbeatValidator(min_samples=5)
        baseline = _normal_heartbeat(mean_ms=800, count=20)
        validator.enroll("user1", baseline)
        # Similar intervals
        current = _normal_heartbeat(mean_ms=800, count=20)
        assert validator.verify("user1", current) is True

    def test_verify_rejects_outlier(self):
        validator = HeartbeatValidator(min_samples=5, tolerance=0.20)
        baseline = _normal_heartbeat(mean_ms=800, count=20)
        validator.enroll("user1", baseline)
        # Very different intervals — much faster heartbeat
        current = _normal_heartbeat(mean_ms=400, count=20)
        assert validator.verify("user1", current) is False

    def test_verify_no_baseline_returns_false(self):
        validator = HeartbeatValidator()
        assert validator.verify("unknown", [800, 810, 790]) is False

    def test_enroll_too_few_samples_raises(self):
        validator = HeartbeatValidator(min_samples=10)
        with pytest.raises(ValueError, match="at least 10"):
            validator.enroll("u1", [800, 810])

    def test_verify_insufficient_samples_allows(self):
        """Insufficient current samples should allow (enrollment phase)."""
        validator = HeartbeatValidator(min_samples=10)
        baseline = _normal_heartbeat(count=15)
        validator.enroll("u1", baseline)
        # Only 3 current samples → should return True (enrollment behavior)
        assert validator.verify("u1", [800.0, 810.0, 790.0]) is True

    def test_rmssd_zero_for_constant_intervals(self):
        validator = HeartbeatValidator()
        metrics = validator.get_metrics([800.0] * 10)
        assert metrics["rmssd"] == 0.0

    def test_sdnn_zero_for_constant_intervals(self):
        validator = HeartbeatValidator()
        metrics = validator.get_metrics([800.0] * 10)
        assert metrics["sdnn"] == 0.0


# ── EEGFrequencyAnalyzer ───────────────────────────────────────────────


@pytest.mark.unit
@pytest.mark.skipif(not HAS_NUMPY, reason="numpy not installed")
class TestEEGFrequencyAnalyzer:
    """Tests for the EEGFrequencyAnalyzer class."""

    def test_compute_band_powers_alpha_dominant(self):
        """A 10 Hz sine wave should concentrate power in the alpha band."""
        analyzer = EEGFrequencyAnalyzer(sampling_rate=256.0)
        signal = _sine_wave(10.0, duration_s=2.0, rate=256.0)
        powers = analyzer.compute_band_powers(signal)
        assert powers["alpha"] > 0.5  # most power in alpha
        assert powers["alpha"] > powers["delta"]
        assert powers["alpha"] > powers["gamma"]

    def test_compute_band_powers_delta_dominant(self):
        """A 2 Hz sine wave should concentrate power in the delta band."""
        analyzer = EEGFrequencyAnalyzer(sampling_rate=256.0)
        signal = _sine_wave(2.0, duration_s=2.0, rate=256.0)
        powers = analyzer.compute_band_powers(signal)
        assert powers["delta"] > 0.5
        assert powers["delta"] > powers["alpha"]

    def test_compute_band_powers_beta_dominant(self):
        """A 20 Hz sine wave should concentrate power in the beta band."""
        analyzer = EEGFrequencyAnalyzer(sampling_rate=256.0)
        signal = _sine_wave(20.0, duration_s=2.0, rate=256.0)
        powers = analyzer.compute_band_powers(signal)
        assert powers["beta"] > 0.5

    def test_band_powers_sum_to_approximately_one(self):
        analyzer = EEGFrequencyAnalyzer(sampling_rate=256.0)
        signal = _composite_eeg([2.0, 10.0, 20.0])
        powers = analyzer.compute_band_powers(signal)
        total = sum(powers.values())
        assert abs(total - 1.0) < 0.05  # within 5% of 1.0

    def test_all_bands_returned(self):
        analyzer = EEGFrequencyAnalyzer()
        signal = _sine_wave(10.0)
        powers = analyzer.compute_band_powers(signal)
        assert set(powers.keys()) == {"delta", "theta", "alpha", "beta", "gamma"}

    def test_enroll_and_verify_matching(self):
        analyzer = EEGFrequencyAnalyzer(sampling_rate=256.0)
        baseline = _composite_eeg([2.0, 10.0, 20.0], duration_s=2.0)
        analyzer.enroll("user1", baseline)
        # Similar signal
        current = _composite_eeg([2.0, 10.0, 20.0], duration_s=2.0)
        assert analyzer.verify("user1", current) is True

    def test_verify_rejects_different_signal(self):
        analyzer = EEGFrequencyAnalyzer(sampling_rate=256.0)
        baseline = _composite_eeg([2.0, 10.0], duration_s=2.0)
        analyzer.enroll("user1", baseline)
        # Very different — gamma-heavy
        current = _sine_wave(40.0, duration_s=2.0)
        assert analyzer.verify("user1", current) is False

    def test_verify_no_baseline_returns_false(self):
        analyzer = EEGFrequencyAnalyzer()
        assert analyzer.verify("unknown", _sine_wave(10.0)) is False

    def test_enroll_zero_power_raises(self):
        analyzer = EEGFrequencyAnalyzer()
        with pytest.raises(ValueError, match="zero-power"):
            analyzer.enroll("u1", [0.0] * 100)

    def test_short_signal_returns_zeros(self):
        analyzer = EEGFrequencyAnalyzer()
        powers = analyzer.compute_band_powers([1.0])
        assert all(v == 0.0 for v in powers.values())


# ── Standalone hook: verify_heartbeat_intervals ────────────────────────


@pytest.mark.unit
@pytest.mark.skipif(not HAS_NUMPY, reason="numpy not installed")
class TestVerifyHeartbeatIntervals:
    """Tests for the verify_heartbeat_intervals hook function."""

    def test_metric_only_mode_no_baseline(self):
        intervals = [800, 810, 790, 805, 800]
        result = verify_heartbeat_intervals(intervals)
        assert result["status"] == "success"
        assert result["verified"] is True
        assert "metrics" in result
        assert "rmssd" in result["metrics"]

    def test_verify_with_baseline_matching(self):
        baseline = _normal_heartbeat(count=15)
        current = _normal_heartbeat(count=15)
        result = verify_heartbeat_intervals(current, baseline_intervals=baseline)
        assert result["status"] == "success"
        assert result["verified"] is True
        assert "baseline_metrics" in result

    def test_verify_with_baseline_mismatch(self):
        baseline = _normal_heartbeat(mean_ms=800, count=15)
        current = _normal_heartbeat(mean_ms=400, count=15)
        result = verify_heartbeat_intervals(
            current, baseline_intervals=baseline, tolerance=0.20
        )
        assert result["status"] == "success"
        assert result["verified"] is False

    def test_enroll_too_few_returns_error(self):
        result = verify_heartbeat_intervals([800, 810], baseline_intervals=[800, 810])
        assert result["status"] == "error"


# ── Standalone hook: analyze_eeg_bands ─────────────────────────────────


@pytest.mark.unit
@pytest.mark.skipif(not HAS_NUMPY, reason="numpy not installed")
class TestAnalyzeEEGBands:
    """Tests for the analyze_eeg_bands hook function."""

    def test_analysis_only_mode(self):
        signal = _sine_wave(10.0, duration_s=2.0)
        result = analyze_eeg_bands(signal)
        assert result["status"] == "success"
        assert result["verified"] is True
        assert "band_powers" in result
        assert result["band_powers"]["alpha"] > 0.5

    def test_verify_with_baseline_matching(self):
        baseline = _composite_eeg([2.0, 10.0], duration_s=2.0)
        current = _composite_eeg([2.0, 10.0], duration_s=2.0)
        result = analyze_eeg_bands(current, baseline_samples=baseline)
        assert result["status"] == "success"
        assert result["verified"] is True

    def test_verify_with_baseline_mismatch(self):
        baseline = _sine_wave(10.0, duration_s=2.0)  # alpha-dominant
        current = _sine_wave(40.0, duration_s=2.0)  # gamma-dominant
        result = analyze_eeg_bands(current, baseline_samples=baseline)
        assert result["status"] == "success"
        assert result["verified"] is False

    def test_custom_sampling_rate(self):
        signal = _sine_wave(10.0, duration_s=2.0, rate=128.0)
        result = analyze_eeg_bands(signal, sampling_rate=128.0)
        assert result["status"] == "success"
        assert result["band_powers"]["alpha"] > 0.5


# ── Multi-modal: verify_biocognitive ───────────────────────────────────


@pytest.mark.unit
@pytest.mark.skipif(not HAS_NUMPY, reason="numpy not installed")
class TestVerifyBiocognitive:
    """Tests for the multi-modal verify_biocognitive entry point."""

    def test_no_data_returns_error(self):
        result = verify_biocognitive(user_id="u1")
        assert result["status"] == "error"

    def test_keystroke_only_verification(self):
        baseline = [0.12] * 15
        result = verify_biocognitive(
            user_id="u1",
            keystroke_values=baseline,
            current_keystroke=0.121,
        )
        assert result["status"] == "success"
        assert result["verified"] is True
        assert "keystroke" in result["modalities"]

    def test_heartbeat_only_verification(self):
        baseline = _normal_heartbeat(count=15)
        current = _normal_heartbeat(count=15)
        result = verify_biocognitive(
            user_id="u1",
            heartbeat_intervals=current,
            heartbeat_baseline=baseline,
        )
        assert result["status"] == "success"
        assert result["verified"] is True
        assert "heartbeat" in result["modalities"]

    def test_eeg_only_verification(self):
        baseline = _composite_eeg([2.0, 10.0], duration_s=2.0)
        current = _composite_eeg([2.0, 10.0], duration_s=2.0)
        result = verify_biocognitive(
            user_id="u1",
            eeg_samples=current,
            eeg_baseline=baseline,
        )
        assert result["status"] == "success"
        assert result["verified"] is True
        assert "eeg" in result["modalities"]

    def test_multi_modal_all_pass(self):
        keystroke_baseline = [0.12] * 15
        hb_baseline = _normal_heartbeat(count=15)
        eeg_baseline = _composite_eeg([2.0, 10.0], duration_s=2.0)
        result = verify_biocognitive(
            user_id="u1",
            keystroke_values=keystroke_baseline,
            current_keystroke=0.121,
            heartbeat_intervals=_normal_heartbeat(count=15),
            heartbeat_baseline=hb_baseline,
            eeg_samples=_composite_eeg([2.0, 10.0], duration_s=2.0),
            eeg_baseline=eeg_baseline,
        )
        assert result["status"] == "success"
        assert result["verified"] is True
        assert len(result["modalities"]) == 3

    def test_multi_modal_one_fails(self):
        keystroke_baseline = [0.12] * 15
        hb_baseline = _normal_heartbeat(mean_ms=800, count=15)
        # EEG baseline alpha, current gamma → mismatch
        eeg_baseline = _sine_wave(10.0, duration_s=2.0)
        eeg_current = _sine_wave(40.0, duration_s=2.0)
        result = verify_biocognitive(
            user_id="u1",
            keystroke_values=keystroke_baseline,
            current_keystroke=0.121,
            heartbeat_intervals=_normal_heartbeat(count=15),
            heartbeat_baseline=hb_baseline,
            eeg_samples=eeg_current,
            eeg_baseline=eeg_baseline,
        )
        assert result["status"] == "success"
        assert result["verified"] is False

    def test_keystroke_no_baseline_with_current(self):
        result = verify_biocognitive(
            user_id="u1",
            current_keystroke=0.12,
        )
        assert result["status"] == "success"
        assert result["modalities"]["keystroke"]["verified"] is False


# ── MCP tool: identity_verify_biocognitive ─────────────────────────────


@pytest.mark.unit
@pytest.mark.skipif(not HAS_NUMPY, reason="numpy not installed")
class TestIdentityVerifyBiocognitiveMCPTool:
    """Tests for the identity_verify_biocognitive MCP tool wrapper."""

    def test_mcp_tool_metadata_present(self):
        from codomyrmex.identity.mcp_tools import identity_verify_biocognitive

        assert hasattr(identity_verify_biocognitive, "_mcp_tool_meta")
        meta = identity_verify_biocognitive._mcp_tool_meta
        assert meta["category"] == "identity"
        assert "bio-cognitive" in meta["description"].lower()

    def test_mcp_tool_no_data_error(self):
        from codomyrmex.identity.mcp_tools import identity_verify_biocognitive

        result = identity_verify_biocognitive(user_id="u1")
        assert result["status"] == "error"

    def test_mcp_tool_heartbeat_verification(self):
        from codomyrmex.identity.mcp_tools import identity_verify_biocognitive

        baseline = _normal_heartbeat(count=15)
        current = _normal_heartbeat(count=15)
        result = identity_verify_biocognitive(
            user_id="u1",
            heartbeat_intervals=current,
            heartbeat_baseline=baseline,
        )
        assert result["status"] == "success"
        assert result["verified"] is True

    def test_mcp_tool_eeg_verification(self):
        from codomyrmex.identity.mcp_tools import identity_verify_biocognitive

        baseline = _composite_eeg([10.0], duration_s=2.0)
        current = _composite_eeg([10.0], duration_s=2.0)
        result = identity_verify_biocognitive(
            user_id="u1",
            eeg_samples=current,
            eeg_baseline=baseline,
        )
        assert result["status"] == "success"
        assert result["verified"] is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

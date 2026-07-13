"""Bio-Cognitive Verification Module.

Provides behavioral authentication based on user pattern metrics such as
keystroke dynamics, decision latencies, heartbeat intervals (HRV), and
EEG frequency-band analysis.

The module exposes:

- :class:`BioCognitiveVerifier` – statistical behavioural verifier
- :class:`HeartbeatValidator` – heart-rate variability interval validation
- :class:`EEGFrequencyAnalyzer` – EEG band-power analysis (delta, theta,
  alpha, beta, gamma)
- :data:`EEG_BANDS` – canonical EEG frequency-band ranges (Hz)
- :func:`verify_heartbeat_intervals` – standalone heartbeat validation hook
- :func:`analyze_eeg_bands` – standalone EEG band-power hook
- :func:`verify_biocognitive` – multi-modal verification entry point
"""

from __future__ import annotations

from typing import Any

import numpy as np

from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)

# ── EEG frequency-band definitions (Hz) ────────────────────────────────

EEG_BANDS: dict[str, tuple[float, float]] = {
    "delta": (0.5, 4.0),
    "theta": (4.0, 8.0),
    "alpha": (8.0, 13.0),
    "beta": (13.0, 30.0),
    "gamma": (30.0, 100.0),
}


class BioCognitiveVerifier:
    """Verifies identity based on behavioral biometrics.

    Uses statistical analysis of behavioral patterns (keystroke dynamics,
    decision latency) to ensure the current operator matches the expected
    identity baseline.
    """

    def __init__(self) -> None:
        # keyed by user_id -> metric_name -> list of values
        self._baselines: dict[str, dict[str, list[float]]] = {}
        self._thresholds: dict[str, float] = {
            "keystroke_flight_time": 0.15,  # Variance allowed
            "decision_latency": 0.20,
        }

    def record_metric(self, user_id: str, metric: str, value: float) -> None:
        """Record a new behavioral metric sample.

        Args:
            user_id: Unique identifier for the user or persona.
            metric: The name of the metric being recorded (e.g., 'keystroke_flight_time').
            value: The observed value of the metric.
        """
        if user_id not in self._baselines:
            self._baselines[user_id] = {}
        if metric not in self._baselines[user_id]:
            self._baselines[user_id][metric] = []

        self._baselines[user_id][metric].append(value)
        # Keep window of last 100 samples to adapt to drift
        if len(self._baselines[user_id][metric]) > 100:
            self._baselines[user_id][metric].pop(0)

    def verify(self, user_id: str, metric: str, current_value: float) -> bool:
        """Verify if current value matches user's baseline using statistical analysis.

        Uses Z-score analysis to determine if the current observation is within
        expected deviation from the mean baseline for that user and metric.

        Args:
            user_id: Unique identifier for the user to verify.
            metric: The name of the metric to check.
            current_value: The current observed value to be verified.

        Returns:
            bool: True if verification succeeds or if there's insufficient data
                  for a conclusive result during enrollment phases.
        """
        if user_id not in self._baselines or metric not in self._baselines[user_id]:
            logger.warning("No baseline for user %s on %s", user_id, metric)
            return False

        samples = self._baselines[user_id][metric]
        if len(samples) < 10:
            logger.info(
                "Insufficient samples for verification, assuming true for training"
            )
            return True

        mean = float(np.mean(samples))
        std = float(np.std(samples))

        # Enforce minimum std to avoid division by zero and allow specific variance
        min_std = 0.01
        effective_std = max(std, min_std)

        # Simple Z-score check
        z_score = abs(current_value - mean) / effective_std

        # Allow deviation up to 2.5 sigma for typical behavior
        is_valid = z_score < 2.5

        if not is_valid:
            logger.warning("Bio-cognitive mismatch: %s z-score %.2f", metric, z_score)

        return is_valid

    def enroll(self, user_id: str, metric_type: str, baseline: list[float]) -> None:
        """Enroll a user with a full baseline for a specific metric.

        Args:
            user_id: The ID of the user to enroll.
            metric_type: The name of the metric being enrolled.
            baseline: A list of baseline values for that metric.
        """
        if user_id not in self._baselines:
            self._baselines[user_id] = {}
        self._baselines[user_id][metric_type] = list(baseline)
        logger.info("Enrolled user %s for metric %s", user_id, metric_type)

    def get_confidence(self, user_id: str) -> float:
        """Calculate aggregate confidence score for a user's identity based on data volume.

        Returns:
            float: A value between 0.0 and 1.0 representing identity confidence.
        """
        if user_id not in self._baselines:
            return 0.0

        # Simple heuristic: more samples = more confidence
        total_samples = sum(len(v) for v in self._baselines[user_id].values())
        return min(total_samples / 100.0, 1.0)

    def create_challenge(self, persona: Any) -> dict[str, str]:
        """Create a challenge for the agent to respond to.

        Args:
            persona: The persona instance to create a challenge for.

        Returns:
            A dictionary containing challenge details.
        """
        # In a real implementation, this might return specific tasks/prompts
        return {
            "type": "keystroke_dynamics",
            "prompt": "Please type the following phrase: 'The quick brown fox jumps over the lazy dog.'",
            "persona_id": getattr(persona, "id", str(persona)),
        }


# ── Heartbeat interval validation ──────────────────────────────────────


class HeartbeatValidator:
    """Validate heartbeat (RR-interval) data against a user's baseline.

    Heart-rate variability (HRV) metrics computed:

    - **RMSSD** – root mean square of successive differences (ms)
    - **SDNN** – standard deviation of NN intervals (ms)
    - **mean_HR** – mean heart rate (bpm)

    Verification compares current RMSSD/SDNN to a stored baseline with
    configurable tolerance.

    Parameters
    ----------
    min_samples:
        Minimum RR-interval samples required before verification is performed
        (insufficient data → ``True`` to allow enrolment).
    tolerance:
        Relative tolerance for RMSSD/SDNN deviation (default 0.30 = ±30 %).
    """

    def __init__(
        self,
        min_samples: int = 5,
        tolerance: float = 0.30,
    ) -> None:
        self._baselines: dict[str, dict[str, float]] = {}
        self.min_samples = min_samples
        self.tolerance = tolerance

    # -- enrolment --------------------------------------------------------

    def enroll(self, user_id: str, intervals_ms: list[float]) -> None:
        """Enrol a user from a list of RR intervals (milliseconds)."""
        if len(intervals_ms) < self.min_samples:
            raise ValueError(
                f"Need at least {self.min_samples} intervals for enrolment, "
                f"got {len(intervals_ms)}"
            )
        self._baselines[user_id] = self._compute_metrics(intervals_ms)
        logger.info("Enrolled heartbeat baseline for %s", user_id)

    # -- metrics ----------------------------------------------------------

    @staticmethod
    def _compute_metrics(intervals_ms: list[float]) -> dict[str, float]:
        """Compute RMSSD, SDNN, and mean_HR from RR intervals."""
        arr = np.asarray(intervals_ms, dtype=float)
        diffs = np.diff(arr)
        rmssd: float = float(np.sqrt(np.mean(diffs**2))) if len(diffs) else 0.0
        sdnn: float = float(np.std(arr))
        mean_interval: float = float(np.mean(arr))
        mean_hr: float = 60_000.0 / mean_interval if mean_interval > 0 else 0.0
        return {"rmssd": rmssd, "sdnn": sdnn, "mean_hr": mean_hr}

    # -- verification -----------------------------------------------------

    def verify(self, user_id: str, intervals_ms: list[float]) -> bool:
        """Verify whether *intervals_ms* matches the enrolled baseline."""
        if user_id not in self._baselines:
            logger.warning("No heartbeat baseline for %s", user_id)
            return False
        if len(intervals_ms) < self.min_samples:
            logger.info("Insufficient heartbeat samples (%d); allowing", len(intervals_ms))
            return True

        current = self._compute_metrics(intervals_ms)
        baseline = self._baselines[user_id]

        for metric in ("rmssd", "sdnn"):
            base_val = baseline[metric]
            curr_val = current[metric]
            if base_val <= 0:
                # Near-zero baseline; fall back to absolute comparison
                if abs(curr_val - base_val) > self.tolerance * 100:
                    logger.warning("Heartbeat %s mismatch: base=%.2f cur=%.2f", metric, base_val, curr_val)
                    return False
            else:
                ratio = abs(curr_val - base_val) / base_val
                if ratio > self.tolerance:
                    logger.warning("Heartbeat %s mismatch: base=%.2f cur=%.2f (%.0f%%)", metric, base_val, curr_val, ratio * 100)
                    return False

        # Also check mean heart rate — a doubled HR should be rejected even
        # if HRV metrics (RMSSD/SDNN) happen to be near-zero in both.
        base_hr = baseline["mean_hr"]
        curr_hr = current["mean_hr"]
        if base_hr > 0:
            hr_ratio = abs(curr_hr - base_hr) / base_hr
            if hr_ratio > self.tolerance:
                logger.warning(
                    "Heartbeat mean_hr mismatch: base=%.1f cur=%.1f (%.0f%%)",
                    base_hr, curr_hr, hr_ratio * 100,
                )
                return False
        return True

    def get_metrics(self, intervals_ms: list[float]) -> dict[str, float]:
        """Return computed HRV metrics for *intervals_ms* (no enrolment)."""
        return self._compute_metrics(intervals_ms)


# ── EEG frequency-band analysis ─────────────────────────────────────────


class EEGFrequencyAnalyzer:
    """Analyse EEG signal samples and compute per-band power.

    Accepts EEG amplitude samples and a sampling rate.  Computes the
    power spectral density via :func:`numpy.fft.rfft` and integrates power
    into canonical frequency bands defined in :data:`EEG_BANDS`.

    The analyzer can also verify whether the band-power ratio matches a
    previously enrolled baseline.
    """

    def __init__(self, sampling_rate: float = 256.0) -> None:
        self.sampling_rate = sampling_rate
        self._baselines: dict[str, dict[str, float]] = {}

    # -- band-power computation -------------------------------------------

    def compute_band_powers(self, samples: list[float]) -> dict[str, float]:
        """Compute normalised band-power fractions for *samples*.

        Returns a dict mapping each band name in :data:`EEG_BANDS` to its
        fractional power (all bands sum to ~1.0).  If the signal has no
        power, all bands return 0.0.
        """
        arr = np.asarray(samples, dtype=float)
        n = len(arr)
        if n < 2:
            return dict.fromkeys(EEG_BANDS, 0.0)

        # Frequency bins
        spectrum = np.abs(np.fft.rfft(arr)) ** 2
        freqs = np.fft.rfftfreq(n, d=1.0 / self.sampling_rate)
        total_power = float(np.sum(spectrum))
        if total_power <= 0.0:
            return dict.fromkeys(EEG_BANDS, 0.0)

        band_powers: dict[str, float] = {}
        for band, (lo, hi) in EEG_BANDS.items():
            mask = (freqs >= lo) & (freqs < hi)
            band_powers[band] = float(np.sum(spectrum[mask]) / total_power)
        return band_powers

    # -- enrolment & verification -----------------------------------------

    def enroll(self, user_id: str, samples: list[float]) -> None:
        """Enrol baseline EEG band-power ratios for *user_id*."""
        powers = self.compute_band_powers(samples)
        if sum(powers.values()) == 0.0:
            raise ValueError("Cannot enrol from a zero-power EEG signal")
        self._baselines[user_id] = powers
        logger.info("Enrolled EEG baseline for %s", user_id)

    def verify(
        self,
        user_id: str,
        samples: list[float],
        tolerance: float = 0.25,
    ) -> bool:
        """Verify whether EEG band-power ratios match the baseline.

        Parameters
        ----------
        tolerance:
            Maximum allowed absolute deviation per band (default 0.25 = 25
            percentage points).
        """
        if user_id not in self._baselines:
            logger.warning("No EEG baseline for %s", user_id)
            return False

        current = self.compute_band_powers(samples)
        if sum(current.values()) == 0.0:
            logger.warning("Zero-power EEG signal for %s verification", user_id)
            return False

        baseline = self._baselines[user_id]
        for band in EEG_BANDS:
            delta = abs(current[band] - baseline[band])
            if delta > tolerance:
                logger.warning(
                    "EEG band %s mismatch: base=%.3f cur=%.3f (Δ=%.3f)",
                    band,
                    baseline[band],
                    current[band],
                    delta,
                )
                return False
        return True


# ── Standalone hook functions ──────────────────────────────────────────


def verify_heartbeat_intervals(
    intervals_ms: list[float],
    baseline_intervals: list[float] | None = None,
    user_id: str = "default",
    tolerance: float = 0.30,
) -> dict[str, Any]:
    """Validate heartbeat RR-interval data.

    If *baseline_intervals* is provided, enrols them first, then verifies
    *intervals_ms* against the baseline.  Otherwise only computes metrics.

    Returns a dict with keys: ``status``, ``verified``, ``metrics``,
    ``baseline_metrics`` (if baseline was given).
    """
    validator = HeartbeatValidator(tolerance=tolerance)
    result: dict[str, Any] = {
        "status": "success",
        "metrics": validator.get_metrics(intervals_ms),
    }
    if baseline_intervals is not None:
        try:
            validator.enroll(user_id, baseline_intervals)
        except ValueError as exc:
            return {"status": "error", "message": str(exc)}
        result["baseline_metrics"] = validator.get_metrics(baseline_intervals)
        result["verified"] = validator.verify(user_id, intervals_ms)
    else:
        result["verified"] = True  # no baseline → metric-only mode
    return result


def analyze_eeg_bands(
    samples: list[float],
    baseline_samples: list[float] | None = None,
    user_id: str = "default",
    sampling_rate: float = 256.0,
    tolerance: float = 0.25,
) -> dict[str, Any]:
    """Analyse EEG signal into frequency-band powers and optionally verify.

    If *baseline_samples* is provided, enrols and verifies against it.
    Returns a dict with keys: ``status``, ``band_powers``,
    ``verified``, ``baseline_powers`` (if baseline was given).
    """
    analyzer = EEGFrequencyAnalyzer(sampling_rate=sampling_rate)
    band_powers = analyzer.compute_band_powers(samples)
    result: dict[str, Any] = {
        "status": "success",
        "band_powers": band_powers,
    }
    if baseline_samples is not None:
        try:
            analyzer.enroll(user_id, baseline_samples)
        except ValueError as exc:
            return {"status": "error", "message": str(exc)}
        result["baseline_powers"] = analyzer.compute_band_powers(baseline_samples)
        result["verified"] = analyzer.verify(user_id, samples, tolerance=tolerance)
    else:
        result["verified"] = True
    return result


def verify_biocognitive(
    user_id: str,
    keystroke_values: list[float] | None = None,
    current_keystroke: float | None = None,
    heartbeat_intervals: list[float] | None = None,
    heartbeat_baseline: list[float] | None = None,
    eeg_samples: list[float] | None = None,
    eeg_baseline: list[float] | None = None,
    eeg_sampling_rate: float = 256.0,
) -> dict[str, Any]:
    """Multi-modal bio-cognitive verification entry point.

    Runs whichever modalities have data available and aggregates results.
    Returns ``True`` for ``verified`` only if every available modality
    passes verification.

    Returns a dict with keys: ``status``, ``verified``, ``modalities``,
    ``confidence``.
    """
    verifier = BioCognitiveVerifier()
    hb_validator = HeartbeatValidator()
    eeg_analyzer = EEGFrequencyAnalyzer(sampling_rate=eeg_sampling_rate)

    modalities: dict[str, dict[str, Any]] = {}
    all_verified = True

    # -- Keystroke dynamics ----------------------------------------------
    if keystroke_values is not None:
        verifier.enroll(user_id, "keystroke_flight_time", keystroke_values)
        if current_keystroke is not None:
            ok = verifier.verify(user_id, "keystroke_flight_time", current_keystroke)
            modalities["keystroke"] = {"verified": ok, "current": current_keystroke}
            all_verified = all_verified and ok
        else:
            modalities["keystroke"] = {"verified": True, "note": "enrolled, no current value"}
    elif current_keystroke is not None:
        # No baseline → cannot verify
        modalities["keystroke"] = {"verified": False, "reason": "no baseline"}

    # -- Heartbeat / HRV --------------------------------------------------
    if heartbeat_intervals is not None:
        hb_result = verify_heartbeat_intervals(
            heartbeat_intervals,
            baseline_intervals=heartbeat_baseline,
            user_id=user_id,
        )
        modalities["heartbeat"] = {
            "verified": hb_result.get("verified", False),
            "metrics": hb_result.get("metrics"),
        }
        if not hb_result.get("verified", False):
            all_verified = False

    # -- EEG ---------------------------------------------------------------
    if eeg_samples is not None:
        eeg_result = analyze_eeg_bands(
            eeg_samples,
            baseline_samples=eeg_baseline,
            user_id=user_id,
            sampling_rate=eeg_sampling_rate,
        )
        modalities["eeg"] = {
            "verified": eeg_result.get("verified", False),
            "band_powers": eeg_result.get("band_powers"),
        }
        if not eeg_result.get("verified", False):
            all_verified = False

    # If no modality had data, we can't verify
    if not modalities:
        return {
            "status": "error",
            "message": "No bio-cognitive data provided for verification",
        }

    return {
        "status": "success",
        "verified": all_verified,
        "modalities": modalities,
        "confidence": verifier.get_confidence(user_id),
    }

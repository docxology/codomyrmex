"""Bio-Cognitive Verification Module.

Provides behavioral authentication based on user pattern metrics such as
keystroke dynamics and decision latencies.
"""

from __future__ import annotations

from typing import Any

import numpy as np

from codomyrmex.logging_monitoring.core.logger_config import get_logger

logger = get_logger(__name__)


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

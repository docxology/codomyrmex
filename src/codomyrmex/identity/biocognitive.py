"""Bio-Cognitive Verification Module.

Provides behavioral authentication based on User pattern metrics.
"""


import numpy as np

from codomyrmex.logging_monitoring.core.logger_config import get_logger

logger = get_logger(__name__)

class BioCognitiveVerifier:
    """Verifies identity based on behavioral biometrics."""

    def __init__(self):
        """Execute   Init   operations natively."""
        # keyed by user_id -> metric_name -> list of values
        self._baselines: dict[str, dict[str, list[float]]] = {}
        self._thresholds: dict[str, float] = {
            "keystroke_flight_time": 0.15,  # Variance allowed
            "decision_latency": 0.20
        }

    def record_metric(self, user_id: str, metric: str, value: float) -> None:
        """Record a new behavioral metric sample."""
        if user_id not in self._baselines:
            self._baselines[user_id] = {}
        if metric not in self._baselines[user_id]:
            self._baselines[user_id][metric] = []

        self._baselines[user_id][metric].append(value)
        # Keep window of last 100 samples
        if len(self._baselines[user_id][metric]) > 100:
             self._baselines[user_id][metric].pop(0)

    def verify(self, user_id: str, metric: str, current_value: float) -> bool:
        """Verify if current value matches user's baseline."""
        if user_id not in self._baselines or metric not in self._baselines[user_id]:
            logger.warning(f"No baseline for user {user_id} on {metric}")
            return False

        samples = self._baselines[user_id][metric]
        if len(samples) < 10:
            logger.info("Insufficient samples for verification, assuming true for training")
            return True

        mean = np.mean(samples)
        std = np.std(samples)

        # Enforce minimum std to avoid division by zero and allow specific variance
        min_std = 0.01
        effective_std = max(std, min_std)

        # Simple Z-score check
        z_score = abs(current_value - mean) / effective_std

        # Allow deviation up to 2.5 sigma
        is_valid = z_score < 2.5

        if not is_valid:
            logger.warning(f"Bio-cognitive mismatch: {metric} z-score {z_score:.2f}")

        return is_valid

    def enroll(self, user_id: str, metric_type: str, baseline: list[float]) -> None:
        """Enroll a user with a baseline for a specific metric."""
        if user_id not in self._baselines:
            self._baselines[user_id] = {}
        self._baselines[user_id][metric_type] = list(baseline)
        logger.info(f"Enrolled user {user_id} for metric {metric_type}")

    def get_confidence(self, user_id: str) -> float:
        """Calculate aggregate confidence score for a user."""
        if user_id not in self._baselines:
            return 0.0

        # Simple heuristic: more samples = more confidence
        total_samples = sum(len(v) for v in self._baselines[user_id].values())
        return min(total_samples / 100.0, 1.0)

from dataclasses import dataclass

from codomyrmex.logging_monitoring.core.logger_config import get_logger

"""User behavior analysis for security."""

logger = get_logger(__name__)


@dataclass
class BehaviorPattern:
    """Represents a user behavior pattern."""

    pattern_type: str
    frequency: int
    risk_level: str  # low, medium, high
    description: str


@dataclass
class Anomaly:
    """Represents a behavioral anomaly."""

    anomaly_type: str
    severity: str  # low, medium, high, critical
    description: str
    confidence: float  # 0.0 to 1.0


class BehaviorAnalyzer:
    """Analyzes user behavior for security purposes."""

    def __init__(self):
        """Initialize this instance."""

        self.behavior_history: dict[str, list[dict]] = {}
        logger.info("BehaviorAnalyzer initialized")

    SENSITIVE_RESOURCES = {"admin_panel", "database", "credentials", "financial_records", "user_data", "server_config", "security_settings"}

    def analyze_behavior(self, user_id: str, behavior_data: dict) -> list[BehaviorPattern]:
        """Analyze user behavior patterns."""
        if user_id not in self.behavior_history:
            self.behavior_history[user_id] = []

        self.behavior_history[user_id].append(behavior_data)

        patterns = []
        history = self.behavior_history[user_id]

        # Count frequency of each action type in history
        action_counts: dict[str, int] = {}
        for entry in history:
            action = entry.get("action", "unknown")
            action_counts[action] = action_counts.get(action, 0) + 1

        for action, frequency in action_counts.items():
            # Determine risk level based on whether action involves sensitive resources
            resource = behavior_data.get("resource", "")
            if resource in self.SENSITIVE_RESOURCES or action in ("delete", "export", "privilege_escalation"):
                risk_level = "high"
            elif action in ("modify", "download", "access"):
                risk_level = "medium"
            else:
                risk_level = "low"

            patterns.append(
                BehaviorPattern(
                    pattern_type=action,
                    frequency=frequency,
                    risk_level=risk_level,
                    description=f"User performed '{action}' {frequency} time(s)",
                )
            )

        logger.debug(f"Analyzed behavior for user {user_id}")
        return patterns

    def detect_anomalies(self, user_id: str, current_behavior: dict) -> list[Anomaly]:
        """Detect anomalous behavior."""
        if user_id not in self.behavior_history:
            return []

        anomalies = []
        history = self.behavior_history[user_id]

        # Build baseline from history
        historical_login_hours = [
            entry.get("login_hour") for entry in history if entry.get("login_hour") is not None
        ]
        historical_locations = {entry.get("location") for entry in history if entry.get("location")}
        historical_resources = {entry.get("resource") for entry in history if entry.get("resource")}

        # Check login time anomaly
        current_login_hour = current_behavior.get("login_hour")
        if current_login_hour is not None and historical_login_hours:
            avg_hour = sum(historical_login_hours) / len(historical_login_hours)
            if abs(current_login_hour - avg_hour) > 4:
                anomalies.append(
                    Anomaly(
                        anomaly_type="unusual_login_time",
                        severity="medium",
                        description=f"Login at hour {current_login_hour} deviates from average hour {avg_hour:.1f}",
                        confidence=0.75,
                    )
                )

        # Check location anomaly
        current_location = current_behavior.get("location")
        if current_location and historical_locations and current_location not in historical_locations:
            anomalies.append(
                Anomaly(
                    anomaly_type="new_location",
                    severity="high",
                    description=f"Access from new location '{current_location}' not seen in history",
                    confidence=0.8,
                )
            )

        # Check sensitive resource access anomaly
        current_resource = current_behavior.get("resource")
        if (
            current_resource
            and current_resource in self.SENSITIVE_RESOURCES
            and current_resource not in historical_resources
        ):
            anomalies.append(
                Anomaly(
                    anomaly_type="new_sensitive_access",
                    severity="high",
                    description=f"First-time access to sensitive resource '{current_resource}'",
                    confidence=0.85,
                )
            )

        logger.debug(f"Checked for anomalies for user {user_id}")
        return anomalies


def analyze_user_behavior(
    user_id: str,
    behavior_data: dict,
    analyzer: BehaviorAnalyzer | None = None,
) -> list[BehaviorPattern]:
    """Analyze user behavior."""
    if analyzer is None:
        analyzer = BehaviorAnalyzer()
    return analyzer.analyze_behavior(user_id, behavior_data)


def detect_anomalous_behavior(
    user_id: str,
    current_behavior: dict,
    analyzer: BehaviorAnalyzer | None = None,
) -> list[Anomaly]:
    """Detect anomalous behavior."""
    if analyzer is None:
        analyzer = BehaviorAnalyzer()
    return analyzer.detect_anomalies(user_id, current_behavior)


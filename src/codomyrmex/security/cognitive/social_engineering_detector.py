import re
from dataclasses import dataclass

from codomyrmex.logging_monitoring.core.logger_config import get_logger

"""Social engineering detection."""

logger = get_logger(__name__)


@dataclass
class SocialEngineeringIndicator:
    """Represents a social engineering indicator."""

    indicator_type: str
    severity: str  # low, medium, high
    description: str
    confidence: float  # 0.0 to 1.0


class SocialEngineeringDetector:
    """Detects social engineering attempts."""

    def __init__(self):
        self.patterns = {
            "urgency": r"(immediately|urgent|right now|asap|act fast|time is running out|expires today|last chance|limited time)",
            "authority": r"(CEO|director|manager|executive|IT department|admin|supervisor|board|compliance officer)",
            "information_gathering": r"(password|credentials|ssn|social security|bank account|credit card|verify your|confirm your|update your)",
            "reward": r"(congratulations|you've won|claim your prize|selected|lucky winner|reward|free gift|bonus)",
            "fear": r"(account suspended|unauthorized access|security breach|your account|compromised|locked out|legal action|terminated)",
        }
        logger.info("SocialEngineeringDetector initialized")

    def detect(self, communication: str) -> list[SocialEngineeringIndicator]:
        """Detect social engineering indicators in communication."""
        indicators = []
        text_lower = communication.lower()

        for indicator_type, pattern in self.patterns.items():
            matches = re.findall(pattern, text_lower, re.IGNORECASE)
            if indicator_type in ("information_gathering", "fear"):
                severity = "high"
            elif indicator_type in ("urgency", "authority"):
                severity = "medium"
            else:
                severity = "low"

            for match in matches:
                confidence = 0.85 if " " in match else 0.7
                indicators.append(
                    SocialEngineeringIndicator(
                        indicator_type=indicator_type,
                        severity=severity,
                        description=f"Detected {indicator_type} tactic: '{match}'",
                        confidence=confidence,
                    )
                )

        logger.debug("Analyzed communication for social engineering")
        return indicators

    def analyze_communication(self, communication: str) -> dict:
        """Analyze communication for social engineering."""
        indicators = self.detect(communication)

        analysis = {
            "total_indicators": len(indicators),
            "high_severity_count": sum(1 for i in indicators if i.severity == "high"),
            "indicators": indicators,
            "risk_score": self._calculate_risk_score(indicators),
        }

        return analysis

    def _calculate_risk_score(self, indicators: list[SocialEngineeringIndicator]) -> float:
        """Calculate risk score from indicators."""
        if not indicators:
            return 0.0

        total_score = sum(
            i.confidence * (1.0 if i.severity == "high" else 0.5 if i.severity == "medium" else 0.25)
            for i in indicators
        )
        return min(total_score / len(indicators), 1.0)


def detect_social_engineering(
    communication: str,
    detector: SocialEngineeringDetector = None,
) -> list[SocialEngineeringIndicator]:
    """Detect social engineering."""
    if detector is None:
        detector = SocialEngineeringDetector()
    return detector.detect(communication)


def analyze_communication(
    communication: str,
    detector: SocialEngineeringDetector = None,
) -> dict:
    """Analyze communication."""
    if detector is None:
        detector = SocialEngineeringDetector()
    return detector.analyze_communication(communication)


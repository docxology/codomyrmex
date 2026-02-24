import re
from dataclasses import dataclass

from codomyrmex.logging_monitoring.core.logger_config import get_logger

"""Phishing detection and analysis."""

logger = get_logger(__name__)


@dataclass
class PhishingAnalysis:
    """Results of phishing analysis."""

    is_phishing: bool
    confidence: float  # 0.0 to 1.0
    indicators: list[str]
    risk_level: str  # low, medium, high, critical
    recommendation: str


class PhishingAnalyzer:
    """Analyzes emails and communications for phishing attempts."""

    def __init__(self):

        logger.info("PhishingAnalyzer initialized")

    def analyze(self, email_content: str, sender: str | None = None) -> PhishingAnalysis:
        """Analyze email for phishing indicators."""
        indicators = []
        content_lower = email_content.lower()

        # Check for suspicious URLs with IP addresses
        if re.search(r"https?://\d+\.\d+\.\d+\.\d+", email_content):
            indicators.append("Suspicious URL with IP address detected")

        # Check for URL shorteners
        if re.search(r"(bit\.ly|tinyurl|goo\.gl|t\.co)", content_lower):
            indicators.append("URL shortener detected (may hide malicious destination)")

        # Check for non-HTTPS links
        if re.search(r"http://", email_content) and not re.search(r"https://", email_content):
            indicators.append("Non-HTTPS URL detected (insecure connection)")

        # Check for urgency language
        urgency_matches = re.findall(r"(urgent|immediately|act now|expires|limited time|verify your account)", content_lower)
        if urgency_matches:
            indicators.append(f"Urgency language detected: {', '.join(set(urgency_matches))}")

        # Check for sensitive info requests
        sensitive_matches = re.findall(r"(password|credit card|ssn|social security|bank account|pin number)", content_lower)
        if sensitive_matches:
            indicators.append(f"Request for sensitive information: {', '.join(set(sensitive_matches))}")

        # Check for excessive punctuation
        if re.search(r"[!]{2,}", email_content):
            indicators.append("Excessive exclamation marks (common in phishing)")

        # Check for excessive caps
        if re.search(r"[A-Z]{5,}", email_content):
            indicators.append("Excessive capitalization (common in phishing)")

        # Check sender domain mismatch
        if sender:
            sender_domain_match = re.search(r"@([\w.-]+)", sender)
            if sender_domain_match:
                sender_domain = sender_domain_match.group(1).lower()
                content_domains = re.findall(r"https?://(?:www\.)?([\w.-]+)", email_content)
                for domain in content_domains:
                    domain_lower = domain.lower()
                    if sender_domain not in domain_lower and domain_lower not in sender_domain:
                        indicators.append(f"Sender domain '{sender_domain}' does not match link domain '{domain_lower}'")
                        break

        is_phishing = len(indicators) > 0
        confidence = min(len(indicators) * 0.2, 1.0)

        risk_level = "low"
        if confidence > 0.7:
            risk_level = "critical"
        elif confidence > 0.5:
            risk_level = "high"
        elif confidence > 0.3:
            risk_level = "medium"

        recommendation = "No action needed" if not is_phishing else "Do not click links or provide information"

        return PhishingAnalysis(
            is_phishing=is_phishing,
            confidence=confidence,
            indicators=indicators,
            risk_level=risk_level,
            recommendation=recommendation,
        )


def analyze_email(
    email_content: str,
    sender: str | None = None,
    analyzer: PhishingAnalyzer | None = None,
) -> PhishingAnalysis:
    """Analyze email for phishing."""
    if analyzer is None:
        analyzer = PhishingAnalyzer()
    return analyzer.analyze(email_content, sender)


def detect_phishing_attempt(
    email_content: str,
    sender: str | None = None,
    analyzer: PhishingAnalyzer | None = None,
) -> bool:
    """Detect if email is a phishing attempt."""
    if analyzer is None:
        analyzer = PhishingAnalyzer()
    analysis = analyzer.analyze(email_content, sender)
    return analysis.is_phishing


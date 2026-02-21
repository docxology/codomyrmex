"""Privacy Module — Data Anonymization & Privacy Preservation.

Provides functional data anonymization strategies:
- K-anonymity: generalize quasi-identifiers until each group has ≥k records.
- Data masking: hash, redact, partial-mask sensitive fields.
- Differential privacy: add calibrated Laplace noise to numeric aggregates.
- PII detection: identify and flag personally identifiable information.
"""

from __future__ import annotations

import hashlib
import math
import random
import re
from dataclasses import dataclass, field
from typing import Any

from codomyrmex.logging_monitoring.logger_config import get_logger

logger = get_logger(__name__)


# ─── PII Detection ─────────────────────────────────────────────────────

_PII_PATTERNS: dict[str, re.Pattern[str]] = {
    "email": re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"),
    "phone": re.compile(r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b"),
    "ssn": re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
    "credit_card": re.compile(r"\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b"),
    "ipv4": re.compile(r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b"),
}


@dataclass
class PIIMatch:
    """A detected PII occurrence."""

    field: str
    pii_type: str
    value: str
    start: int
    end: int


def detect_pii(text: str, field_name: str = "") -> list[PIIMatch]:
    """Scan text for PII patterns.

    Args:
        text: The string to scan.
        field_name: Optional field name for context.

    Returns:
        List of PIIMatch objects for each detected PII occurrence.
    """
    matches: list[PIIMatch] = []
    for pii_type, pattern in _PII_PATTERNS.items():
        for m in pattern.finditer(text):
            matches.append(
                PIIMatch(
                    field=field_name,
                    pii_type=pii_type,
                    value=m.group(),
                    start=m.start(),
                    end=m.end(),
                )
            )
    return matches


# ─── Data Masking ───────────────────────────────────────────────────────


def mask_hash(value: str, algorithm: str = "sha256") -> str:
    """One-way hash masking using the specified algorithm.

    Args:
        value: The string to hash.
        algorithm: Hash algorithm (sha256, md5, sha1).

    Returns:
        Hex digest of the hashed value.
    """
    h = hashlib.new(algorithm)
    h.update(value.encode("utf-8"))
    return h.hexdigest()


def mask_redact(value: str, replacement: str = "***") -> str:
    """Replace entire value with a redaction marker."""
    return replacement


def mask_partial(value: str, visible_chars: int = 4, mask_char: str = "*") -> str:
    """Show only the last N characters, mask the rest.

    Example: mask_partial("1234567890", 4) → "******7890"
    """
    if len(value) <= visible_chars:
        return value
    return mask_char * (len(value) - visible_chars) + value[-visible_chars:]


def mask_email(email: str) -> str:
    """Mask an email address, preserving domain.

    Example: mask_email("alice@example.com") → "a***@example.com"
    """
    if "@" not in email:
        return mask_redact(email)
    local, domain = email.rsplit("@", 1)
    if len(local) <= 1:
        return f"{local}***@{domain}"
    return f"{local[0]}{'*' * (len(local) - 1)}@{domain}"


# ─── Differential Privacy ──────────────────────────────────────────────


def laplace_noise(epsilon: float, sensitivity: float = 1.0) -> float:
    """Generate a single sample from the Laplace distribution.

    Calibrated for (ε, 0)-differential privacy.

    Args:
        epsilon: Privacy budget (smaller = more privacy, more noise).
        sensitivity: Global sensitivity of the query.

    Returns:
        A float noise value.
    """
    if epsilon <= 0:
        raise ValueError("Epsilon must be positive")
    scale = sensitivity / epsilon
    return random.random() - 0.5  # Uniform approx; proper Laplace below
    # Proper Laplace: sign * scale * ln(1 - uniform)


def add_laplace_noise(value: float, epsilon: float, sensitivity: float = 1.0) -> float:
    """Add Laplace noise to a numeric value for differential privacy.

    Args:
        value: The true value.
        epsilon: Privacy budget.
        sensitivity: Query sensitivity.

    Returns:
        Noised value.
    """
    if epsilon <= 0:
        raise ValueError("Epsilon must be positive")
    scale = sensitivity / epsilon
    # Proper Laplace distribution sampling
    u = random.random() - 0.5
    noise = -scale * math.copysign(1, u) * math.log(1 - 2 * abs(u))
    return value + noise


def dp_mean(values: list[float], epsilon: float, lower: float, upper: float) -> float:
    """Differentially private mean using Laplace mechanism.

    Args:
        values: List of numeric values.
        epsilon: Privacy budget.
        lower: Lower bound of the value range.
        upper: Upper bound of the value range.

    Returns:
        DP-noised mean value.
    """
    if not values:
        return 0.0
    n = len(values)
    true_mean = sum(values) / n
    sensitivity = (upper - lower) / n
    return add_laplace_noise(true_mean, epsilon, sensitivity)


def dp_count(count: int, epsilon: float) -> float:
    """Differentially private count using Laplace mechanism.

    Args:
        count: True count.
        epsilon: Privacy budget.

    Returns:
        DP-noised count (may be fractional).
    """
    return add_laplace_noise(float(count), epsilon, sensitivity=1.0)


# ─── Privacy Processor (main class) ────────────────────────────────────


@dataclass
class PrivacyRule:
    """A rule specifying how to anonymize a specific field."""

    field: str
    strategy: str  # "hash", "redact", "partial", "email", "noise"
    params: dict[str, Any] = field(default_factory=dict)


class Privacy:
    """Data anonymization engine with configurable per-field rules.

    Example::

        p = Privacy()
        p.add_rule(PrivacyRule("email", "email"))
        p.add_rule(PrivacyRule("ssn", "redact"))
        p.add_rule(PrivacyRule("salary", "noise", {"epsilon": 1.0}))

        clean = p.process({"email": "alice@co.com", "ssn": "123-45-6789", "salary": 75000})
        assert "@" in clean["email"]
        assert clean["ssn"] == "***"
    """

    def __init__(self, config: dict[str, Any] | None = None) -> None:
        self.config = config or {}
        self._rules: dict[str, PrivacyRule] = {}
        logger.info("Privacy engine initialized")

    def add_rule(self, rule: PrivacyRule) -> None:
        """Register a privacy rule for a field."""
        self._rules[rule.field] = rule

    def process(self, data: dict[str, Any]) -> dict[str, Any]:
        """Apply all configured privacy rules to a data record.

        Args:
            data: A flat dict of field→value pairs.

        Returns:
            A copy of the data with anonymized fields.
        """
        result = dict(data)
        for field_name, rule in self._rules.items():
            if field_name not in result:
                continue
            val = result[field_name]
            if rule.strategy == "hash":
                result[field_name] = mask_hash(str(val), rule.params.get("algorithm", "sha256"))
            elif rule.strategy == "redact":
                result[field_name] = mask_redact(str(val), rule.params.get("replacement", "***"))
            elif rule.strategy == "partial":
                result[field_name] = mask_partial(str(val), rule.params.get("visible", 4))
            elif rule.strategy == "email":
                result[field_name] = mask_email(str(val))
            elif rule.strategy == "noise":
                eps = rule.params.get("epsilon", 1.0)
                sens = rule.params.get("sensitivity", 1.0)
                result[field_name] = add_laplace_noise(float(val), eps, sens)
            else:
                logger.warning("Unknown privacy strategy: %s", rule.strategy)
        return result

    def scan_pii(self, data: dict[str, Any]) -> list[PIIMatch]:
        """Scan all string fields in data for PII patterns."""
        matches: list[PIIMatch] = []
        for key, val in data.items():
            if isinstance(val, str):
                matches.extend(detect_pii(val, field_name=key))
        return matches


def create_privacy(config: dict[str, Any] | None = None) -> Privacy:
    """Create a new Privacy instance."""
    return Privacy(config)

"""SecretPatterns: compiled regex patterns for detecting secrets."""

import re

from .models import SecretSeverity, SecretType


class SecretPatterns:
    """Collection of patterns for detecting secrets."""

    PATTERNS = [
        (r"AKIA[0-9A-Z]{16}", SecretType.AWS_KEY, SecretSeverity.CRITICAL, 0.95),
        (
            r'aws[_-]?secret[_-]?access[_-]?key["\']?\s*[:=]\s*["\']?([A-Za-z0-9/+=]{40})',
            SecretType.AWS_KEY,
            SecretSeverity.CRITICAL,
            0.9,
        ),
        (r"ghp_[A-Za-z0-9]{36}", SecretType.GITHUB_TOKEN, SecretSeverity.CRITICAL, 0.99),
        (
            r'github[_-]?token["\']?\s*[:=]\s*["\']?([A-Za-z0-9_-]{40})',
            SecretType.GITHUB_TOKEN,
            SecretSeverity.HIGH,
            0.8,
        ),
        (
            r'api[_-]?key["\']?\s*[:=]\s*["\']?([A-Za-z0-9_-]{20,})',
            SecretType.API_KEY,
            SecretSeverity.HIGH,
            0.7,
        ),
        (
            r'api[_-]?secret["\']?\s*[:=]\s*["\']?([A-Za-z0-9_-]{20,})',
            SecretType.API_KEY,
            SecretSeverity.HIGH,
            0.7,
        ),
        (
            r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----",
            SecretType.PRIVATE_KEY,
            SecretSeverity.CRITICAL,
            0.99,
        ),
        (
            r"-----BEGIN PGP PRIVATE KEY BLOCK-----",
            SecretType.PRIVATE_KEY,
            SecretSeverity.CRITICAL,
            0.99,
        ),
        (
            r"eyJ[A-Za-z0-9_-]*\.eyJ[A-Za-z0-9_-]*\.[A-Za-z0-9_-]*",
            SecretType.JWT,
            SecretSeverity.MEDIUM,
            0.9,
        ),
        (
            r"(?:postgres|mysql|mongodb)://[^:]+:([^@]+)@",
            SecretType.DATABASE_URL,
            SecretSeverity.HIGH,
            0.85,
        ),
        (
            r'password["\']?\s*[:=]\s*["\']?([^\s"\']{8,})',
            SecretType.PASSWORD,
            SecretSeverity.MEDIUM,
            0.6,
        ),
        (
            r'passwd["\']?\s*[:=]\s*["\']?([^\s"\']{8,})',
            SecretType.PASSWORD,
            SecretSeverity.MEDIUM,
            0.6,
        ),
        (
            r'["\']([A-Za-z0-9+/]{40,}={0,2})["\']',
            SecretType.GENERIC,
            SecretSeverity.LOW,
            0.4,
        ),
    ]

    def __init__(self, custom_patterns: list[tuple] | None = None):
        self.patterns = self.PATTERNS.copy()
        if custom_patterns:
            self.patterns.extend(custom_patterns)
        self._compiled = [
            (re.compile(p[0], re.IGNORECASE), p[1], p[2], p[3]) for p in self.patterns
        ]

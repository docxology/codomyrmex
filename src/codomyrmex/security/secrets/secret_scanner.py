"""Secret detection in source files.

Regex and entropy-based detection of API keys, tokens,
passwords, and private keys in source code.
"""

from __future__ import annotations

import math
import re
from dataclasses import dataclass
from typing import Any


@dataclass
class SecretFinding:
    """A detected secret in source code.

    Attributes:
        file_path: File containing the secret.
        line_number: Line number.
        secret_type: Type of secret (api_key, token, etc.).
        snippet: Redacted snippet.
        confidence: Detection confidence.
        entropy: Shannon entropy of the match.
    """

    file_path: str
    line_number: int
    secret_type: str
    snippet: str = ""
    confidence: float = 0.8
    entropy: float = 0.0


_SECRET_PATTERNS: list[dict[str, Any]] = [
    {
        "name": "api_key",
        "pattern": r"(?:api[_-]?key|apikey)\s*[=:]\s*['\"]([a-zA-Z0-9_\-]{20,})['\"]",
        "confidence": 0.9,
    },
    {
        "name": "aws_access_key",
        "pattern": r"AKIA[0-9A-Z]{16}",
        "confidence": 0.95,
    },
    {
        "name": "private_key",
        "pattern": r"-----BEGIN (?:RSA |EC )?PRIVATE KEY-----",
        "confidence": 0.99,
    },
    {
        "name": "password",
        "pattern": r"(?:password|passwd|pwd)\s*[=:]\s*['\"]([^'\"]{8,})['\"]",
        "confidence": 0.7,
    },
    {
        "name": "bearer_token",
        "pattern": r"Bearer\s+[a-zA-Z0-9_\-\.]{20,}",
        "confidence": 0.85,
    },
    {
        "name": "generic_secret",
        "pattern": r"(?:secret|token)\s*[=:]\s*['\"]([a-zA-Z0-9_\-]{16,})['\"]",
        "confidence": 0.6,
    },
]


class SecretScanner:
    """Scan source files for exposed secrets.

    Example::

        scanner = SecretScanner()
        findings = scanner.scan_string(source_code, "config.py")
    """

    def __init__(self, min_entropy: float = 3.0) -> None:
        """Initialize this instance."""
        self._min_entropy = min_entropy
        self._patterns = [
            {**p, "compiled": re.compile(p["pattern"], re.IGNORECASE)}
            for p in _SECRET_PATTERNS
        ]

    def scan_string(self, source: str, file_path: str = "") -> list[SecretFinding]:
        """Scan a source code string for secrets.

        Args:
            source: Source code content.
            file_path: File path for reporting.

        Returns:
            List of SecretFinding objects.
        """
        findings: list[SecretFinding] = []
        lines = source.splitlines()

        for i, line in enumerate(lines, 1):
            for pat in self._patterns:
                match = pat["compiled"].search(line)
                if match:
                    matched_text = match.group(0)
                    entropy = self._shannon_entropy(matched_text)

                    # Redact the middle of the match
                    redacted = self._redact(matched_text)

                    findings.append(SecretFinding(
                        file_path=file_path,
                        line_number=i,
                        secret_type=pat["name"],
                        snippet=redacted,
                        confidence=pat["confidence"],
                        entropy=entropy,
                    ))

        return findings

    def scan_lines(self, lines: list[str], file_path: str = "") -> list[SecretFinding]:
        """Scan a list of lines."""
        return self.scan_string("\n".join(lines), file_path)

    @staticmethod
    def _shannon_entropy(text: str) -> float:
        """Calculate Shannon entropy of text."""
        if not text:
            return 0.0
        freq: dict[str, int] = {}
        for ch in text:
            freq[ch] = freq.get(ch, 0) + 1
        length = len(text)
        entropy = 0.0
        for count in freq.values():
            p = count / length
            if p > 0:
                entropy -= p * math.log2(p)
        return entropy

    @staticmethod
    def _redact(text: str, visible: int = 4) -> str:
        """Redact the middle of a string."""
        if len(text) <= visible * 2:
            return "***"
        return text[:visible] + "***" + text[-visible:]


__all__ = ["SecretFinding", "SecretScanner"]

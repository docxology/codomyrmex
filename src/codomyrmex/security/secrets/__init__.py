"""
Security Secrets Module

Secret detection, rotation, and secure storage utilities.
"""

__version__ = "0.1.0"

import base64
import hashlib
import hmac
import json
import os
import re
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple


class SecretType(Enum):
    """Types of secrets that can be detected."""
    API_KEY = "api_key"
    AWS_KEY = "aws_key"
    GITHUB_TOKEN = "github_token"
    PRIVATE_KEY = "private_key"
    PASSWORD = "password"
    JWT = "jwt"
    DATABASE_URL = "database_url"
    GENERIC = "generic"


class SecretSeverity(Enum):
    """Severity levels for detected secrets."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class DetectedSecret:
    """A detected secret in content."""
    secret_type: SecretType
    severity: SecretSeverity
    location: tuple[int, int]  # (start, end) positions
    redacted_value: str
    line_number: int | None = None
    file_path: str | None = None
    context: str = ""
    confidence: float = 1.0

    @property
    def is_high_severity(self) -> bool:
        return self.severity in [SecretSeverity.HIGH, SecretSeverity.CRITICAL]


@dataclass
class ScanResult:
    """Result of a secret scan."""
    secrets_found: list[DetectedSecret] = field(default_factory=list)
    files_scanned: int = 0
    scan_time_ms: float = 0.0

    @property
    def has_secrets(self) -> bool:
        return len(self.secrets_found) > 0

    @property
    def high_severity_count(self) -> int:
        return sum(1 for s in self.secrets_found if s.is_high_severity)


class SecretPatterns:
    """Collection of patterns for detecting secrets."""

    # Pattern definitions: (regex, secret_type, severity, confidence)
    PATTERNS = [
        # AWS
        (r'AKIA[0-9A-Z]{16}', SecretType.AWS_KEY, SecretSeverity.CRITICAL, 0.95),
        (r'aws[_-]?secret[_-]?access[_-]?key["\']?\s*[:=]\s*["\']?([A-Za-z0-9/+=]{40})',
         SecretType.AWS_KEY, SecretSeverity.CRITICAL, 0.9),

        # GitHub
        (r'ghp_[A-Za-z0-9]{36}', SecretType.GITHUB_TOKEN, SecretSeverity.CRITICAL, 0.99),
        (r'github[_-]?token["\']?\s*[:=]\s*["\']?([A-Za-z0-9_-]{40})',
         SecretType.GITHUB_TOKEN, SecretSeverity.HIGH, 0.8),

        # Generic API keys
        (r'api[_-]?key["\']?\s*[:=]\s*["\']?([A-Za-z0-9_-]{20,})',
         SecretType.API_KEY, SecretSeverity.HIGH, 0.7),
        (r'api[_-]?secret["\']?\s*[:=]\s*["\']?([A-Za-z0-9_-]{20,})',
         SecretType.API_KEY, SecretSeverity.HIGH, 0.7),

        # Private keys
        (r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----',
         SecretType.PRIVATE_KEY, SecretSeverity.CRITICAL, 0.99),
        (r'-----BEGIN PGP PRIVATE KEY BLOCK-----',
         SecretType.PRIVATE_KEY, SecretSeverity.CRITICAL, 0.99),

        # JWT
        (r'eyJ[A-Za-z0-9_-]*\.eyJ[A-Za-z0-9_-]*\.[A-Za-z0-9_-]*',
         SecretType.JWT, SecretSeverity.MEDIUM, 0.9),

        # Database URLs
        (r'(?:postgres|mysql|mongodb)://[^:]+:([^@]+)@',
         SecretType.DATABASE_URL, SecretSeverity.HIGH, 0.85),

        # Password patterns
        (r'password["\']?\s*[:=]\s*["\']?([^\s"\']{8,})',
         SecretType.PASSWORD, SecretSeverity.MEDIUM, 0.6),
        (r'passwd["\']?\s*[:=]\s*["\']?([^\s"\']{8,})',
         SecretType.PASSWORD, SecretSeverity.MEDIUM, 0.6),

        # Generic high-entropy strings (potential secrets)
        (r'["\']([A-Za-z0-9+/]{40,}={0,2})["\']',
         SecretType.GENERIC, SecretSeverity.LOW, 0.4),
    ]

    def __init__(self, custom_patterns: list[tuple] | None = None):
        self.patterns = self.PATTERNS.copy()
        if custom_patterns:
            self.patterns.extend(custom_patterns)
        self._compiled = [
            (re.compile(p[0], re.IGNORECASE), p[1], p[2], p[3])
            for p in self.patterns
        ]


class SecretScanner:
    """
    Scan content for secrets.

    Usage:
        scanner = SecretScanner()

        # Scan a string
        result = scanner.scan_text(code)
        for secret in result.secrets_found:
            print(f"Found {secret.secret_type} at line {secret.line_number}")

        # Scan a file
        result = scanner.scan_file("config.py")

        # Scan a directory
        result = scanner.scan_directory("src/")
    """

    # Files to ignore during directory scan
    IGNORE_PATTERNS = [
        r'\.git',
        r'node_modules',
        r'__pycache__',
        r'\.pyc$',
        r'\.min\.js$',
        r'\.lock$',
        r'package-lock\.json$',
    ]

    def __init__(
        self,
        patterns: SecretPatterns | None = None,
        min_confidence: float = 0.5,
    ):
        self.patterns = patterns or SecretPatterns()
        self.min_confidence = min_confidence
        self._ignore_compiled = [re.compile(p) for p in self.IGNORE_PATTERNS]

    def _redact(self, value: str, show_chars: int = 4) -> str:
        """Redact a secret value."""
        if len(value) <= show_chars * 2:
            return "*" * len(value)
        return value[:show_chars] + "..." + value[-show_chars:]

    def _get_line_number(self, text: str, position: int) -> int:
        """Get line number for a position in text."""
        return text[:position].count('\n') + 1

    def _get_context(self, text: str, start: int, end: int, context_chars: int = 50) -> str:
        """Get context around a match."""
        ctx_start = max(0, start - context_chars)
        ctx_end = min(len(text), end + context_chars)
        context = text[ctx_start:ctx_end].replace('\n', ' ')
        return f"...{context}..." if ctx_start > 0 or ctx_end < len(text) else context

    def _should_ignore(self, path: str) -> bool:
        """Check if a path should be ignored."""
        for pattern in self._ignore_compiled:
            if pattern.search(path):
                return True
        return False

    def scan_text(
        self,
        text: str,
        file_path: str | None = None,
    ) -> ScanResult:
        """
        Scan text for secrets.

        Args:
            text: Text content to scan
            file_path: Optional file path for context

        Returns:
            ScanResult with detected secrets
        """
        import time
        start_time = time.time()

        secrets_found = []

        for pattern, secret_type, severity, confidence in self.patterns._compiled:
            if confidence < self.min_confidence:
                continue

            for match in pattern.finditer(text):
                # Get the secret value (use group 1 if exists, else group 0)
                if match.groups():
                    secret_value = match.group(1)
                    location = (match.start(1), match.end(1))
                else:
                    secret_value = match.group(0)
                    location = (match.start(), match.end())

                secrets_found.append(DetectedSecret(
                    secret_type=secret_type,
                    severity=severity,
                    location=location,
                    redacted_value=self._redact(secret_value),
                    line_number=self._get_line_number(text, location[0]),
                    file_path=file_path,
                    context=self._get_context(text, location[0], location[1]),
                    confidence=confidence,
                ))

        return ScanResult(
            secrets_found=secrets_found,
            files_scanned=1 if file_path else 0,
            scan_time_ms=(time.time() - start_time) * 1000,
        )

    def scan_file(self, file_path: str) -> ScanResult:
        """Scan a file for secrets."""
        path = Path(file_path)

        if not path.exists():
            return ScanResult()

        if self._should_ignore(str(path)):
            return ScanResult()

        try:
            text = path.read_text(errors='ignore')
            return self.scan_text(text, str(path))
        except Exception:
            return ScanResult()

    def scan_directory(
        self,
        directory: str,
        extensions: list[str] | None = None,
    ) -> ScanResult:
        """
        Scan a directory for secrets.

        Args:
            directory: Directory path
            extensions: File extensions to scan (e.g., ['.py', '.js'])

        Returns:
            Aggregated ScanResult
        """
        import time
        start_time = time.time()

        all_secrets = []
        files_scanned = 0

        dir_path = Path(directory)
        if not dir_path.is_dir():
            return ScanResult()

        for path in dir_path.rglob("*"):
            if path.is_file():
                if self._should_ignore(str(path)):
                    continue

                if extensions:
                    if path.suffix.lower() not in extensions:
                        continue

                result = self.scan_file(str(path))
                all_secrets.extend(result.secrets_found)
                files_scanned += 1

        return ScanResult(
            secrets_found=all_secrets,
            files_scanned=files_scanned,
            scan_time_ms=(time.time() - start_time) * 1000,
        )


class SecretVault:
    """
    Simple encrypted secret storage.

    Usage:
        vault = SecretVault("secrets.vault", "master_password")

        # Store secrets
        vault.set("api_key", "my-secret-key")
        vault.set("db_password", "super-secret")

        # Retrieve
        api_key = vault.get("api_key")

        # Save to disk
        vault.save()
    """

    def __init__(
        self,
        path: str | None = None,
        master_password: str | None = None,
    ):
        self.path = Path(path) if path else None
        self._secrets: dict[str, str] = {}
        self._key = self._derive_key(master_password) if master_password else None

        if self.path and self.path.exists() and self._key:
            self._load()

    def _derive_key(self, password: str) -> bytes:
        """Derive encryption key from password."""
        # Simple key derivation (use PBKDF2 in production)
        return hashlib.sha256(password.encode()).digest()

    def _encrypt(self, value: str) -> str:
        """Simple XOR encryption (use proper encryption in production)."""
        if not self._key:
            return base64.b64encode(value.encode()).decode()

        key = self._key
        encrypted = bytes(
            c ^ key[i % len(key)]
            for i, c in enumerate(value.encode())
        )
        return base64.b64encode(encrypted).decode()

    def _decrypt(self, encrypted: str) -> str:
        """Decrypt a value."""
        data = base64.b64decode(encrypted)

        if not self._key:
            return data.decode()

        key = self._key
        decrypted = bytes(
            c ^ key[i % len(key)]
            for i, c in enumerate(data)
        )
        return decrypted.decode()

    def set(self, name: str, value: str) -> None:
        """Store a secret."""
        self._secrets[name] = self._encrypt(value)

    def get(self, name: str, default: str | None = None) -> str | None:
        """Retrieve a secret."""
        if name not in self._secrets:
            return default
        return self._decrypt(self._secrets[name])

    def delete(self, name: str) -> bool:
        """Delete a secret."""
        if name in self._secrets:
            del self._secrets[name]
            return True
        return False

    def list_names(self) -> list[str]:
        """List all secret names."""
        return list(self._secrets.keys())

    def save(self) -> None:
        """Save vault to disk."""
        if self.path:
            with open(self.path, 'w') as f:
                json.dump(self._secrets, f)

    def _load(self) -> None:
        """Load vault from disk."""
        if self.path and self.path.exists():
            with open(self.path) as f:
                self._secrets = json.load(f)


def get_secret_from_env(name: str, default: str | None = None) -> str | None:
    """Get a secret from environment variables."""
    return os.environ.get(name, default)


def mask_secret(value: str, show_chars: int = 4) -> str:
    """Mask a secret for display."""
    if len(value) <= show_chars * 2:
        return "*" * len(value)
    return value[:show_chars] + "*" * (len(value) - show_chars * 2) + value[-show_chars:]


def generate_secret(length: int = 32, include_special: bool = True) -> str:
    """Generate a random secret."""
    import secrets
    import string

    chars = string.ascii_letters + string.digits
    if include_special:
        chars += "!@#$%^&*"

    return ''.join(secrets.choice(chars) for _ in range(length))


__all__ = [
    # Enums
    "SecretType",
    "SecretSeverity",
    # Data classes
    "DetectedSecret",
    "ScanResult",
    # Classes
    "SecretPatterns",
    "SecretScanner",
    "SecretVault",
    # Functions
    "get_secret_from_env",
    "mask_secret",
    "generate_secret",
]

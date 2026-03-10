"""SecretScanner: scan text, files, and directories for secrets."""

import re
import time
from pathlib import Path
from typing import ClassVar

from .models import DetectedSecret, ScanResult
from .patterns import SecretPatterns


class SecretScanner:
    """
    Scan content for secrets.

    Usage:
        scanner = SecretScanner()
        result = scanner.scan_text(code)
        for secret in result.secrets_found:
            print(f"Found {secret.secret_type} at line {secret.line_number}")
        result = scanner.scan_file("config.py")
        result = scanner.scan_directory("src/")
    """

    IGNORE_PATTERNS: ClassVar[list] = [
        r"\.git",
        r"node_modules",
        r"__pycache__",
        r"\.pyc$",
        r"\.min\.js$",
        r"\.lock$",
        r"package-lock\.json$",
    ]

    def __init__(self, patterns: SecretPatterns | None = None, min_confidence: float = 0.5):
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
        return text[:position].count("\n") + 1

    def _get_context(self, text: str, start: int, end: int, context_chars: int = 50) -> str:
        """Get context around a match."""
        ctx_start = max(0, start - context_chars)
        ctx_end = min(len(text), end + context_chars)
        context = text[ctx_start:ctx_end].replace("\n", " ")
        return f"...{context}..." if ctx_start > 0 or ctx_end < len(text) else context

    def _should_ignore(self, path: str) -> bool:
        """Check if a path should be ignored."""
        return any(pattern.search(path) for pattern in self._ignore_compiled)

    def _extract_secret(self, text: str, match: re.Match) -> tuple[str, tuple[int, int]]:
        """Extract secret value and location from a regex match."""
        if match.groups():
            return match.group(1), (match.start(1), match.end(1))
        return match.group(0), (match.start(), match.end())

    def scan_text(self, text: str, file_path: str | None = None) -> ScanResult:
        """Scan text for secrets."""
        start_time = time.time()
        secrets_found = []

        for pattern, secret_type, severity, confidence in self.patterns._compiled:
            if confidence < self.min_confidence:
                continue

            for match in pattern.finditer(text):
                secret_value, location = self._extract_secret(text, match)
                secrets_found.append(
                    DetectedSecret(
                        secret_type=secret_type,
                        severity=severity,
                        location=location,
                        redacted_value=self._redact(secret_value),
                        line_number=self._get_line_number(text, location[0]),
                        file_path=file_path,
                        context=self._get_context(text, location[0], location[1]),
                        confidence=confidence,
                    )
                )

        return ScanResult(
            secrets_found=secrets_found,
            files_scanned=1 if file_path else 0,
            scan_time_ms=(time.time() - start_time) * 1000,
        )

    def scan_file(self, file_path: str) -> ScanResult:
        """Scan a file for secrets."""
        path = Path(file_path)
        if not path.exists() or self._should_ignore(str(path)):
            return ScanResult()
        try:
            text = path.read_text(errors="ignore")
            return self.scan_text(text, str(path))
        except Exception as _exc:
            return ScanResult()

    def scan_directory(self, directory: str, extensions: list[str] | None = None) -> ScanResult:
        """Scan a directory for secrets."""
        start_time = time.time()
        all_secrets = []
        files_scanned = 0

        dir_path = Path(directory)
        if not dir_path.is_dir():
            return ScanResult()

        for path in dir_path.rglob("*"):
            if not path.is_file() or self._should_ignore(str(path)):
                continue
            if extensions and path.suffix.lower() not in extensions:
                continue
            result = self.scan_file(str(path))
            all_secrets.extend(result.secrets_found)
            files_scanned += 1

        return ScanResult(
            secrets_found=all_secrets,
            files_scanned=files_scanned,
            scan_time_ms=(time.time() - start_time) * 1000,
        )

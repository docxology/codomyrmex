"""
Security Scanning Module

Static and dynamic application security testing.
"""

__version__ = "0.1.0"

import json
import re
import threading
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple


class Severity(Enum):
    """Severity levels for findings."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class FindingType(Enum):
    """Types of security findings."""
    SQL_INJECTION = "sql_injection"
    XSS = "xss"
    PATH_TRAVERSAL = "path_traversal"
    COMMAND_INJECTION = "command_injection"
    HARDCODED_SECRET = "hardcoded_secret"
    INSECURE_RANDOM = "insecure_random"
    WEAK_CRYPTO = "weak_crypto"
    EXPOSED_DEBUG = "exposed_debug"
    INSECURE_DESERIALIZATION = "insecure_deserialization"
    OPEN_REDIRECT = "open_redirect"


@dataclass
class SecurityFinding:
    """A security vulnerability finding."""
    id: str
    finding_type: FindingType
    severity: Severity
    title: str
    description: str
    file_path: str = ""
    line_number: int = 0
    code_snippet: str = ""
    remediation: str = ""
    confidence: float = 1.0
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "type": self.finding_type.value,
            "severity": self.severity.value,
            "title": self.title,
            "description": self.description,
            "file": self.file_path,
            "line": self.line_number,
            "remediation": self.remediation,
        }


@dataclass
class ScanResult:
    """Result of a security scan."""
    scan_id: str
    started_at: datetime = field(default_factory=datetime.now)
    completed_at: datetime | None = None
    findings: list[SecurityFinding] = field(default_factory=list)
    files_scanned: int = 0
    errors: list[str] = field(default_factory=list)

    @property
    def is_complete(self) -> bool:
        """Check if scan is complete."""
        return self.completed_at is not None

    @property
    def finding_count(self) -> int:
        """Get total finding count."""
        return len(self.findings)

    @property
    def critical_count(self) -> int:
        """Get critical finding count."""
        return sum(1 for f in self.findings if f.severity == Severity.CRITICAL)

    @property
    def high_count(self) -> int:
        """Get high finding count."""
        return sum(1 for f in self.findings if f.severity == Severity.HIGH)

    def findings_by_severity(self, severity: Severity) -> list[SecurityFinding]:
        """Get findings by severity."""
        return [f for f in self.findings if f.severity == severity]

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "scan_id": self.scan_id,
            "files_scanned": self.files_scanned,
            "total_findings": self.finding_count,
            "critical": self.critical_count,
            "high": self.high_count,
        }


class SecurityRule(ABC):
    """Base class for security rules."""

    @property
    @abstractmethod
    def id(self) -> str:
        """Get rule ID."""
        pass

    @property
    @abstractmethod
    def finding_type(self) -> FindingType:
        """Get finding type."""
        pass

    @abstractmethod
    def check(self, content: str, file_path: str) -> list[SecurityFinding]:
        """Check content for vulnerabilities."""
        pass


class PatternRule(SecurityRule):
    """Rule based on regex patterns."""

    def __init__(
        self,
        rule_id: str,
        finding_type: FindingType,
        pattern: str,
        severity: Severity,
        title: str,
        description: str,
        remediation: str = "",
    ):
        """Execute   Init   operations natively."""
        self._id = rule_id
        self._finding_type = finding_type
        self._pattern = re.compile(pattern, re.IGNORECASE | re.MULTILINE)
        self._severity = severity
        self._title = title
        self._description = description
        self._remediation = remediation
        self._counter = 0

    @property
    def id(self) -> str:
        """Execute Id operations natively."""
        return self._id

    @property
    def finding_type(self) -> FindingType:
        """Execute Finding Type operations natively."""
        return self._finding_type

    def check(self, content: str, file_path: str) -> list[SecurityFinding]:
        """Execute Check operations natively."""
        findings = []
        lines = content.split('\n')

        for i, line in enumerate(lines, 1):
            if self._pattern.search(line):
                self._counter += 1
                findings.append(SecurityFinding(
                    id=f"{self._id}_{self._counter}",
                    finding_type=self._finding_type,
                    severity=self._severity,
                    title=self._title,
                    description=self._description,
                    file_path=file_path,
                    line_number=i,
                    code_snippet=line.strip()[:100],
                    remediation=self._remediation,
                ))

        return findings


class SQLInjectionRule(PatternRule):
    """Detects potential SQL injection vulnerabilities."""

    def __init__(self):
        """Execute   Init   operations natively."""
        super().__init__(
            rule_id="SQL001",
            finding_type=FindingType.SQL_INJECTION,
            pattern=r'(execute|query|cursor)\s*\(\s*["\'].*%s|format\s*\(',
            severity=Severity.HIGH,
            title="Potential SQL Injection",
            description="User input may be directly concatenated into SQL query",
            remediation="Use parameterized queries or prepared statements",
        )


class HardcodedSecretRule(PatternRule):
    """Detects hardcoded secrets."""

    def __init__(self):
        """Execute   Init   operations natively."""
        super().__init__(
            rule_id="SEC001",
            finding_type=FindingType.HARDCODED_SECRET,
            pattern=r'(password|api_key|secret|token)\s*=\s*["\'][^"\']{8,}["\']',
            severity=Severity.HIGH,
            title="Hardcoded Secret",
            description="Sensitive value appears to be hardcoded",
            remediation="Use environment variables or a secrets manager",
        )


class CommandInjectionRule(PatternRule):
    """Detects potential command injection."""

    def __init__(self):
        """Execute   Init   operations natively."""
        super().__init__(
            rule_id="CMD001",
            finding_type=FindingType.COMMAND_INJECTION,
            pattern=r'(os\.system|subprocess\.call|subprocess\.run)\s*\([^)]*\+',
            severity=Severity.CRITICAL,
            title="Potential Command Injection",
            description="User input may be used in shell command",
            remediation="Use subprocess with shell=False and pass args as list",
        )


class InsecureRandomRule(PatternRule):
    """Detects use of insecure random."""

    def __init__(self):
        """Execute   Init   operations natively."""
        super().__init__(
            rule_id="RND001",
            finding_type=FindingType.INSECURE_RANDOM,
            pattern=r'random\.(random|randint|choice)\s*\(',
            severity=Severity.MEDIUM,
            title="Insecure Random Number Generator",
            description="Using random module for security-sensitive operation",
            remediation="Use secrets module for cryptographic randomness",
        )


class SecurityScanner:
    """
    Static application security testing scanner.

    Usage:
        scanner = SecurityScanner()

        # Scan a file
        result = scanner.scan_file("app.py")

        # Scan a directory
        result = scanner.scan_directory("src/")

        for finding in result.findings:
            print(f"{finding.severity.value}: {finding.title}")
    """

    def __init__(self):
        """Execute   Init   operations natively."""
        self._rules: list[SecurityRule] = []
        self._counter = 0
        self._lock = threading.Lock()

        # Register default rules
        self._register_default_rules()

    def _register_default_rules(self) -> None:
        """Register default security rules."""
        self._rules.extend([
            SQLInjectionRule(),
            HardcodedSecretRule(),
            CommandInjectionRule(),
            InsecureRandomRule(),
        ])

    def add_rule(self, rule: SecurityRule) -> "SecurityScanner":
        """Add a security rule."""
        self._rules.append(rule)
        return self

    def _get_scan_id(self) -> str:
        """Generate unique scan ID."""
        with self._lock:
            self._counter += 1
            return f"scan_{self._counter}"

    def scan_content(self, content: str, file_path: str = "<string>") -> list[SecurityFinding]:
        """Scan content for vulnerabilities."""
        findings = []
        for rule in self._rules:
            findings.extend(rule.check(content, file_path))
        return findings

    def scan_file(self, file_path: str) -> ScanResult:
        """
        Scan a file for vulnerabilities.

        Args:
            file_path: Path to file

        Returns:
            ScanResult with findings
        """
        result = ScanResult(scan_id=self._get_scan_id())

        try:
            path = Path(file_path)
            if not path.exists():
                result.errors.append(f"File not found: {file_path}")
                result.completed_at = datetime.now()
                return result

            content = path.read_text(encoding='utf-8', errors='ignore')
            result.findings = self.scan_content(content, file_path)
            result.files_scanned = 1

        except Exception as e:
            result.errors.append(str(e))

        result.completed_at = datetime.now()
        return result

    def scan_directory(
        self,
        dir_path: str,
        extensions: list[str] | None = None,
        exclude_dirs: list[str] | None = None,
    ) -> ScanResult:
        """
        Scan a directory for vulnerabilities.

        Args:
            dir_path: Path to directory
            extensions: File extensions to scan (default: ['.py'])
            exclude_dirs: Directories to exclude

        Returns:
            ScanResult with findings
        """
        result = ScanResult(scan_id=self._get_scan_id())
        extensions = extensions or ['.py']
        exclude_dirs = exclude_dirs or ['venv', '.venv', 'node_modules', '__pycache__']

        try:
            path = Path(dir_path)
            if not path.is_dir():
                result.errors.append(f"Not a directory: {dir_path}")
                result.completed_at = datetime.now()
                return result

            for file_path in path.rglob('*'):
                # Skip excluded directories
                if any(excl in file_path.parts for excl in exclude_dirs):
                    continue

                # Check extension
                if file_path.suffix not in extensions:
                    continue

                if not file_path.is_file():
                    continue

                try:
                    content = file_path.read_text(encoding='utf-8', errors='ignore')
                    findings = self.scan_content(content, str(file_path))
                    result.findings.extend(findings)
                    result.files_scanned += 1
                except Exception as e:
                    result.errors.append(f"Error scanning {file_path}: {e}")

        except Exception as e:
            result.errors.append(str(e))

        result.completed_at = datetime.now()
        return result


__all__ = [
    # Enums
    "Severity",
    "FindingType",
    # Data classes
    "SecurityFinding",
    "ScanResult",
    # Rules
    "SecurityRule",
    "PatternRule",
    "SQLInjectionRule",
    "HardcodedSecretRule",
    "CommandInjectionRule",
    "InsecureRandomRule",
    # Core
    "SecurityScanner",
]

from .vulnerability_scanner import *  # noqa: E402, F401, F403

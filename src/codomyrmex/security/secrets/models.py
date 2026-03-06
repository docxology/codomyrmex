"""Secret detection data models: SecretType, SecretSeverity, DetectedSecret, ScanResult."""

from dataclasses import dataclass, field
from enum import Enum


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
    location: tuple[int, int]
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

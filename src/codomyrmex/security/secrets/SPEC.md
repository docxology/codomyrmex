# Technical Specification - Secrets

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

**Module**: `codomyrmex.security.secrets`  
**Last Updated**: 2026-01-29

## 1. Purpose

Secret detection, rotation, and secure storage management

## 2. Architecture

### 2.1 Components

```
secrets/
├── __init__.py          # Module exports
├── README.md            # Documentation
├── AGENTS.md            # Agent guidelines
├── SPEC.md              # This file
├── PAI.md               # Personal AI context
└── core.py              # Core implementation
```

### 2.2 Dependencies

- Python 3.10+
- Parent module: `security`

## 3. Interfaces

### 3.1 Public API

```python
# Primary exports from codomyrmex.security.secrets
from codomyrmex.security.secrets import (
    SecretType,          # Enum — API_KEY, AWS_KEY, GITHUB_TOKEN, PRIVATE_KEY,
                         #   PASSWORD, JWT, DATABASE_URL, GENERIC
    SecretSeverity,      # Enum — LOW, MEDIUM, HIGH, CRITICAL
    DetectedSecret,      # Dataclass — detected secret (secret_type, severity, location,
                         #   redacted_value, line_number, file_path, context, confidence);
                         #   has .is_high_severity
    ScanResult,          # Dataclass — scan result (secrets_found, files_scanned,
                         #   scan_time_ms); has .has_secrets, .high_severity_count
    SecretPatterns,      # Pattern collection with 12 built-in detection regexes;
                         #   accepts custom_patterns in constructor
    SecretScanner,       # Main scanner — scan_text(), scan_file(), scan_directory();
                         #   configurable min_confidence threshold
    SecretVault,         # Encrypted secret storage — set(), get(), delete(),
                         #   list_names(), save(); password-derived key
    get_secret_from_env, # Utility — read secret from os.environ
    mask_secret,         # Utility — mask a secret string for display
    generate_secret,     # Utility — generate random secret (stdlib secrets module)
)

# Key class signatures:

class SecretScanner:
    def __init__(self, patterns: SecretPatterns | None = None,
                 min_confidence: float = 0.5): ...
    def scan_text(self, text: str, file_path: str | None = None) -> ScanResult: ...
    def scan_file(self, file_path: str) -> ScanResult: ...
    def scan_directory(self, directory: str,
                       extensions: list[str] | None = None) -> ScanResult: ...

class SecretVault:
    def __init__(self, path: str | None = None,
                 master_password: str | None = None): ...
    def set(self, name: str, value: str) -> None: ...
    def get(self, name: str, default: str | None = None) -> str | None: ...
    def delete(self, name: str) -> bool: ...
    def list_names(self) -> list[str]: ...
    def save(self) -> None: ...

def get_secret_from_env(name: str, default: str | None = None) -> str | None: ...
def mask_secret(value: str, show_chars: int = 4) -> str: ...
def generate_secret(length: int = 32, include_special: bool = True) -> str: ...
```

### 3.2 Configuration

Environment variables:
- `CODOMYRMEX_*`: Configuration options

## 4. Implementation Notes

### 4.1 Design Decisions

1. **Confidence-gated detection**: Each pattern carries a confidence score (0.0-1.0); `SecretScanner` filters matches below `min_confidence` (default 0.5) to reduce noise.
2. **Stdlib secrets module workaround**: `generate_secret()` temporarily removes the package from `sys.modules` to import the stdlib `secrets` module, which is shadowed by the `codomyrmex.security.secrets` package name.
3. **XOR encryption in SecretVault**: The vault uses simple XOR with a SHA-256-derived key for demonstration purposes; it is explicitly not production-grade cryptography.

### 4.2 Limitations

- `SecretVault` uses XOR encryption, which is not semantically secure; production deployments should use AES-GCM or a dedicated secrets manager.
- Pattern-based secret detection can produce false positives on base64-encoded content or test fixtures.
- No secret rotation or expiration tracking is implemented.

## 5. Testing

```bash
# Run tests for this module
uv run pytest src/codomyrmex/tests/unit/security/secrets/
```

## 6. Future Considerations

- Replace XOR encryption in `SecretVault` with AES-GCM using the `cryptography` library and PBKDF2 key derivation.
- Add secret rotation tracking with expiration timestamps and rotation reminders.
- Support integration with external secrets managers (AWS Secrets Manager, HashiCorp Vault).

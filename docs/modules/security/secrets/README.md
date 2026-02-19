# Security Secrets Submodule

**Version**: v0.1.7 | **Source**: [`src/codomyrmex/security/secrets/__init__.py`](../../../../src/codomyrmex/security/secrets/__init__.py)

## Overview

Secret detection, scanning, vault storage, and helper utilities. Provides 13 built-in regex patterns for detecting API keys, tokens, private keys, passwords, and other sensitive data in source code and configuration files.

## Components

| Class / Function | Description |
|------------------|-------------|
| `SecretScanner` | Main scanner. Scans text, files, and directories for secrets with configurable confidence thresholds |
| `SecretPatterns` | Collection of 13 regex patterns with type, severity, and confidence metadata. Extensible via `custom_patterns` |
| `DetectedSecret` | Dataclass for a detected secret with `is_high_severity` property |
| `ScanResult` | Dataclass aggregating detections with `has_secrets` and `high_severity_count` properties |
| `SecretVault` | Simple encrypted key-value secret storage using XOR encryption (development use only) |
| `get_secret_from_env()` | Retrieve secrets from environment variables |
| `mask_secret()` | Mask a secret string for safe display (e.g., `AKIA...CDEF`) |
| `generate_secret()` | Generate a cryptographically random secret string using `secrets` module |

## Enums

### SecretType (8 values)
`API_KEY` | `AWS_KEY` | `GITHUB_TOKEN` | `PRIVATE_KEY` | `PASSWORD` | `JWT` | `DATABASE_URL` | `GENERIC`

### SecretSeverity (4 values)
`LOW` | `MEDIUM` | `HIGH` | `CRITICAL`

## Built-in Patterns

| Pattern | Type | Severity | Confidence |
|---------|------|----------|------------|
| `AKIA[0-9A-Z]{16}` | AWS_KEY | CRITICAL | 0.95 |
| AWS secret access key | AWS_KEY | CRITICAL | 0.90 |
| `ghp_[A-Za-z0-9]{36}` | GITHUB_TOKEN | CRITICAL | 0.99 |
| GitHub token assignment | GITHUB_TOKEN | HIGH | 0.80 |
| API key assignment | API_KEY | HIGH | 0.70 |
| API secret assignment | API_KEY | HIGH | 0.70 |
| RSA/EC/OPENSSH private key header | PRIVATE_KEY | CRITICAL | 0.99 |
| PGP private key header | PRIVATE_KEY | CRITICAL | 0.99 |
| JWT token (`eyJ...`) | JWT | MEDIUM | 0.90 |
| Database connection URL with password | DATABASE_URL | HIGH | 0.85 |
| Password assignment (`password`) | PASSWORD | MEDIUM | 0.60 |
| Password assignment (`passwd`) | PASSWORD | MEDIUM | 0.60 |
| Generic high-entropy string (40+ base64 chars) | GENERIC | LOW | 0.40 |

## Usage

```python
from codomyrmex.security.secrets import SecretScanner, SecretVault, mask_secret, generate_secret

# Scan text for secrets
scanner = SecretScanner(min_confidence=0.7)
result = scanner.scan_text('aws_secret_access_key = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"')
for secret in result.secrets_found:
    print(f"{secret.secret_type.value}: {secret.redacted_value} (line {secret.line_number})")

# Scan directory
result = scanner.scan_directory("src/", extensions=[".py", ".env", ".yml"])

# Vault operations (development use only)
vault = SecretVault("secrets.vault", "master_password")
vault.set("api_key", "my-secret-key")
api_key = vault.get("api_key")
vault.save()

# Helper functions
masked = mask_secret("AKIAIOSFODNN7EXAMPLE")  # "AKIA************MPLE"
new_secret = generate_secret(length=64, include_special=True)
```

## SecretVault Caveat

`SecretVault` uses XOR encryption with SHA-256 key derivation. This is explicitly **not production-grade** (noted in source comments). For production use, employ proper encryption libraries (e.g., `cryptography.fernet`).

## Ignore Patterns

`SecretScanner` automatically skips files matching these patterns during directory scans:
- `.git`, `node_modules`, `__pycache__`
- `.pyc`, `.min.js`, `.lock`, `package-lock.json`

## Dependencies

No external dependencies. Uses only Python standard library (`re`, `os`, `json`, `base64`, `hashlib`, `hmac`, `secrets`, `pathlib`).

## Tests

[`src/codomyrmex/tests/unit/security/secrets/test_secrets.py`](../../../../src/codomyrmex/tests/unit/security/secrets/test_secrets.py)

## Navigation

- **Parent**: [Security Module](../README.md)
- **Source**: [`src/codomyrmex/security/secrets/`](../../../../src/codomyrmex/security/secrets/)

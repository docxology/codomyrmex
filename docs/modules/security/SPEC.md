# Security Module - Design Specification

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Purpose

This specification defines the design principles, functional requirements, architecture, and key data models for the Codomyrmex Security module. The module provides a comprehensive, multi-domain security platform spanning 8 submodules.

## Design Principles

1. **Defense in Depth**: Multiple overlapping security layers across digital, physical, cognitive, and theoretical domains ensure no single point of failure.

2. **Separation of Concerns**: Each of the 8 submodules (digital, physical, cognitive, theory, audit, compliance, scanning, secrets) is independently importable and testable. Submodules communicate via well-defined dataclass interfaces.

3. **Graceful Degradation**: All submodule imports use `try/except ImportError` blocks with `*_AVAILABLE` boolean flags. Missing optional dependencies (e.g., `cryptography`, `pyOpenSSL`) disable features without crashing:
   ```python
   try:
       from .digital import VulnerabilityScanner, ...
       DIGITAL_AVAILABLE = True
   except ImportError:
       DIGITAL_AVAILABLE = False
   ```

4. **Compliance-First**: Built-in support for SOC2, HIPAA, GDPR, PCI-DSS, ISO 27001, and custom compliance frameworks with pre-built control definitions.

5. **Thread Safety**: Core components (`SecurityScanner`, `AuditLogger`, `ComplianceChecker`, `InMemoryAuditStore`, `FileAuditStore`) use `threading.Lock` for concurrent access safety.

6. **Extensible Rules**: Abstract base classes (`SecurityRule`, `AuditStore`, `ControlChecker`) allow custom implementations to extend built-in functionality.

## Functional Requirements

### Scanning (FR-1 through FR-4)
1. **FR-1**: Scan individual files for security vulnerabilities using regex-based pattern rules
2. **FR-2**: Scan directories recursively with configurable file extensions and exclusion patterns
3. **FR-3**: Detect SQL injection, hardcoded secrets, command injection, insecure random via built-in rules
4. **FR-4**: Support custom `SecurityRule` subclasses registered at runtime

### Secrets (FR-5 through FR-8)
5. **FR-5**: Detect 13 secret patterns (AWS keys, GitHub tokens, API keys, private keys, JWTs, database URLs, passwords, generic high-entropy strings)
6. **FR-6**: Scan text, files, and directories with confidence-based filtering
7. **FR-7**: Provide encrypted secret vault with XOR-based encryption (development only)
8. **FR-8**: Offer helper functions: `get_secret_from_env()`, `mask_secret()`, `generate_secret()`

### Audit (FR-9 through FR-11)
9. **FR-9**: Log typed audit events with 11 event types and 5 severity levels
10. **FR-10**: Provide pluggable storage backends (in-memory, file-based) via `AuditStore` ABC
11. **FR-11**: Support time-range, event-type, and actor-based event queries

### Compliance (FR-12 through FR-14)
12. **FR-12**: Define controls for 6 compliance frameworks with status tracking
13. **FR-13**: Execute compliance assessments producing scored reports
14. **FR-14**: Support custom `ControlChecker` implementations via ABC

### Digital (FR-15 through FR-17)
15. **FR-15**: Provide vulnerability scanning, secrets detection, and security analysis via 8 component files
16. **FR-16**: Support encryption/decryption, SSL certificate validation, and security monitoring
17. **FR-17**: Generate security reports

## Architecture Overview

The module follows a hierarchical structure:

```
security/
    __init__.py          # Master exports, conditional imports, dynamic __all__
    scanning/            # Static application security testing
    secrets/             # Secret detection and vault
    audit/               # Audit logging and event tracking
    compliance/          # Compliance checking and policy enforcement
    digital/             # Digital security (8 component files)
    physical/            # Physical security (5 component files)
    cognitive/           # Cognitive security (5 component files)
    theory/              # Security theory (6 component files)
```

The top-level `__init__.py` re-exports from all submodules using conditional import blocks and builds `__all__` dynamically based on which submodules are available.

## Key Data Models

### scanning.SecurityFinding
| Field | Type | Description |
|-------|------|-------------|
| `id` | `str` | Unique finding identifier |
| `finding_type` | `FindingType` | Enum: SQL_INJECTION, XSS, PATH_TRAVERSAL, COMMAND_INJECTION, HARDCODED_SECRET, INSECURE_RANDOM, WEAK_CRYPTO, EXPOSED_DEBUG, INSECURE_DESERIALIZATION, OPEN_REDIRECT |
| `severity` | `Severity` | Enum: CRITICAL, HIGH, MEDIUM, LOW, INFO |
| `title` | `str` | Finding title |
| `description` | `str` | Detailed description |
| `file_path` | `str` | Source file path |
| `line_number` | `int` | Line number |
| `code_snippet` | `str` | Relevant code (max 100 chars) |
| `remediation` | `str` | Fix recommendation |
| `confidence` | `float` | Confidence score (0.0-1.0) |

### secrets.DetectedSecret
| Field | Type | Description |
|-------|------|-------------|
| `secret_type` | `SecretType` | Enum: API_KEY, AWS_KEY, GITHUB_TOKEN, PRIVATE_KEY, PASSWORD, JWT, DATABASE_URL, GENERIC |
| `severity` | `SecretSeverity` | Enum: LOW, MEDIUM, HIGH, CRITICAL |
| `location` | `Tuple[int, int]` | Start/end positions in text |
| `redacted_value` | `str` | Masked secret value |
| `line_number` | `Optional[int]` | Line number |
| `file_path` | `Optional[str]` | Source file path |
| `confidence` | `float` | Pattern confidence score |

### audit.AuditEvent
| Field | Type | Description |
|-------|------|-------------|
| `id` | `str` | Unique event ID (auto-generated) |
| `event_type` | `AuditEventType` | Enum: AUTH_LOGIN, AUTH_LOGOUT, AUTH_FAILED, DATA_ACCESS, DATA_CREATE, DATA_UPDATE, DATA_DELETE, PERMISSION_CHANGE, CONFIG_CHANGE, SYSTEM_ERROR, ADMIN_ACTION |
| `severity` | `AuditSeverity` | Enum: DEBUG, INFO, WARNING, ERROR, CRITICAL |
| `action` | `str` | Action description |
| `actor` | `str` | Who performed the action |
| `resource` | `str` | Affected resource |
| `signature` | `str` | SHA-256 integrity signature (property) |

### compliance.ComplianceReport
| Field | Type | Description |
|-------|------|-------------|
| `report_id` | `str` | Unique report ID |
| `framework` | `ComplianceFramework` | Enum: SOC2, HIPAA, GDPR, PCI_DSS, ISO27001, CUSTOM |
| `results` | `List[ControlResult]` | Individual control results |
| `compliance_score` | `float` | Computed score 0-100 (property) |
| `passed_controls` | `int` | Count of passed controls (property) |
| `failed_controls` | `int` | Count of failed controls (property) |

## Configuration

- **Environment variables**: Used via `get_secret_from_env()` for secret retrieval
- **File-based**: `FileAuditStore` persists audit logs to configurable file paths; `SecretVault` stores encrypted secrets to disk
- **Runtime configuration**: `SecurityScanner` accepts custom rules via `add_rule()`; `ComplianceChecker` accepts controls and checkers via `add_control()` and `add_checker()`

## Navigation

- **Parent**: [README.md](README.md)
- **Technical Overview**: [technical_overview.md](technical_overview.md)
- **Root**: [../../../README.md](../../../README.md)

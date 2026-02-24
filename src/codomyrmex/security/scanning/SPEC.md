# Technical Specification - Scanning

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

**Module**: `codomyrmex.security.scanning`  
**Last Updated**: 2026-01-29

## 1. Purpose

SAST/DAST integration for automated security testing

## 2. Architecture

### 2.1 Components

```
scanning/
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
# Primary exports from codomyrmex.security.scanning
from codomyrmex.security.scanning import (
    Severity,            # Enum — CRITICAL, HIGH, MEDIUM, LOW, INFO
    FindingType,         # Enum — SQL_INJECTION, XSS, PATH_TRAVERSAL, COMMAND_INJECTION,
                         #   HARDCODED_SECRET, INSECURE_RANDOM, WEAK_CRYPTO, EXPOSED_DEBUG,
                         #   INSECURE_DESERIALIZATION, OPEN_REDIRECT
    SecurityFinding,     # Dataclass — single vulnerability finding (id, finding_type,
                         #   severity, title, description, file_path, line_number,
                         #   code_snippet, remediation, confidence, metadata)
    ScanResult,          # Dataclass — scan result container (scan_id, findings,
                         #   files_scanned, errors); has .finding_count, .critical_count,
                         #   .high_count, .findings_by_severity()
    SecurityRule,        # ABC — base rule interface (id, finding_type, check)
    PatternRule,         # Regex-based rule implementation
    SQLInjectionRule,    # Built-in rule: detects SQL injection (SQL001, HIGH)
    HardcodedSecretRule, # Built-in rule: detects hardcoded secrets (SEC001, HIGH)
    CommandInjectionRule,# Built-in rule: detects command injection (CMD001, CRITICAL)
    InsecureRandomRule,  # Built-in rule: detects insecure random usage (RND001, MEDIUM)
    SecurityScanner,     # Main service — scan_content(), scan_file(), scan_directory(),
                         #   add_rule()
)

# Key class signatures:

class SecurityRule(ABC):
    @property
    def id(self) -> str: ...
    @property
    def finding_type(self) -> FindingType: ...
    def check(self, content: str, file_path: str) -> list[SecurityFinding]: ...

class SecurityScanner:
    def __init__(self): ...
    def add_rule(self, rule: SecurityRule) -> "SecurityScanner": ...
    def scan_content(self, content: str, file_path: str = "<string>") -> list[SecurityFinding]: ...
    def scan_file(self, file_path: str) -> ScanResult: ...
    def scan_directory(self, dir_path: str, extensions: list[str] | None = None,
                       exclude_dirs: list[str] | None = None) -> ScanResult: ...
```

### 3.2 Configuration

Environment variables:
- `CODOMYRMEX_*`: Configuration options

## 4. Implementation Notes

### 4.1 Design Decisions

1. **Regex-based pattern matching**: All built-in rules use compiled regex patterns with `IGNORECASE | MULTILINE` flags for broad detection without requiring AST parsing.
2. **Pluggable rule architecture**: `SecurityScanner` accepts arbitrary `SecurityRule` subclasses via `add_rule()`, enabling custom vulnerability checks beyond the four built-in rules.
3. **Default exclusion directories**: `scan_directory()` excludes `venv`, `.venv`, `node_modules`, and `__pycache__` by default to avoid scanning generated or vendored code.

### 4.2 Limitations

- Pattern-based detection produces false positives; no AST or data-flow analysis is performed.
- Only Python source files (`.py`) are scanned by default; other languages require explicit `extensions` configuration.
- No CVSS scoring or CWE/CVE mapping is attached to findings.

## 5. Testing

```bash
# Run tests for this module
uv run pytest src/codomyrmex/tests/unit/security/scanning/
```

## 6. Future Considerations

- Add AST-based taint analysis for Python to reduce false positives on SQL injection and command injection rules.
- Map findings to CWE identifiers and attach CVSS v3.1 base scores.
- Support multi-language scanning (JavaScript, Go, Java) with language-specific rule sets.

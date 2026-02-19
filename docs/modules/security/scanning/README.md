# Security Scanning Submodule

**Version**: v0.1.7 | **Source**: [`src/codomyrmex/security/scanning/__init__.py`](../../../../src/codomyrmex/security/scanning/__init__.py)

## Overview

Static application security testing (SAST) scanner with an extensible rule engine. Scans Python source files for common vulnerability patterns using regex-based rules.

## Components

| Class | Description |
|-------|-------------|
| `SecurityScanner` | Main scanner engine. Manages rules, scans files/directories, returns `ScanResult` |
| `SecurityFinding` | Dataclass representing a single vulnerability finding |
| `ScanResult` | Dataclass aggregating findings with properties: `finding_count`, `critical_count`, `high_count`, `is_complete` |
| `SecurityRule` | Abstract base class for all scanning rules |
| `PatternRule` | Concrete rule implementation using regex patterns |
| `SQLInjectionRule` | Detects SQL injection via string formatting in queries (rule ID: `SQL001`) |
| `HardcodedSecretRule` | Detects hardcoded passwords/keys/tokens (rule ID: `SEC001`) |
| `CommandInjectionRule` | Detects `os.system`/`subprocess` with string concatenation (rule ID: `CMD001`) |
| `InsecureRandomRule` | Detects `random.random()`/`randint()`/`choice()` usage (rule ID: `RND001`) |

## Enums

### Severity
`CRITICAL` | `HIGH` | `MEDIUM` | `LOW` | `INFO`

### FindingType
`SQL_INJECTION` | `XSS` | `PATH_TRAVERSAL` | `COMMAND_INJECTION` | `HARDCODED_SECRET` | `INSECURE_RANDOM` | `WEAK_CRYPTO` | `EXPOSED_DEBUG` | `INSECURE_DESERIALIZATION` | `OPEN_REDIRECT`

## Usage

```python
from codomyrmex.security.scanning import SecurityScanner, PatternRule, FindingType, Severity

# Basic scanning
scanner = SecurityScanner()
result = scanner.scan_file("app.py")
print(f"Found {result.finding_count} issues ({result.critical_count} critical)")

# Directory scanning
result = scanner.scan_directory("src/", extensions=[".py"], exclude_dirs=["venv"])

# Custom rule
custom_rule = PatternRule(
    rule_id="CUSTOM001",
    finding_type=FindingType.EXPOSED_DEBUG,
    pattern=r"DEBUG\s*=\s*True",
    severity=Severity.MEDIUM,
    title="Debug Mode Enabled",
    description="Debug mode should be disabled in production",
    remediation="Set DEBUG = False",
)
scanner.add_rule(custom_rule)
```

## Thread Safety

`SecurityScanner` uses `threading.Lock` for scan ID generation, making it safe for concurrent use.

## Dependencies

No external dependencies. Uses only Python standard library (`re`, `json`, `threading`, `pathlib`, `dataclasses`, `enum`, `abc`).

## Tests

[`src/codomyrmex/tests/unit/security/scanning/test_scanning.py`](../../../../src/codomyrmex/tests/unit/security/scanning/test_scanning.py)

## Navigation

- **Parent**: [Security Module](../README.md)
- **Source**: [`src/codomyrmex/security/scanning/`](../../../../src/codomyrmex/security/scanning/)

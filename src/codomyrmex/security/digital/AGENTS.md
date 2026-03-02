# Codomyrmex Agents — src/codomyrmex/security/digital

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose

Digital security scanning covering AST-based code analysis, dependency vulnerability scanning (via pip-audit and bandit), and OWASP compliance checking. Provides both pattern-matching and AST-visiting analyzers with comprehensive reporting.

## Key Components

| File | Class / Function | Role |
|------|-----------------|------|
| `security_analyzer.py` | `SecurityIssue` | Enum of 10 issue types: `SQL_INJECTION`, `XSS_VULNERABILITY`, `COMMAND_INJECTION`, `PATH_TRAVERSAL`, `INSECURE_RANDOM`, `HARD_CODED_SECRET`, `WEAK_CRYPTO`, `INSECURE_DESERIALIZATION`, `LOGGING_SENSITIVE_DATA`, `MISSING_INPUT_VALIDATION` |
| `security_analyzer.py` | `SecurityFinding` | Dataclass with `issue_type`, `severity`, `confidence`, `file_path`, `line_number`, `code_snippet`, `recommendation`, optional `cwe_id` |
| `security_analyzer.py` | `SecurityAnalyzer` | Dual-mode analyzer: regex pattern matching (`_analyze_patterns`) + Python AST analysis (`_analyze_ast`); `analyze_file()`, `analyze_directory()` |
| `security_analyzer.py` | `ASTSecurityAnalyzer` | AST `NodeVisitor` detecting `eval()` and `exec()` calls as CRITICAL command injection |
| `vulnerability_scanner.py` | `VulnerabilityScanner` | Full scanner: `scan_vulnerabilities()` orchestrates dependency, code, and compliance scans |
| `vulnerability_scanner.py` | `VulnerabilityReport` | Dataclass with `risk_score`, `vulnerabilities`, `compliance_checks`, `.valid` property (completed and score < 70) |
| `vulnerability_scanner.py` | `SecurityScanResult` | Scan result with `component`, `scan_type`, `findings`, `.valid` alias for `.passed` |
| `vulnerability_scanner.py` | `scan_vulnerabilities()` | Convenience function wrapping `VulnerabilityScanner` |
| `vulnerability_scanner.py` | `audit_code_security()` | Code-only scan returning vulnerability list |
| `vulnerability_scanner.py` | `check_compliance()` | Compliance-only check with configurable standards |

## Operating Contracts

- `VulnerabilityScanner` shells out to `pip-audit` and `bandit` with 120-second timeouts; missing tools emit warnings and return empty results.
- `_scan_nodejs_dependencies()` raises `NotImplementedError` (zero-mock policy: no fake data).
- Risk score calculation: `min(100.0, sum(severity_weights) * 10)` with weights CRITICAL=1.0, HIGH=0.8, MEDIUM=0.6, LOW=0.3, INFO=0.1.
- `SecurityAnalyzer` supports 6 file extensions: `.py`, `.js`, `.ts`, `.java`, `.cpp`, `.rb`.
- Errors must be logged via `logging_monitoring` before re-raising.

## Integration Points

- **Depends on**: `codomyrmex.logging_monitoring.core.logger_config`
- **External tools**: `pip-audit` (Python CVE scan), `bandit` (Python SAST)
- **Used by**: CI/CD security gates, `security` parent module MCP tools (`scan_vulnerabilities`, `audit_code_security`)

## Navigation

- **Parent**: [security](../README.md)
- **Root**: [Root](../../../../README.md)

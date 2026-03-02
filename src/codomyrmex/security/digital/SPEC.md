# Digital Security -- Technical Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Orchestrates digital security scanning across codebases and dependencies. Combines AST-based code analysis (`SecurityAnalyzer`) with dependency CVE scanning and OWASP compliance checking (`VulnerabilityScanner`).

## Architecture

Dual-analyzer pattern: `SecurityAnalyzer` performs static analysis using regex patterns and Python AST visiting, while `VulnerabilityScanner` orchestrates external tools (pip-audit, bandit) and compliance checks into unified `VulnerabilityReport` objects.

## Key Classes

### `SecurityAnalyzer`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `analyze_file` | `filepath: str` | `list[SecurityFinding]` | Analyze a single file using pattern matching + AST (for `.py` files) |
| `analyze_directory` | `directory: str, recursive: bool = True` | `list[SecurityFinding]` | Scan all supported files (`.py`, `.js`, `.ts`, `.java`, `.cpp`, `.rb`) |

### `ASTSecurityAnalyzer`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `visit_Call` | `node: ast.Call` | `None` | Detect `eval()` and `exec()` calls as CRITICAL findings |

### `VulnerabilityScanner`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `scan_vulnerabilities` | `target_path: str, scan_types: list[str] \| None` | `VulnerabilityReport` | Run dependency, code, and/or compliance scans |
| `_scan_python_dependencies` | `target_path: str` | `list[dict]` | Shell out to `pip-audit` with 120s timeout |
| `_scan_code_security` | `target_path: str` | `list[dict]` | Shell out to `bandit` with 120s timeout |
| `_check_owasp_compliance` | `target_path: str` | `list[dict]` | Check OWASP Top 10 requirements |
| `_calculate_risk_score` | `vulnerabilities: list[dict]` | `float` | Weighted score: CRITICAL=1.0, HIGH=0.8, MEDIUM=0.6, LOW=0.3, INFO=0.1 |

### `VulnerabilityReport`

| Property | Returns | Description |
|----------|---------|-------------|
| `valid` | `bool` | `True` when `scan_status == "completed"` and `risk_score < 70.0` |

## Dependencies

- **Internal**: `codomyrmex.logging_monitoring.core.logger_config`
- **External tools** (optional): `pip-audit`, `bandit` -- missing tools emit warnings and skip

## Constraints

- `_scan_nodejs_dependencies()` raises `NotImplementedError` (zero-mock policy).
- External tool calls use 120-second subprocess timeouts.
- Pattern-based detection produces false positives; no data-flow analysis.
- `_check_owasp_compliance()` returns `not_checked` status (manual review required).
- Risk score capped at 100.0 via `min()`.

## Error Handling

- `SecurityAnalyzer.analyze_file()` catches all exceptions and returns empty list (logged as error).
- `ASTSecurityAnalyzer` AST parse failures are caught and logged as warnings.
- `VulnerabilityScanner.scan_vulnerabilities()` catches top-level exceptions and sets `scan_status = "failed"`.
- `subprocess.TimeoutExpired`, `json.JSONDecodeError`, and `OSError` are individually handled in tool invocations.
- All errors logged before propagation.

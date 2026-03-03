# Specification: config_audits

## Purpose

Automated auditing of configuration files for compliance, security, and correctness.

## Functional Requirements

1. **Rule-Based Auditing**: Support extensible rules for checking configuration files.
2. **File System Awareness**: Audit file permissions and ownership.
3. **Content Inspection**: Scan configuration values for sensitive data patterns.
4. **Batch Processing**: Support auditing entire directories of configuration files.
5. **Reporting**: Generate detailed reports with severity levels and recommendations.

## Interface Contracts

### MCP Tools

- `config_audit_file(file_path: str) -> str`: Audits a single configuration file via MCP.
- `config_audit_directory(directory_path: str, pattern: str) -> str`: Audits a directory via MCP.

### `ConfigAuditor`

- `audit_file(file_path: str) -> AuditResult`: Audits a single file.
- `audit_directory(directory_path: str, pattern: str) -> list[AuditResult]`: Audits all matching files in a directory.
- `generate_report(results: list[AuditResult]) -> str`: Formats results into a human-readable report.

### `AuditRule`

- `check_func(content: Any, file_path: str | None) -> list[AuditIssue]`: The logic that performs the check.

## Severity Levels

- **CRITICAL**: Immediate action required (e.g., syntax errors, cleartext production secrets).
- **HIGH**: Serious security or operational risk (e.g., debug mode in prod).
- **MEDIUM**: Best practice violation (e.g., overly permissive permissions).
- **LOW**: Minor improvement suggested.

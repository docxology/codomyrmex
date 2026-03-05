"""MCP tool definitions for the config_audits module.

Exposes configuration file auditing for security, compliance, and best practices.
"""

from __future__ import annotations

from typing import Any

from codomyrmex.model_context_protocol.decorators import mcp_tool


def _get_auditor():
    """Lazy import of ConfigAuditor to avoid circular deps."""
    from codomyrmex.config_audits.auditor import ConfigAuditor

    return ConfigAuditor


@mcp_tool(
    category="config_audits",
    description="Audit a configuration file for security issues, secrets, and compliance violations.",
)
def config_audits_audit_file(
    file_path: str,
) -> dict[str, Any]:
    """Audit a single configuration file against default rules.

    Args:
        file_path: Path to the configuration file to audit.

    Returns:
        dict with status, audit_id, is_compliant, issue_count, and issues list.
    """
    try:
        ConfigAuditor = _get_auditor()
        auditor = ConfigAuditor()
        result = auditor.audit_file(file_path)

        issues = [
            {
                "rule_id": issue.rule_id,
                "message": issue.message,
                "severity": issue.severity.value,
                "file_path": issue.file_path,
                "recommendation": issue.recommendation,
            }
            for issue in result.issues
        ]

        return {
            "status": "success",
            "audit_id": result.audit_id,
            "is_compliant": result.is_compliant,
            "issue_count": len(issues),
            "issues": issues,
            "summary": result.summary,
        }
    except Exception as exc:
        return {"status": "error", "message": str(exc)}


@mcp_tool(
    category="config_audits",
    description="Audit all configuration files in a directory for security and compliance.",
)
def config_audits_audit_directory(
    directory_path: str,
    pattern: str = "*.json",
) -> dict[str, Any]:
    """Audit all configuration files matching a pattern in a directory.

    Args:
        directory_path: Path to the directory containing config files.
        pattern: Glob pattern for matching files (default '*.json').

    Returns:
        dict with status, files_audited count, total_issues, and per-file results.
    """
    try:
        ConfigAuditor = _get_auditor()
        auditor = ConfigAuditor()
        results = auditor.audit_directory(directory_path, pattern=pattern)

        file_results = []
        total_issues = 0
        for result in results:
            issue_count = len(result.issues)
            total_issues += issue_count
            file_results.append(
                {
                    "audit_id": result.audit_id,
                    "summary": result.summary,
                    "is_compliant": result.is_compliant,
                    "issue_count": issue_count,
                }
            )

        return {
            "status": "success",
            "files_audited": len(results),
            "total_issues": total_issues,
            "results": file_results,
        }
    except Exception as exc:
        return {"status": "error", "message": str(exc)}


@mcp_tool(
    category="config_audits",
    description="Generate a human-readable audit report from directory scan results.",
)
def config_audits_generate_report(
    directory_path: str,
    pattern: str = "*.json",
) -> dict[str, Any]:
    """Audit a directory and generate a formatted compliance report.

    Args:
        directory_path: Path to the directory containing config files.
        pattern: Glob pattern for matching files (default '*.json').

    Returns:
        dict with status and the formatted report string.
    """
    try:
        ConfigAuditor = _get_auditor()
        auditor = ConfigAuditor()
        results = auditor.audit_directory(directory_path, pattern=pattern)
        report = auditor.generate_report(results)

        return {
            "status": "success",
            "report": report,
        }
    except Exception as exc:
        return {"status": "error", "message": str(exc)}

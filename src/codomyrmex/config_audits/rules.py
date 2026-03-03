import json
from pathlib import Path
from typing import Any

from .models import AuditIssue, AuditRule, Severity


def check_secrets(content: Any, file_path: str | None) -> list[AuditIssue]:
    """Check for potential secrets in configuration content.

    Args:
        content: The configuration file content to inspect.
        file_path: The optional path to the file.

    Returns:
        A list of AuditIssue objects representing any found secrets.
    """
    import re
    issues = []
    if not isinstance(content, str):
        content_str = str(content)
    else:
        content_str = content

    sensitive_patterns = [
        (r'password\s*[:=]\s*["\'][^"\']+["\']', "Potential password found in plain text"),
        (r'api_key\s*[:=]\s*["\'][^"\']+["\']', "Potential API key found in plain text"),
        (r'secret\s*[:=]\s*["\'][^"\']+["\']', "Potential secret found in plain text"),
        (r'token\s*[:=]\s*["\'][^"\']+["\']', "Potential token found in plain text"),
    ]

    for pattern, message in sensitive_patterns:
        if re.search(pattern, content_str, re.IGNORECASE):
            issues.append(AuditIssue(
                rule_id="SEC001",
                message=message,
                severity=Severity.HIGH,
                file_path=file_path,
                recommendation="Use a secret manager or environment variables for sensitive data."
            ))

    return issues


def check_permissions(content: Any, file_path: str | None) -> list[AuditIssue]:
    """Check file permissions for configuration files.

    Args:
        content: The configuration file content.
        file_path: The optional path to the file to stat.

    Returns:
        A list of AuditIssue objects representing permissive permissions.
    """
    issues = []
    if not file_path:
        return issues

    path = Path(file_path)
    if not path.exists():
        return issues

    mode = path.stat().st_mode
    if mode & 0o004:  # World readable
        issues.append(AuditIssue(
            rule_id="SEC002",
            message=f"File {file_path} has overly permissive world permissions: {oct(mode)}",
            severity=Severity.MEDIUM,
            file_path=file_path,
            recommendation="Restrict file permissions to owner or group only (e.g., 600 or 640)."
        ))

    return issues


def check_json_syntax(content: Any, file_path: str | None) -> list[AuditIssue]:
    """Check if the content is valid JSON (if it's supposed to be).

    Args:
        content: The configuration file content to parse.
        file_path: The optional path to the file, used to check for a .json extension.

    Returns:
        A list of AuditIssue objects representing JSON syntax errors.
    """
    issues = []
    if not file_path or not file_path.endswith(".json"):
        return issues

    try:
        json.loads(content)
    except json.JSONDecodeError as e:
        issues.append(AuditIssue(
            rule_id="SYN001",
            message=f"Invalid JSON syntax: {e}",
            severity=Severity.CRITICAL,
            file_path=file_path,
            recommendation="Fix the JSON syntax error."
        ))

    return issues


def check_debug_enabled(content: Any, file_path: str | None) -> list[AuditIssue]:
    """Check if debug mode is enabled in production configuration.

    Args:
        content: The configuration file content to inspect.
        file_path: The optional path to the file, used to determine if it is a production config.

    Returns:
        A list of AuditIssue objects representing the presence of debug mode.
    """
    issues = []
    if not file_path or "prod" not in file_path.lower():
        return issues

    content_str = str(content).lower()
    if '"debug": true' in content_str or 'debug: true' in content_str:
        issues.append(AuditIssue(
            rule_id="OPS001",
            message="Debug mode enabled in production configuration",
            severity=Severity.HIGH,
            file_path=file_path,
            recommendation="Set debug to false for production environments."
        ))

    return issues


DEFAULT_RULES = [
    AuditRule(
        rule_id="SEC001",
        description="Check for hardcoded secrets",
        severity=Severity.HIGH,
        check_func=check_secrets
    ),
    AuditRule(
        rule_id="SEC002",
        description="Check file permissions",
        severity=Severity.MEDIUM,
        check_func=check_permissions
    ),
    AuditRule(
        rule_id="SYN001",
        description="Check JSON syntax",
        severity=Severity.CRITICAL,
        check_func=check_json_syntax
    ),
    AuditRule(
        rule_id="OPS001",
        description="Check for debug mode in production",
        severity=Severity.HIGH,
        check_func=check_debug_enabled
    ),
]

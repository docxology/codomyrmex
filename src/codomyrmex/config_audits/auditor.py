import uuid
from datetime import datetime
from pathlib import Path

from codomyrmex.logging_monitoring import get_logger

from .models import AuditIssue, AuditResult, AuditRule, Severity
from .rules import DEFAULT_RULES

logger = get_logger(__name__)


class ConfigAuditor:
    """Orchestrates the auditing of configuration files."""

    def __init__(self, rules: list[AuditRule] | None = None):
        """Initialize the auditor with a set of rules.

        Args:
            rules: List of AuditRule objects. If None, uses DEFAULT_RULES.
        """
        self.rules = rules if rules is not None else DEFAULT_RULES

    def audit_file(self, file_path: str | Path) -> AuditResult:
        """Audit a single configuration file.

        Args:
            file_path: Path to the configuration file.

        Returns:
            AuditResult containing any issues found.
        """
        path = Path(file_path)
        issues = []

        if not path.exists():
            return AuditResult(
                audit_id=str(uuid.uuid4()),
                success=False,
                summary=f"File not found: {file_path}",
                issues=[AuditIssue(
                    rule_id="SYS001",
                    message=f"Configuration file missing: {file_path}",
                    severity=Severity.HIGH,
                    file_path=str(file_path)
                )]
            )

        try:
            content = path.read_text()
        except Exception as e:
            return AuditResult(
                audit_id=str(uuid.uuid4()),
                success=False,
                summary=f"Error reading file: {e}",
                issues=[AuditIssue(
                    rule_id="SYS002",
                    message=f"Failed to read file {file_path}: {e}",
                    severity=Severity.HIGH,
                    file_path=str(file_path)
                )]
            )

        for rule in self.rules:
            try:
                rule_issues = rule.check_func(content, str(path))
                issues.extend(rule_issues)
            except Exception as e:
                logger.error(f"Error applying rule {rule.rule_id}: {e}")
                issues.append(AuditIssue(
                    rule_id="SYS003",
                    message=f"Error applying rule {rule.rule_id}: {e}",
                    severity=Severity.MEDIUM,
                    file_path=str(path)
                ))

        return AuditResult(
            audit_id=str(uuid.uuid4()),
            issues=issues,
            success=True,
            summary=f"Audited {file_path}. Found {len(issues)} issues."
        )

    def audit_directory(self, directory_path: str | Path, pattern: str = "*.json") -> list[AuditResult]:
        """Audit all configuration files in a directory.

        Args:
            directory_path: Path to the directory.
            pattern: Glob pattern to match configuration files.

        Returns:
            List of AuditResult objects.
        """
        path = Path(directory_path)
        results = []

        if not path.is_dir():
            logger.error(f"Not a directory: {directory_path}")
            return results

        # Support common config extensions if pattern is default
        patterns = [pattern] if pattern != "*.json" else ["*.json", "*.yaml", "*.yml"]

        found_files = []
        for p in patterns:
            found_files.extend(path.glob(p))

        for file_path in sorted(set(found_files)):
            results.append(self.audit_file(file_path))

        return results

    def generate_report(self, results: list[AuditResult]) -> str:
        """Generate a human-readable summary report of audit results.

        Args:
            results: List of AuditResult objects.

        Returns:
            Formatted report string.
        """
        if not results:
            return "No audit results to report."

        total_issues = sum(len(r.issues) for r in results)
        critical_issues = sum(
            1 for r in results for i in r.issues if i.severity == Severity.CRITICAL
        )
        high_issues = sum(
            1 for r in results for i in r.issues if i.severity == Severity.HIGH
        )

        report = [
            "=== Configuration Audit Report ===",
            f"Timestamp: {datetime.now().isoformat()}",
            f"Files Audited: {len(results)}",
            f"Total Issues Found: {total_issues}",
            f"  Critical: {critical_issues}",
            f"  High: {high_issues}",
            "",
        ]

        for result in results:
            status = "PASS" if result.is_compliant else "FAIL"
            report.append(f"File: {result.summary.split(' ')[1]} [{status}]")
            for issue in result.issues:
                report.append(f"  - [{issue.severity.value.upper()}] {issue.rule_id}: {issue.message}")
                if issue.recommendation:
                    report.append(f"    Recommendation: {issue.recommendation}")
            report.append("")

        return "\n".join(report)

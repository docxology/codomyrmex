"""
Health Reporter for Codomyrmex System Discovery

This module provides comprehensive health reporting capabilities,
generating detailed reports on system and module health status.
"""

import json
import time
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from pathlib import Path

# Import logging
try:
    from codomyrmex.logging_monitoring.logger_config import get_logger
    logger = get_logger(__name__)
except ImportError:
    import logging
    logger = logging.getLogger(__name__)

# Import health checker
try:
    from .health_checker import HealthChecker, HealthStatus, HealthCheckResult, perform_health_check
except ImportError:
    HealthChecker = None
    HealthStatus = None
    HealthCheckResult = None
    perform_health_check = None


@dataclass
class HealthReport:
    """Comprehensive health report for the system."""

    timestamp: float = field(default_factory=time.time)
    duration_seconds: float = 0.0
    total_modules: int = 0
    healthy_modules: int = 0
    degraded_modules: int = 0
    unhealthy_modules: int = 0
    unknown_modules: int = 0
    module_results: Dict[str, HealthCheckResult] = field(default_factory=dict)
    system_metrics: Dict[str, Any] = field(default_factory=dict)
    recommendations: List[str] = field(default_factory=list)
    critical_issues: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "timestamp": self.timestamp,
            "duration_seconds": self.duration_seconds,
            "total_modules": self.total_modules,
            "healthy_modules": self.healthy_modules,
            "degraded_modules": self.degraded_modules,
            "unhealthy_modules": self.unhealthy_modules,
            "unknown_modules": self.unknown_modules,
            "module_results": {name: result.to_dict() for name, result in self.module_results.items()},
            "system_metrics": self.system_metrics,
            "recommendations": self.recommendations,
            "critical_issues": self.critical_issues,
            "summary": self._generate_summary()
        }

    def _generate_summary(self) -> Dict[str, Any]:
        """Generate a summary of the health report."""
        health_score = 0.0
        if self.total_modules > 0:
            health_score = (
                (self.healthy_modules * 1.0 +
                 self.degraded_modules * 0.5) / self.total_modules
            ) * 100

        overall_status = "unknown"
        if self.unhealthy_modules > 0:
            overall_status = "critical"
        elif self.degraded_modules > 0:
            overall_status = "warning"
        elif self.healthy_modules == self.total_modules:
            overall_status = "healthy"

        return {
            "health_score_percentage": round(health_score, 1),
            "overall_status": overall_status,
            "modules_checked": self.total_modules,
            "issues_count": len(self.critical_issues) + sum(
                len(result.issues) for result in self.module_results.values()
            )
        }


class HealthReporter:
    """
    Comprehensive health reporting system for Codomyrmex.

    Generates detailed health reports, provides recommendations,
    and tracks health trends over time.
    """

    def __init__(self):
        """Initialize the health reporter."""
        self.checker = HealthChecker() if HealthChecker else None

    def generate_health_report(self, modules: List[str], include_system_metrics: bool = True) -> HealthReport:
        """
        Generate a comprehensive health report for specified modules.

        Args:
            modules: List of module names to check
            include_system_metrics: Whether to include system-wide metrics

        Returns:
            HealthReport with detailed health information
        """
        if not self.checker:
            logger.error("HealthChecker not available")
            return self._create_empty_report()

        start_time = time.time()
        report = HealthReport()
        report.total_modules = len(modules)

        logger.info(f"Starting health check for {len(modules)} modules")

        # Perform health checks for each module
        for module_name in modules:
            try:
                result = self.checker.perform_health_check(module_name)
                report.module_results[module_name] = result

                # Update counters
                if result.status == HealthStatus.HEALTHY:
                    report.healthy_modules += 1
                elif result.status == HealthStatus.DEGRADED:
                    report.degraded_modules += 1
                elif result.status == HealthStatus.UNHEALTHY:
                    report.unhealthy_modules += 1
                    report.critical_issues.extend(result.issues)
                else:  # UNKNOWN
                    report.unknown_modules += 1

                # Collect recommendations
                report.recommendations.extend(result.recommendations)

            except Exception as e:
                logger.error(f"Failed to check module {module_name}: {e}")
                # Create a failed result
                failed_result = HealthCheckResult(
                    module_name=module_name,
                    status=HealthStatus.UNKNOWN
                )
                failed_result.add_issue(f"Health check failed: {str(e)}")
                report.module_results[module_name] = failed_result
                report.unknown_modules += 1

        # Collect system metrics if requested
        if include_system_metrics:
            try:
                from codomyrmex.performance.performance_monitor import get_system_metrics
                report.system_metrics = get_system_metrics()
            except Exception as e:
                logger.warning(f"Failed to collect system metrics: {e}")
                report.system_metrics = {"error": str(e)}

        # Calculate duration
        report.duration_seconds = time.time() - start_time

        # Generate additional recommendations based on overall health
        self._generate_overall_recommendations(report)

        logger.info(f"Health check completed in {report.duration_seconds:.2f}s")
        return report

    def _create_empty_report(self) -> HealthReport:
        """Create an empty report for error cases."""
        report = HealthReport()
        report.critical_issues.append("HealthChecker not available")
        report.recommendations.append("Install required dependencies for health checking")
        return report

    def _generate_overall_recommendations(self, report: HealthReport) -> None:
        """Generate overall recommendations based on health report."""
        # Check for common issues
        if report.unhealthy_modules > 0:
            report.recommendations.append(
                f"Address critical issues in {report.unhealthy_modules} unhealthy modules"
            )

        if report.unknown_modules > 0:
            report.recommendations.append(
                f"Investigate {report.unknown_modules} modules with unknown status"
            )

        # Check system metrics
        if report.system_metrics:
            cpu_percent = report.system_metrics.get("cpu_percent", 0)
            memory_percent = report.system_metrics.get("memory_percent", 0)

            if cpu_percent > 80:
                report.recommendations.append("High CPU usage detected - consider resource optimization")
            if memory_percent > 80:
                report.recommendations.append("High memory usage detected - check for memory leaks")

        # Module-specific recommendations
        for module_name, result in report.module_results.items():
            if result.status == HealthStatus.UNHEALTHY:
                report.recommendations.append(
                    f"Fix critical issues in {module_name} module"
                )
            elif result.status == HealthStatus.DEGRADED:
                report.recommendations.append(
                    f"Address performance issues in {module_name} module"
                )

    def format_health_report(self, report: HealthReport, format: str = "text") -> str:
        """
        Format a health report for display.

        Args:
            report: HealthReport to format
            format: Output format ("text", "json", "markdown")

        Returns:
            Formatted report string
        """
        if format == "json":
            return json.dumps(report.to_dict(), indent=2)

        elif format == "markdown":
            return self._format_markdown_report(report)

        else:  # text format
            return self._format_text_report(report)

    def _format_text_report(self, report: HealthReport) -> str:
        """Format report as plain text."""
        lines = []

        # Header
        lines.append("=" * 60)
        lines.append("Codomyrmex Health Report")
        lines.append("=" * 60)
        lines.append("")

        # Summary
        summary = report._generate_summary()
        lines.append(f"Generated: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(report.timestamp))}")
        lines.append(f"Duration: {report.duration_seconds:.2f}s")
        lines.append("")
        lines.append(f"Overall Status: {summary['overall_status'].upper()}")
        lines.append(f"Health Score: {summary['health_score_percentage']}%")
        lines.append("")

        # Module counts
        lines.append("Module Status Summary:")
        lines.append(f"  Total Modules: {report.total_modules}")
        lines.append(f"  Healthy: {report.healthy_modules}")
        lines.append(f"  Degraded: {report.degraded_modules}")
        lines.append(f"  Unhealthy: {report.unhealthy_modules}")
        lines.append(f"  Unknown: {report.unknown_modules}")
        lines.append("")

        # Critical issues
        if report.critical_issues:
            lines.append("Critical Issues:")
            for issue in report.critical_issues:
                lines.append(f"  - {issue}")
            lines.append("")

        # Recommendations
        if report.recommendations:
            lines.append("Recommendations:")
            for rec in report.recommendations:
                lines.append(f"  - {rec}")
            lines.append("")

        # System metrics
        if report.system_metrics:
            lines.append("System Metrics:")
            for key, value in report.system_metrics.items():
                if isinstance(value, float):
                    lines.append(f"  {key}: {value:.1f}")
                else:
                    lines.append(f"  {key}: {value}")
            lines.append("")

        return "\n".join(lines)

    def _format_markdown_report(self, report: HealthReport) -> str:
        """Format report as Markdown."""
        lines = []

        # Header
        lines.append("# Codomyrmex Health Report")
        lines.append("")

        summary = report._generate_summary()
        lines.append(f"**Generated:** {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(report.timestamp))}")
        lines.append(f"**Duration:** {report.duration_seconds:.2f}s")
        lines.append(f"**Overall Status:** {summary['overall_status'].upper()}")
        lines.append(f"**Health Score:** {summary['health_score_percentage']}%")
        lines.append("")

        # Module counts
        lines.append("## Module Status Summary")
        lines.append("")
        lines.append(f"- **Total Modules:** {report.total_modules}")
        lines.append(f"- **Healthy:** {report.healthy_modules}")
        lines.append(f"- **Degraded:** {report.degraded_modules}")
        lines.append(f"- **Unhealthy:** {report.unhealthy_modules}")
        lines.append(f"- **Unknown:** {report.unknown_modules}")
        lines.append("")

        # Critical issues
        if report.critical_issues:
            lines.append("## Critical Issues")
            lines.append("")
            for issue in report.critical_issues:
                lines.append(f"- {issue}")
            lines.append("")

        # Recommendations
        if report.recommendations:
            lines.append("## Recommendations")
            lines.append("")
            for rec in report.recommendations:
                lines.append(f"- {rec}")
            lines.append("")

        # Module details
        if report.module_results:
            lines.append("## Module Details")
            lines.append("")
            for module_name, result in report.module_results.items():
                lines.append(f"### {module_name}")
                lines.append(f"- **Status:** {result.status.value.upper()}")
                if result.issues:
                    lines.append("- **Issues:**")
                    for issue in result.issues:
                        lines.append(f"  - {issue}")
                if result.recommendations:
                    lines.append("- **Recommendations:**")
                    for rec in result.recommendations:
                        lines.append(f"  - {rec}")
                lines.append("")

        return "\n".join(lines)

    def export_health_report(self, report: HealthReport, filepath: str, format: Optional[str] = None) -> None:
        """
        Export a health report to a file.

        Args:
            filepath: Path to export the report
            format: Export format (inferred from extension if None)
        """
        if format is None:
            if filepath.endswith('.json'):
                format = 'json'
            elif filepath.endswith('.md'):
                format = 'markdown'
            else:
                format = 'text'

        formatted_report = self.format_health_report(report, format)

        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(formatted_report)

            logger.info(f"Health report exported to {filepath}")

        except Exception as e:
            logger.error(f"Failed to export health report to {filepath}: {e}")
            raise

    def compare_health_reports(self, current: HealthReport, previous: HealthReport) -> Dict[str, Any]:
        """
        Compare two health reports to identify changes.

        Args:
            current: Current health report
            previous: Previous health report for comparison

        Returns:
            Dictionary with comparison results
        """
        comparison = {
            "timestamp_current": current.timestamp,
            "timestamp_previous": previous.timestamp,
            "time_difference_seconds": current.timestamp - previous.timestamp,
            "health_score_change": 0.0,
            "status_changes": {},
            "new_issues": [],
            "resolved_issues": [],
            "new_modules": [],
            "removed_modules": []
        }

        # Calculate health score change
        current_summary = current._generate_summary()
        previous_summary = previous._generate_summary()
        comparison["health_score_change"] = (
            current_summary["health_score_percentage"] - previous_summary["health_score_percentage"]
        )

        # Compare module statuses
        current_modules = set(current.module_results.keys())
        previous_modules = set(previous.module_results.keys())

        new_modules = current_modules - previous_modules
        removed_modules = previous_modules - current_modules
        common_modules = current_modules & previous_modules

        comparison["new_modules"] = list(new_modules)
        comparison["removed_modules"] = list(removed_modules)

        # Check status changes for common modules
        for module in common_modules:
            current_status = current.module_results[module].status
            previous_status = previous.module_results[module].status

            if current_status != previous_status:
                comparison["status_changes"][module] = {
                    "from": previous_status.value,
                    "to": current_status.value
                }

        # Compare issues
        current_issues = set()
        for result in current.module_results.values():
            current_issues.update(result.issues)

        previous_issues = set()
        for result in previous.module_results.values():
            previous_issues.update(result.issues)

        comparison["new_issues"] = list(current_issues - previous_issues)
        comparison["resolved_issues"] = list(previous_issues - current_issues)

        return comparison


def generate_health_report(modules: List[str]) -> HealthReport:
    """
    Convenience function to generate a health report.

    Args:
        modules: List of module names to check

    Returns:
        HealthReport with comprehensive health information
    """
    reporter = HealthReporter()
    return reporter.generate_health_report(modules)


def format_health_report(report: HealthReport, format: str = "text") -> str:
    """
    Convenience function to format a health report.

    Args:
        report: HealthReport to format
        format: Output format ("text", "json", "markdown")

    Returns:
        Formatted report string
    """
    reporter = HealthReporter()
    return reporter.format_health_report(report, format)


def export_health_report(report: HealthReport, filepath: str) -> None:
    """
    Convenience function to export a health report.

    Args:
        report: HealthReport to export
        filepath: Path to export the report
    """
    reporter = HealthReporter()
    reporter.export_health_report(report, filepath)

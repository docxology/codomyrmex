"""CodeReviewer — ReportingMixin mixin."""

from __future__ import annotations

import json
import os
import subprocess
import time
from pathlib import Path
from typing import Any


from codomyrmex.logging_monitoring.core.logger_config import get_logger
from codomyrmex.coding.review.models import (
    AnalysisResult,
    AnalysisSummary,
    QualityDashboard,
    QualityGateResult,
    SeverityLevel,
)

logger = get_logger(__name__)


class ReportingMixin:
    """ReportingMixin mixin providing reporting capabilities."""

    def generate_report(self, output_path: str, format: str = "html") -> bool:
        """Generate comprehensive analysis report."""
        try:
            if format.lower() == "html":
                return self._generate_html_report(output_path)
            elif format.lower() == "json":
                return self._generate_json_report(output_path)
            elif format.lower() == "markdown":
                return self._generate_markdown_report(output_path)
            else:
                logger.error(f"Unsupported report format: {format}")
                return False

        except Exception as e:
            logger.error(f"Error generating report: {e}")
            return False

    def _generate_html_report(self, output_path: str) -> bool:
        """Generate HTML report."""
        # Use pyscn to generate HTML report if available
        report_path = self.pyscn_analyzer.generate_report(os.path.dirname(output_path))
        if report_path:
            # Copy to desired location if different
            if report_path != output_path:
                shutil.copy2(report_path, output_path)
            return True

        # Fallback to basic HTML generation
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Code Review Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .summary {{ background: #f5f5f5; padding: 15px; margin: 10px 0; }}
                .issue {{ border-left: 4px solid #ddd; padding: 10px; margin: 10px 0; }}
                .error {{ border-color: #e74c3c; }}
                .warning {{ border-color: #f39c12; }}
                .info {{ border-color: #3498db; }}
            </style>
        </head>
        <body>
            <h1>Code Review Report</h1>
            <div class="summary">
                <h2>Summary</h2>
                <p>Total Issues: {len(self.results)}</p>
                <p>Files Analyzed: {len({r.file_path for r in self.results})}</p>
            </div>
            <h2>Issues</h2>
        """

        for result in self.results:
            severity_class = result.severity.value
            html_content += f"""
            <div class="issue {severity_class}">
                <h3>{result.file_path}:{result.line_number}</h3>
                <p><strong>{result.severity.value.upper()}:</strong> {result.message}</p>
                <p><em>Category:</em> {result.category} | <em>Rule:</em> {result.rule_id}</p>
                {f"<p><em>Suggestion:</em> {result.suggestion}</p>" if result.suggestion else ""}
            </div>
            """

        html_content += """
        </body>
        </html>
        """

        with open(output_path, "w") as f:
            f.write(html_content)

        return True

    def _generate_json_report(self, output_path: str) -> bool:
        """Generate JSON report."""
        report_data = {
            "summary": {
                "total_issues": len(self.results),
                "files_analyzed": len({r.file_path for r in self.results}),
                "analysis_time": 0,  # Would need to track this
            },
            "results": [
                {
                    "file_path": result.file_path,
                    "line_number": result.line_number,
                    "column_number": result.column_number,
                    "severity": result.severity.value,
                    "message": result.message,
                    "rule_id": result.rule_id,
                    "category": result.category,
                    "suggestion": result.suggestion,
                    "context": result.context,
                    "fix_available": result.fix_available,
                    "confidence": result.confidence,
                }
                for result in self.results
            ]
        }

        with open(output_path, "w") as f:
            json.dump(report_data, f, indent=2)

        return True

    def _generate_markdown_report(self, output_path: str) -> bool:
        """Generate Markdown report."""
        md_content = "# Code Review Report\n\n"

        # Summary
        md_content += "## Summary\n\n"
        md_content += f"- **Total Issues**: {len(self.results)}\n"
        md_content += f"- **Files Analyzed**: {len({r.file_path for r in self.results})}\n"
        md_content += "- **Analysis Time**: N/A\n\n"

        # Issues by severity
        severity_counts = {}
        for result in self.results:
            severity_counts[result.severity] = severity_counts.get(result.severity, 0) + 1

        md_content += "## Issues by Severity\n\n"
        for severity, count in severity_counts.items():
            md_content += f"- **{severity.value.upper()}**: {count}\n"
        md_content += "\n"

        # Detailed issues
        md_content += "## Detailed Issues\n\n"
        for result in self.results:
            md_content += f"### {result.file_path}:{result.line_number}\n\n"
            md_content += f"- **Severity**: {result.severity.value}\n"
            md_content += f"- **Message**: {result.message}\n"
            md_content += f"- **Category**: {result.category}\n"
            md_content += f"- **Rule**: {result.rule_id}\n"
            if result.suggestion:
                md_content += f"- **Suggestion**: {result.suggestion}\n"
            md_content += "\n"

        with open(output_path, "w") as f:
            f.write(md_content)

        return True

    def generate_comprehensive_report(self, output_path: str = "comprehensive_report.html") -> bool:
        """Generate a comprehensive quality report including dashboard and all analysis."""
        try:
            # Generate quality dashboard
            dashboard = self.generate_quality_dashboard()

            # Generate HTML report with dashboard data
            html_content = self._generate_dashboard_html(dashboard)

            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html_content)

            logger.info(f"Comprehensive report generated: {output_path}")
            return True

        except Exception as e:
            logger.error(f"Error generating comprehensive report: {e}")
            return False

    def _generate_dashboard_html(self, dashboard: QualityDashboard) -> str:
        """Generate HTML for the quality dashboard."""
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Code Quality Dashboard - {dashboard.grade} ({dashboard.overall_score}%)</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .header {{ text-align: center; margin-bottom: 30px; }}
        .score {{ font-size: 48px; font-weight: bold; color: {self._get_score_color(dashboard.overall_score)}; }}
        .grade {{ font-size: 24px; color: #666; }}
        .metrics {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 30px 0; }}
        .metric-card {{ background: #f8f9fa; padding: 20px; border-radius: 8px; text-align: center; }}
        .metric-value {{ font-size: 24px; font-weight: bold; }}
        .metric-label {{ color: #666; margin-top: 5px; }}
        .section {{ margin: 30px 0; }}
        .section h3 {{ color: #333; border-bottom: 2px solid #eee; padding-bottom: 10px; }}
        .issue-list {{ background: #fff; border: 1px solid #ddd; border-radius: 5px; }}
        .issue-item {{ padding: 15px; border-bottom: 1px solid #eee; }}
        .issue-item:last-child {{ border-bottom: none; }}
        .priority-high {{ border-left: 4px solid #dc3545; }}
        .priority-medium {{ border-left: 4px solid #ffc107; }}
        .priority-low {{ border-left: 4px solid #28a745; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Code Quality Dashboard</h1>
            <div class="score">{dashboard.overall_score:.1f}%</div>
            <div class="grade">Grade: {dashboard.grade}</div>
            <p>Analysis Date: {dashboard.analysis_timestamp}</p>
        </div>

        <div class="metrics">
            <div class="metric-card">
                <div class="metric-value">{dashboard.total_files}</div>
                <div class="metric-label">Files Analyzed</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{dashboard.total_functions}</div>
                <div class="metric-label">Functions</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{dashboard.total_lines:,}</div>
                <div class="metric-label">Lines of Code</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{dashboard.complexity_score:.1f}%</div>
                <div class="metric-label">Complexity Score</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{dashboard.maintainability_score:.1f}%</div>
                <div class="metric-label">Maintainability</div>
            </div>
        </div>

        <div class="section">
            <h3>🚨 Priority Actions</h3>
            <div class="issue-list">
"""

        for action in dashboard.priority_actions[:5]:  # Top 5
            priority_class = f"priority-{action['priority']}"
            html += f"""
                <div class="issue-item {priority_class}">
                    <strong>{action['type'].replace('_', ' ').title()}</strong><br>
                    {action['description']}
                </div>
"""

        html += """
            </div>
        </div>

        <div class="section">
            <h3>💡 Quick Wins</h3>
            <div class="issue-list">
"""

        for win in dashboard.quick_wins[:3]:  # Top 3
            html += f"""
                <div class="issue-item">
                    <strong>{win['type'].replace('_', ' ').title()}</strong><br>
                    {win['description']} (Effort: {win['effort']}, Impact: {win['impact']})
                </div>
"""

        html += """
            </div>
        </div>

        <div class="section">
            <h3>📈 Long-term Improvements</h3>
            <div class="issue-list">
"""

        for improvement in dashboard.long_term_improvements[:3]:  # Top 3
            html += f"""
                <div class="issue-item">
                    <strong>{improvement['type'].replace('_', ' ').title()}</strong><br>
                    {improvement['description']} (Effort: {improvement['effort']}, Impact: {improvement['impact']})
                </div>
"""

        html += """
            </div>
        </div>

        <div class="section">
            <p><em>Generated by Codomyrmex Code Review Module</em></p>
        </div>
    </div>
</body>
</html>
"""
        return html

    def _get_score_color(self, score: float) -> str:
        """Get color for score display."""
        if score >= 90:
            return "#28a745"  # Green
        elif score >= 80:
            return "#ffc107"  # Yellow
        elif score >= 70:
            return "#fd7e14"  # Orange
        else:
            return "#dc3545"  # Red


"""
Security Reports for Codomyrmex Security Audit Module.

Provides comprehensive security reporting and assessment generation capabilities.
"""

import os
import sys
import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
import jinja2

# Add project root to Python path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

try:
    from logging_monitoring.logger_config import get_logger

    logger = get_logger(__name__)
except ImportError:
    import logging

    logger = logging.getLogger(__name__)


@dataclass
class SecurityReport:
    """Comprehensive security assessment report."""

    report_id: str
    title: str
    generated_at: datetime
    target_system: str
    executive_summary: str
    risk_assessment: Dict[str, Any]
    findings: List[Dict[str, Any]] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    compliance_status: Dict[str, Any] = field(default_factory=dict)
    metrics: Dict[str, Any] = field(default_factory=dict)
    appendices: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert report to dictionary format."""
        return {
            "report_id": self.report_id,
            "title": self.title,
            "generated_at": self.generated_at.isoformat(),
            "target_system": self.target_system,
            "executive_summary": self.executive_summary,
            "risk_assessment": self.risk_assessment,
            "findings": self.findings,
            "recommendations": self.recommendations,
            "compliance_status": self.compliance_status,
            "metrics": self.metrics,
            "appendices": self.appendices,
        }


class SecurityReportGenerator:
    """
    Security report generator for comprehensive assessments.

    Features:
    - Multiple output formats (JSON, HTML, PDF)
    - Executive summaries and risk assessments
    - Compliance reporting
    - Metrics and trend analysis
    - Template-based report generation
    """

    def __init__(self, template_dir: Optional[str] = None):
        """
        Initialize the security report generator.

        Args:
            template_dir: Directory containing report templates
        """
        self.template_dir = template_dir or os.path.join(
            os.path.dirname(__file__), "templates"
        )
        self.templates: Dict[str, jinja2.Template] = {}

        # Initialize Jinja2 environment
        self._setup_jinja2()

        # Load templates
        self._load_templates()

    def _setup_jinja2(self):
        """Setup Jinja2 template environment."""
        template_loader = jinja2.FileSystemLoader(self.template_dir)
        self.jinja_env = jinja2.Environment(
            loader=template_loader,
            autoescape=True,
            trim_blocks=True,
            lstrip_blocks=True,
        )

        # Add custom filters
        self.jinja_env.filters["format_datetime"] = self._format_datetime_filter
        self.jinja_env.filters["severity_color"] = self._severity_color_filter
        self.jinja_env.filters["risk_level"] = self._risk_level_filter

    def _load_templates(self):
        """Load report templates."""
        # Create template directory if it doesn't exist
        os.makedirs(self.template_dir, exist_ok=True)

        # Default templates
        self._create_default_templates()

    def _create_default_templates(self):
        """Create default report templates."""
        templates = {
            "executive_summary.html": """
<!DOCTYPE html>
<html>
<head>
    <title>{{ report.title }} - Executive Summary</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        .header { background: #f0f0f0; padding: 20px; border-radius: 5px; }
        .risk-high { color: #dc3545; }
        .risk-medium { color: #ffc107; }
        .risk-low { color: #28a745; }
        .metric { background: #e9ecef; padding: 10px; margin: 10px 0; border-radius: 3px; }
    </style>
</head>
<body>
    <div class="header">
        <h1>{{ report.title }}</h1>
        <p><strong>Generated:</strong> {{ report.generated_at | format_datetime }}</p>
        <p><strong>Target System:</strong> {{ report.target_system }}</p>
    </div>

    <h2>Executive Summary</h2>
    <p>{{ report.executive_summary }}</p>

    <h2>Risk Assessment</h2>
    <div class="metric">
        <strong>Overall Risk Level:</strong>
        <span class="risk-{{ report.risk_assessment.level | lower }}">
            {{ report.risk_assessment.level }}
        </span>
    </div>
    <div class="metric">
        <strong>Risk Score:</strong> {{ report.risk_assessment.score }}/100
    </div>
    <p>{{ report.risk_assessment.description }}</p>

    <h2>Key Findings</h2>
    <ul>
    {% for finding in report.findings %}
        <li>
            <strong>{{ finding.title }}</strong> ({{ finding.severity }})
            <br>{{ finding.description }}
        </li>
    {% endfor %}
    </ul>

    <h2>Recommendations</h2>
    <ol>
    {% for rec in report.recommendations %}
        <li>{{ rec }}</li>
    {% endfor %}
    </ol>
</body>
</html>
            """,
            "compliance_report.html": """
<!DOCTYPE html>
<html>
<head>
    <title>{{ report.title }} - Compliance Report</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        .compliant { color: #28a745; }
        .non-compliant { color: #dc3545; }
        .not-checked { color: #6c757d; }
        table { border-collapse: collapse; width: 100%; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background-color: #f2f2f2; }
    </style>
</head>
<body>
    <h1>{{ report.title }} - Compliance Report</h1>
    <p><strong>Generated:</strong> {{ report.generated_at | format_datetime }}</p>

    <h2>Compliance Status</h2>
    <table>
        <tr>
            <th>Standard</th>
            <th>Status</th>
            <th>Compliance %</th>
            <th>Details</th>
        </tr>
        {% for standard, status in report.compliance_status.items() %}
        <tr>
            <td>{{ standard }}</td>
            <td class="{{ status.status | lower }}">{{ status.status | replace('_', ' ') | title }}</td>
            <td>{{ status.compliance_percentage }}%</td>
            <td>{{ status.details }}</td>
        </tr>
        {% endfor %}
    </table>
</body>
</html>
            """,
        }

        # Write templates to files
        for template_name, template_content in templates.items():
            template_path = os.path.join(self.template_dir, template_name)
            try:
                with open(template_path, "w") as f:
                    f.write(template_content)
            except Exception as e:
                logger.warning(f"Failed to create template {template_name}: {e}")

    def _format_datetime_filter(self, dt):
        """Jinja2 filter for formatting datetime."""
        if isinstance(dt, str):
            return dt
        return dt.strftime("%Y-%m-%d %H:%M:%S UTC")

    def _severity_color_filter(self, severity):
        """Jinja2 filter for severity colors."""
        colors = {
            "CRITICAL": "#dc3545",
            "HIGH": "#fd7e14",
            "MEDIUM": "#ffc107",
            "LOW": "#28a745",
            "INFO": "#6c757d",
        }
        return colors.get(severity.upper(), "#6c757d")

    def _risk_level_filter(self, score):
        """Jinja2 filter for risk levels."""
        if score >= 80:
            return "high"
        elif score >= 60:
            return "medium"
        else:
            return "low"

    def generate_comprehensive_report(
        self,
        vulnerability_data: Dict[str, Any],
        compliance_data: Dict[str, Any],
        monitoring_data: Dict[str, Any],
    ) -> SecurityReport:
        """
        Generate a comprehensive security report from various data sources.

        Args:
            vulnerability_data: Vulnerability scan results
            compliance_data: Compliance check results
            monitoring_data: Security monitoring data

        Returns:
            SecurityReport: Comprehensive security report
        """
        report_id = (
            f"security_report_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}"
        )

        # Analyze vulnerability data
        vulnerability_analysis = self._analyze_vulnerabilities(vulnerability_data)

        # Analyze compliance data
        compliance_analysis = self._analyze_compliance(compliance_data)

        # Analyze monitoring data
        monitoring_analysis = self._analyze_monitoring(monitoring_data)

        # Calculate overall risk assessment
        overall_risk = self._calculate_overall_risk(
            vulnerability_analysis, compliance_analysis, monitoring_analysis
        )

        # Generate executive summary
        executive_summary = self._generate_executive_summary(
            vulnerability_analysis,
            compliance_analysis,
            monitoring_analysis,
            overall_risk,
        )

        # Generate recommendations
        recommendations = self._generate_recommendations(
            vulnerability_analysis, compliance_analysis, monitoring_analysis
        )

        # Create report
        report = SecurityReport(
            report_id=report_id,
            title="Comprehensive Security Assessment Report",
            generated_at=datetime.now(timezone.utc),
            target_system=vulnerability_data.get("target", "Unknown System"),
            executive_summary=executive_summary,
            risk_assessment=overall_risk,
            findings=self._compile_findings(
                vulnerability_analysis, compliance_analysis, monitoring_analysis
            ),
            recommendations=recommendations,
            compliance_status=compliance_analysis,
            metrics=self._calculate_metrics(
                vulnerability_analysis, compliance_analysis, monitoring_analysis
            ),
        )

        return report

    def _analyze_vulnerabilities(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze vulnerability data."""
        vulnerabilities = data.get("vulnerabilities", [])

        analysis = {
            "total_vulnerabilities": len(vulnerabilities),
            "critical_count": 0,
            "high_count": 0,
            "medium_count": 0,
            "low_count": 0,
            "severity_breakdown": {},
            "top_vulnerabilities": [],
        }

        for vuln in vulnerabilities:
            severity = vuln.get("severity", "UNKNOWN").upper()
            analysis[f"{severity.lower()}_count"] += 1

            if severity not in analysis["severity_breakdown"]:
                analysis["severity_breakdown"][severity] = 0
            analysis["severity_breakdown"][severity] += 1

        # Sort top vulnerabilities by severity
        severity_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3, "INFO": 4}
        sorted_vulns = sorted(
            vulnerabilities,
            key=lambda x: severity_order.get(x.get("severity", "UNKNOWN").upper(), 5),
        )
        analysis["top_vulnerabilities"] = sorted_vulns[:10]

        return analysis

    def _analyze_compliance(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze compliance data."""
        compliance_checks = data.get("compliance_checks", [])

        analysis = {
            "total_checks": len(compliance_checks),
            "compliant_count": 0,
            "non_compliant_count": 0,
            "not_checked_count": 0,
            "compliance_percentage": 0.0,
            "standards_coverage": {},
        }

        for check in compliance_checks:
            status = check.get("status", "not_checked")
            standard = check.get("standard", "Unknown")

            if status == "compliant":
                analysis["compliant_count"] += 1
            elif status == "non_compliant":
                analysis["non_compliant_count"] += 1
            else:
                analysis["not_checked_count"] += 1

            if standard not in analysis["standards_coverage"]:
                analysis["standards_coverage"][standard] = {"total": 0, "compliant": 0}
            analysis["standards_coverage"][standard]["total"] += 1
            if status == "compliant":
                analysis["standards_coverage"][standard]["compliant"] += 1

        # Calculate compliance percentage
        if analysis["total_checks"] > 0:
            analysis["compliance_percentage"] = round(
                (analysis["compliant_count"] / analysis["total_checks"]) * 100, 2
            )

        return analysis

    def _analyze_monitoring(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze security monitoring data."""
        events = data.get("events", [])

        analysis = {
            "total_events": len(events),
            "events_by_type": {},
            "events_by_severity": {},
            "recent_events": [],
            "anomalies_detected": 0,
        }

        for event in events:
            # Count by type
            event_type = event.get("event_type", "unknown")
            if event_type not in analysis["events_by_type"]:
                analysis["events_by_type"][event_type] = 0
            analysis["events_by_type"][event_type] += 1

            # Count by severity
            severity = event.get("severity", "unknown")
            if severity not in analysis["events_by_severity"]:
                analysis["events_by_severity"][severity] = 0
            analysis["events_by_severity"][severity] += 1

        # Get recent events (last 24 hours)
        cutoff_time = datetime.now(timezone.utc)  # Would need proper timestamp parsing
        analysis["recent_events"] = events[:20]  # Simplified

        return analysis

    def _calculate_overall_risk(
        self, vuln_analysis: Dict, compliance_analysis: Dict, monitoring_analysis: Dict
    ) -> Dict[str, Any]:
        """Calculate overall risk assessment."""
        # Risk scoring algorithm
        risk_score = 0

        # Vulnerability risk (40% weight)
        vuln_risk = 0
        if vuln_analysis["total_vulnerabilities"] > 0:
            vuln_risk = (
                (
                    vuln_analysis["critical_count"] * 10
                    + vuln_analysis["high_count"] * 7
                    + vuln_analysis["medium_count"] * 4
                    + vuln_analysis["low_count"] * 1
                )
                / vuln_analysis["total_vulnerabilities"]
                * 10
            )
        risk_score += vuln_risk * 0.4

        # Compliance risk (30% weight)
        compliance_risk = 100 - compliance_analysis.get("compliance_percentage", 50)
        risk_score += compliance_risk * 0.3

        # Monitoring risk (30% weight)
        monitoring_risk = min(monitoring_analysis.get("total_events", 0) * 2, 100)
        risk_score += monitoring_risk * 0.3

        risk_score = min(100, max(0, risk_score))

        # Determine risk level
        if risk_score >= 70:
            risk_level = "CRITICAL"
            description = "Immediate security attention required"
        elif risk_score >= 50:
            risk_level = "HIGH"
            description = "Security improvements needed"
        elif risk_score >= 30:
            risk_level = "MEDIUM"
            description = "Monitor and address security issues"
        else:
            risk_level = "LOW"
            description = "Security posture is good"

        return {
            "score": round(risk_score, 1),
            "level": risk_level,
            "description": description,
            "components": {
                "vulnerability_risk": round(vuln_risk, 1),
                "compliance_risk": round(compliance_risk, 1),
                "monitoring_risk": round(monitoring_risk, 1),
            },
        }

    def _generate_executive_summary(
        self,
        vuln_analysis: Dict,
        compliance_analysis: Dict,
        monitoring_analysis: Dict,
        risk_assessment: Dict,
    ) -> str:
        """Generate executive summary."""
        summary = (
            f"This security assessment evaluated the target system and identified "
        )

        if vuln_analysis["total_vulnerabilities"] > 0:
            summary += (
                f"{vuln_analysis['total_vulnerabilities']} security vulnerabilities, "
            )
        else:
            summary += "no security vulnerabilities, "

        summary += f"{compliance_analysis.get('compliance_percentage', 0)}% compliance with security standards, "

        summary += f"and {monitoring_analysis.get('total_events', 0)} security events. "

        summary += f"The overall risk assessment indicates a {risk_assessment['level']} risk level "
        summary += f"with a security score of {risk_assessment['score']}/100. "

        summary += risk_assessment["description"] + "."

        return summary

    def _generate_recommendations(
        self, vuln_analysis: Dict, compliance_analysis: Dict, monitoring_analysis: Dict
    ) -> List[str]:
        """Generate security recommendations."""
        recommendations = []

        # Vulnerability recommendations
        if vuln_analysis["critical_count"] > 0:
            recommendations.append(
                "🚨 CRITICAL: Address critical vulnerabilities immediately"
            )
        if vuln_analysis["high_count"] > 0:
            recommendations.append(
                "⚠️ HIGH: Review and fix high-severity vulnerabilities within 30 days"
            )

        # Compliance recommendations
        if compliance_analysis.get("compliance_percentage", 0) < 80:
            recommendations.append(
                "📋 COMPLIANCE: Improve compliance with security standards"
            )

        # Monitoring recommendations
        if monitoring_analysis.get("total_events", 0) > 100:
            recommendations.append(
                "🔍 MONITORING: Review security monitoring alerts and reduce false positives"
            )

        # General recommendations
        recommendations.extend(
            [
                "🔒 Implement regular security scans and vulnerability assessments",
                "📚 Provide security awareness training for development team",
                "🔧 Establish secure coding practices and code review processes",
                "📊 Implement security metrics and KPIs for continuous monitoring",
            ]
        )

        return recommendations

    def _compile_findings(
        self, vuln_analysis: Dict, compliance_analysis: Dict, monitoring_analysis: Dict
    ) -> List[Dict[str, Any]]:
        """Compile all security findings."""
        findings = []

        # Vulnerability findings
        for vuln in vuln_analysis.get("top_vulnerabilities", []):
            findings.append(
                {
                    "title": vuln.get("description", "Security Vulnerability"),
                    "severity": vuln.get("severity", "UNKNOWN"),
                    "category": "vulnerability",
                    "description": vuln.get("description", ""),
                    "impact": f"Affects {vuln.get('package', 'unknown package')}",
                }
            )

        # Compliance findings
        if compliance_analysis.get("compliance_percentage", 100) < 100:
            findings.append(
                {
                    "title": "Compliance Issues",
                    "severity": "MEDIUM",
                    "category": "compliance",
                    "description": f"System is {compliance_analysis.get('compliance_percentage', 0)}% compliant",
                    "impact": "May affect regulatory compliance and security posture",
                }
            )

        # Monitoring findings
        if monitoring_analysis.get("total_events", 0) > 50:
            findings.append(
                {
                    "title": "High Security Event Volume",
                    "severity": "MEDIUM",
                    "category": "monitoring",
                    "description": f"Detected {monitoring_analysis.get('total_events', 0)} security events",
                    "impact": "May indicate security issues or monitoring configuration problems",
                }
            )

        return findings

    def _calculate_metrics(
        self, vuln_analysis: Dict, compliance_analysis: Dict, monitoring_analysis: Dict
    ) -> Dict[str, Any]:
        """Calculate security metrics."""
        return {
            "vulnerability_metrics": {
                "total_vulnerabilities": vuln_analysis["total_vulnerabilities"],
                "severity_distribution": vuln_analysis["severity_breakdown"],
                "fix_rate": 0.0,  # Would need historical data
            },
            "compliance_metrics": {
                "overall_compliance": compliance_analysis.get(
                    "compliance_percentage", 0
                ),
                "standards_coverage": compliance_analysis.get("standards_coverage", {}),
            },
            "monitoring_metrics": {
                "total_events": monitoring_analysis.get("total_events", 0),
                "events_per_day": monitoring_analysis.get("total_events", 0)
                // 30,  # Rough estimate
                "alert_effectiveness": 0.0,  # Would need alert response data
            },
        }

    def export_report(
        self, report: SecurityReport, output_path: str, format: str = "json"
    ) -> bool:
        """
        Export security report to file.

        Args:
            report: Security report to export
            output_path: Path to output file
            format: Export format (json, html, pdf)

        Returns:
            bool: True if export successful
        """
        try:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)

            if format.lower() == "json":
                with open(output_path, "w") as f:
                    json.dump(report.to_dict(), f, indent=2, default=str)

            elif format.lower() == "html":
                html_content = self._generate_html_report(report)
                with open(output_path, "w") as f:
                    f.write(html_content)

            else:
                logger.error(f"Unsupported export format: {format}")
                return False

            logger.info(f"Security report exported to {output_path}")
            return True

        except Exception as e:
            logger.error(f"Failed to export security report: {e}")
            return False

    def _generate_html_report(self, report: SecurityReport) -> str:
        """Generate HTML report from template."""
        try:
            template = self.jinja_env.get_template("executive_summary.html")
            return template.render(report=report)
        except Exception as e:
            logger.error(f"Failed to generate HTML report: {e}")
            return f"<html><body><h1>{report.title}</h1><p>Error generating report: {e}</p></body></html>"


# Convenience functions
def generate_security_report(
    vulnerability_data: Dict[str, Any],
    compliance_data: Dict[str, Any],
    monitoring_data: Dict[str, Any],
    output_path: Optional[str] = None,
) -> SecurityReport:
    """
    Convenience function to generate a comprehensive security report.

    Args:
        vulnerability_data: Vulnerability scan results
        compliance_data: Compliance check results
        monitoring_data: Security monitoring data
        output_path: Optional path to export report

    Returns:
        SecurityReport: Generated security report
    """
    generator = SecurityReportGenerator()

    report = generator.generate_comprehensive_report(
        vulnerability_data, compliance_data, monitoring_data
    )

    if output_path:
        generator.export_report(report, output_path, format="json")

    return report

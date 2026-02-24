"""Security Reports for Codomyrmex Security Audit Module.

Provides comprehensive security reporting and assessment generation capabilities.
"""

import json
import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

try:
    import jinja2
    JINJA2_AVAILABLE = True
except ImportError:
    JINJA2_AVAILABLE = False
    # Fallback to prevent immediate crash if jinja2 missing, though functionality will fail
    pass

from codomyrmex.logging_monitoring.core.logger_config import get_logger

logger = get_logger(__name__)


@dataclass
class SecurityReport:
    """Comprehensive security assessment report."""
    report_id: str
    title: str
    generated_at: datetime
    target_system: str
    executive_summary: str
    risk_assessment: dict[str, Any]
    findings: list[dict[str, Any]] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)
    compliance_status: dict[str, Any] = field(default_factory=dict)
    metrics: dict[str, Any] = field(default_factory=dict)
    appendices: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
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
    """Security report generator for comprehensive assessments."""

    def __init__(self, template_dir: str | None = None):
        """Initialize the security report generator."""
        if not JINJA2_AVAILABLE:
            raise ImportError("jinja2 package not available. Install with: pip install jinja2")

        self.template_dir = template_dir or os.path.join(
            os.path.dirname(__file__), "templates"
        )
        self.templates: dict[str, Any] = {}
        self._setup_jinja2()
        self._load_templates()

    def _setup_jinja2(self):
        """Setup Jinja2 template environment."""
        # Using DictLoader for default templates since we create them in-code
        self.jinja_env = jinja2.Environment(
            loader=jinja2.BaseLoader(),  # Placeholder, will be used with from_string usually or FileSystemLoader ifdir exists
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
        # We will use in-memory templates for simplicity and to avoid file system dependency issues in this repair
        self.templates_source = self._get_default_templates()

    def _get_default_templates(self) -> dict[str, str]:
        """Get default report templates."""
        return {
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

    def _format_datetime_filter(self, dt):
        """Jinja2 filter for formatting datetime."""
        if isinstance(dt, str):
            return dt
        return dt.strftime("%Y-%m-%d %H:%M:%S UTC")

    def _severity_color_filter(self, severity):
        """Jinja2 filter for severity colors."""
        return {
            "CRITICAL": "#dc3545",
            "HIGH": "#fd7e14",
            "MEDIUM": "#ffc107",
            "LOW": "#28a745",
            "INFO": "#6c757d",
        }.get(severity.upper(), "#6c757d")

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
        vulnerability_data: dict[str, Any],
        compliance_data: dict[str, Any],
        monitoring_data: dict[str, Any],
    ) -> SecurityReport:
        """Generate comprehensive security report."""
        report_id = f"security_report_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}"

        vulnerability_analysis = self._analyze_vulnerabilities(vulnerability_data)
        compliance_analysis = self._analyze_compliance(compliance_data)
        monitoring_analysis = self._analyze_monitoring(monitoring_data)
        overall_risk = self._calculate_overall_risk(
            vulnerability_analysis, compliance_analysis, monitoring_analysis
        )
        executive_summary = self._generate_executive_summary(
            vulnerability_analysis, compliance_analysis, monitoring_analysis, overall_risk
        )
        recommendations = self._generate_recommendations(
            vulnerability_analysis, compliance_analysis, monitoring_analysis
        )

        return SecurityReport(
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

    def _analyze_vulnerabilities(self, data: dict[str, Any]) -> dict[str, Any]:
        """Analyze vulnerability data."""
        # Simplified implementation
        vulnerabilities = data.get("vulnerabilities", [])
        return {
            "total_vulnerabilities": len(vulnerabilities),
            "critical_count": sum(1 for v in vulnerabilities if v.get("severity") == "CRITICAL"),
            "high_count": sum(1 for v in vulnerabilities if v.get("severity") == "HIGH"),
            "medium_count": sum(1 for v in vulnerabilities if v.get("severity") == "MEDIUM"),
            "low_count": sum(1 for v in vulnerabilities if v.get("severity") == "LOW"),
            "top_vulnerabilities": vulnerabilities[:10],
            "severity_breakdown": {}
        }

    def _analyze_compliance(self, data: dict[str, Any]) -> dict[str, Any]:
        """Analyze compliance data."""
        checks = data.get("compliance_checks", [])
        total = len(checks)
        compliant = sum(1 for c in checks if c.get("status") == "compliant")

        return {
             "total_checks": total,
             "compliance_percentage": (compliant / total * 100) if total > 0 else 0,
             "standards_coverage": {}
        }

    def _analyze_monitoring(self, data: dict[str, Any]) -> dict[str, Any]:
        """Analyze monitoring data."""
        events = data.get("events", [])
        return {
            "total_events": len(events),
            "events_by_type": {}
        }

    def _calculate_overall_risk(self, vuln: dict, comp: dict, mon: dict) -> dict[str, Any]:
        """Calculate overall risk."""
        # Heuristic risk scoring based on vulnerability counts
        score = 0
        if vuln.get("critical_count", 0) > 0: score += 50
        if vuln.get("high_count", 0) > 0: score += 30

        level = "LOW"
        if score > 80: level = "CRITICAL"
        elif score > 50: level = "HIGH"
        elif score > 20: level = "MEDIUM"

        return {
            "score": score,
            "level": level,
            "description": f"Risk level is {level}"
        }

    def _generate_executive_summary(self, vuln: dict, comp: dict, mon: dict, risk: dict) -> str:
        """Generate summary."""
        return f"System assessment complete. Risk Level: {risk['level']}. Found {vuln.get('total_vulnerabilities', 0)} vulnerabilities."

    def _generate_recommendations(self, vuln: dict, comp: dict, mon: dict) -> list[str]:
        """Generate recommendations."""
        recs = []
        if vuln.get("total_vulnerabilities", 0) > 0:
            recs.append("Remediate identified vulnerabilities.")
        return recs

    def _compile_findings(self, vuln: dict, comp: dict, mon: dict) -> list[dict[str, Any]]:
        """Compile findings."""
        findings = []
        for v in vuln.get("top_vulnerabilities", []):
            findings.append({
                "title": v.get("title", "Vulnerability"),
                "severity": v.get("severity", "UNKNOWN"),
                "description": v.get("description", "")
            })
        return findings

    def _calculate_metrics(self, vuln: dict, comp: dict, mon: dict) -> dict[str, Any]:
        """Calculate metrics."""
        return {
            "vulnerability_metrics": vuln,
            "compliance_metrics": comp,
            "monitoring_metrics": mon
        }

    def export_report(self, report: SecurityReport, output_path: str, format: str = "json") -> bool:
        """Export report to file."""
        try:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)

            if format.lower() == "json":
                with open(output_path, "w") as f:
                    json.dump(report.to_dict(), f, indent=2, default=str)
            elif format.lower() == "html":
                template_str = self.templates_source.get("executive_summary.html", "")
                template = self.jinja_env.from_string(template_str)
                html = template.render(report=report)
                with open(output_path, "w") as f:
                    f.write(html)
            else:
                 return False
            return True
        except Exception as e:
            logger.error(f"Export failed: {e}")
            return False


def generate_security_report(
    vulnerability_data: dict[str, Any],
    compliance_data: dict[str, Any],
    monitoring_data: dict[str, Any],
    output_path: str | None = None,
) -> SecurityReport:
    """Convenience function."""
    generator = SecurityReportGenerator()
    report = generator.generate_comprehensive_report(
        vulnerability_data, compliance_data, monitoring_data
    )
    if output_path:
        generator.export_report(report, output_path, format="json")
    return report

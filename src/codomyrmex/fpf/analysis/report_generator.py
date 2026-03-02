
"""Report generator for FPF specifications.


logger = get_logger(__name__)
This module provides functionality to generate comprehensive HTML reports
with analysis, statistics, and visualizations.
"""

from datetime import datetime
from pathlib import Path

from codomyrmex.fpf.core.models import FPFSpec

from .analyzer import FPFAnalyzer
from .term_analyzer import TermAnalyzer


class ReportGenerator:
    """Generator for comprehensive FPF reports."""

    def __init__(self, spec: FPFSpec):
        """Initialize the report generator.

        Args:
            spec: The FPFSpec object
        """
        self.spec = spec
        self.analyzer = FPFAnalyzer(spec)
        self.term_analyzer = TermAnalyzer()

    def generate_report(self, output_path: Path, include_analysis: bool = True) -> None:
        """Generate comprehensive HTML report.

        Args:
            output_path: Path to output HTML file
            include_analysis: Whether to include analysis sections
        """
        analysis = self.analyzer.get_analysis_summary() if include_analysis else None
        term_frequency = self.term_analyzer.get_term_frequency(self.spec)
        shared_terms = self.term_analyzer.get_shared_terms(self.spec, min_occurrences=2)

        html_lines = [
            "<!DOCTYPE html>",
            "<html>",
            "<head>",
            "<meta charset='utf-8'>",
            "<title>FPF Specification Report</title>",
            "<style>",
            self._get_css_styles(),
            "</style>",
            "</head>",
            "<body>",
            "<div class='container'>",
            "<h1>FPF Specification Report</h1>",
            f"<p class='meta'>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>",
        ]

        # Overview section
        html_lines.extend(self._generate_overview_section())

        # Statistics section
        html_lines.extend(self._generate_statistics_section(analysis))

        # Patterns section
        html_lines.extend(self._generate_patterns_section())

        # Concepts section
        html_lines.extend(self._generate_concepts_section())

        # Analysis section
        if include_analysis and analysis:
            html_lines.extend(self._generate_analysis_section(analysis))

        # Terms section
        html_lines.extend(self._generate_terms_section(term_frequency, shared_terms))

        html_lines.extend([
            "</div>",
            "</body>",
            "</html>",
        ])

        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text("\n".join(html_lines), encoding="utf-8")

    def _get_css_styles(self) -> str:
        """Get CSS styles for HTML report."""
        return """
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background: #f5f5f5;
        }
        .container {
            background: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        h1 {
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
        }
        h2 {
            color: #34495e;
            margin-top: 30px;
            border-bottom: 2px solid #ecf0f1;
            padding-bottom: 5px;
        }
        .meta {
            color: #7f8c8d;
            font-size: 0.9em;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }
        th, td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }
        th {
            background-color: #3498db;
            color: white;
            font-weight: bold;
        }
        tr:hover {
            background-color: #f5f5f5;
        }
        .stat-box {
            display: inline-block;
            margin: 10px;
            padding: 15px;
            background: #ecf0f1;
            border-radius: 5px;
            min-width: 150px;
        }
        .stat-value {
            font-size: 2em;
            font-weight: bold;
            color: #3498db;
        }
        .stat-label {
            color: #7f8c8d;
            font-size: 0.9em;
        }
        """

    def _generate_overview_section(self) -> list[str]:
        """Generate overview section."""
        return [
            "<h2>Overview</h2>",
            f"<p><strong>Version:</strong> {self.spec.version or 'Unknown'}</p>",
            f"<p><strong>Source:</strong> {self.spec.source_url or 'Unknown'}</p>",
            f"<p><strong>Total Patterns:</strong> {len(self.spec.patterns)}</p>",
            f"<p><strong>Total Concepts:</strong> {len(self.spec.concepts)}</p>",
            f"<p><strong>Total Relationships:</strong> {len(self.spec.relationships)}</p>",
        ]

    def _generate_statistics_section(self, analysis: dict | None) -> list[str]:
        """Generate statistics section."""
        lines = ["<h2>Statistics</h2>", "<div class='stats-grid'>"]

        # Pattern statistics
        status_counts = {}
        for pattern in self.spec.patterns:
            status = pattern.status
            status_counts[status] = status_counts.get(status, 0) + 1

        for status, count in status_counts.items():
            lines.append(
                f"<div class='stat-box'>"
                f"<div class='stat-value'>{count}</div>"
                f"<div class='stat-label'>{status} Patterns</div>"
                f"</div>"
            )

        if analysis:
            lines.append(
                f"<div class='stat-box'>"
                f"<div class='stat-value'>{analysis['statistics'].get('avg_importance', 0):.2f}</div>"
                f"<div class='stat-label'>Avg Importance</div>"
                f"</div>"
            )

        lines.append("</div>")
        return lines

    def _generate_patterns_section(self) -> list[str]:
        """Generate patterns section."""
        lines = [
            "<h2>Patterns</h2>",
            "<table>",
            "<tr><th>ID</th><th>Title</th><th>Status</th><th>Part</th></tr>",
        ]

        for pattern in sorted(self.spec.patterns, key=lambda p: p.id):
            lines.append(
                f"<tr>"
                f"<td>{pattern.id}</td>"
                f"<td>{pattern.title}</td>"
                f"<td>{pattern.status}</td>"
                f"<td>{pattern.part or 'N/A'}</td>"
                f"</tr>"
            )

        lines.append("</table>")
        return lines

    def _generate_concepts_section(self) -> list[str]:
        """Generate concepts section."""
        lines = [
            "<h2>Top Concepts</h2>",
            "<table>",
            "<tr><th>Name</th><th>Type</th><th>Pattern</th></tr>",
        ]

        for concept in sorted(self.spec.concepts[:50], key=lambda c: c.name):
            lines.append(
                f"<tr>"
                f"<td>{concept.name}</td>"
                f"<td>{concept.type}</td>"
                f"<td>{concept.pattern_id}</td>"
                f"</tr>"
            )

        lines.append("</table>")
        return lines

    def _generate_analysis_section(self, analysis: dict) -> list[str]:
        """Generate analysis section."""
        lines = ["<h2>Analysis</h2>"]

        # Critical patterns
        lines.append("<h3>Critical Patterns</h3>")
        lines.append("<table><tr><th>Pattern ID</th><th>Importance Score</th></tr>")
        for pattern_id, score in analysis.get("critical_patterns", [])[:10]:
            lines.append(f"<tr><td>{pattern_id}</td><td>{score:.3f}</td></tr>")
        lines.append("</table>")

        # Part cohesion
        lines.append("<h3>Part Cohesion</h3>")
        lines.append("<table><tr><th>Part</th><th>Cohesion Score</th></tr>")
        for part, cohesion in analysis.get("part_cohesion", {}).items():
            lines.append(f"<tr><td>{part}</td><td>{cohesion:.3f}</td></tr>")
        lines.append("</table>")

        return lines

    def _generate_terms_section(
        self, term_frequency: dict[str, int], shared_terms: list[tuple[str, int, list[str]]]
    ) -> list[str]:
        """Generate terms section."""
        lines = [
            "<h2>Shared Terms</h2>",
            "<p>Terms that appear across multiple patterns:</p>",
            "<table><tr><th>Term</th><th>Occurrences</th><th>Patterns</th></tr>",
        ]

        for term, count, pattern_ids in shared_terms[:20]:
            patterns_str = ", ".join(pattern_ids[:5])
            if len(pattern_ids) > 5:
                patterns_str += f" (+{len(pattern_ids) - 5} more)"
            lines.append(
                f"<tr>"
                f"<td>{term}</td>"
                f"<td>{count}</td>"
                f"<td>{patterns_str}</td>"
                f"</tr>"
            )

        lines.append("</table>")
        return lines


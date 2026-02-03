"""Data visualizer using codomyrmex visualization capabilities.

Demonstrates integration with codomyrmex.data_visualization for
creating charts, plots, and interactive visualizations.

Example:
    >>> from pathlib import Path
    >>> from src.visualizer import DataVisualizer
    >>> 
    >>> visualizer = DataVisualizer()
    >>> dashboard_path = visualizer.create_dashboard(analysis_results)
    >>> print(f"Dashboard saved to: {dashboard_path}")
"""

from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime
import json
import logging

# Real codomyrmex imports - no fallback for mega-seed project
from codomyrmex.logging_monitoring import get_logger

HAS_CODOMYRMEX_LOGGING = True  # Exported for integration tests

logger = get_logger(__name__)


@dataclass
class ChartConfig:
    """Configuration for chart generation.
    
    Attributes:
        title: Chart title.
        chart_type: Type of chart (bar, line, pie, etc.).
        width: Chart width in pixels.
        height: Chart height in pixels.
        theme: Color theme (dark, light).
        output_format: Output file format (png, svg, html).
        
    Example:
        >>> config = ChartConfig(title="Code Metrics", chart_type="bar")
        >>> print(config.theme)  # "dark"
    """
    
    title: str
    chart_type: str = "bar"
    width: int = 800
    height: int = 600
    theme: str = "dark"
    output_format: str = "html"
    
    @property
    def is_interactive(self) -> bool:
        """Check if output format supports interactivity."""
        return self.output_format == "html"


class DataVisualizer:
    """Visualizer for analysis results.
    
    Creates visual representations of code analysis data using
    codomyrmex.data_visualization module capabilities.
    
    Generates HTML dashboards with:
    - Summary metrics cards
    - File analysis tables
    - Pattern distribution charts
    - Issue summaries
    
    Attributes:
        output_dir: Directory for generated visualizations.
        
    Example:
        >>> visualizer = DataVisualizer(output_dir=Path("reports"))
        >>> path = visualizer.create_dashboard(results)
    """
    
    def __init__(self, output_dir: Optional[Path] = None):
        """Initialize the visualizer.
        
        Args:
            output_dir: Directory for generated visualizations.
                       Defaults to "reports/visualizations".
        """
        self.output_dir = output_dir or Path("reports/visualizations")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Theme colors
        self.colors = {
            "primary": "#667eea",
            "secondary": "#764ba2",
            "accent": "#e94560",
            "background": "#1a1a2e",
            "surface": "#16213e",
            "text": "#eee",
            "muted": "#888",
        }
        
    def visualize_metrics(
        self,
        metrics: Dict[str, Any],
        config: Optional[ChartConfig] = None
    ) -> Path:
        """Create visualization of analysis metrics.
        
        Args:
            metrics: Dictionary of metrics to visualize.
            config: Optional chart configuration.
            
        Returns:
            Path to generated visualization.
            
        Example:
            >>> metrics = {"lines": 1000, "functions": 50}
            >>> path = visualizer.visualize_metrics(metrics)
        """
        config = config or ChartConfig(title="Code Metrics")
        
        logger.info(f"Generating {config.chart_type} chart: {config.title}")
        
        # Generate safe filename
        safe_title = config.title.lower().replace(" ", "_").replace("/", "_")
        output_path = self.output_dir / f"{safe_title}.{config.output_format}"
        
        # Generate chart HTML
        html = self._generate_metrics_chart(metrics, config)
        output_path.write_text(html)
        
        logger.info(f"Visualization saved to {output_path}")
        
        return output_path
        
    def create_dashboard(
        self,
        analysis_results: Dict[str, Any],
        output_path: Optional[Path] = None
    ) -> Path:
        """Create interactive dashboard from analysis results.
        
        Generates a comprehensive HTML dashboard with:
        - Summary metrics (files, lines, functions, classes)
        - File analysis table
        - Pattern distribution
        - Issue summary
        
        Args:
            analysis_results: Complete analysis results from ProjectAnalyzer.
            output_path: Optional custom output path.
            
        Returns:
            Path to generated dashboard HTML.
            
        Example:
            >>> results = analyzer.analyze(Path("src"))
            >>> dashboard = visualizer.create_dashboard(results)
            >>> print(f"Open {dashboard} in browser")
        """
        output_path = output_path or self.output_dir / "dashboard.html"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Creating dashboard at {output_path}")
        
        # Generate dashboard sections
        sections = []
        
        # Header section
        sections.append(self._create_header_section(analysis_results))
        
        # Summary section
        if "summary" in analysis_results:
            sections.append(self._create_summary_section(analysis_results["summary"]))
            
        # Patterns section
        if "summary" in analysis_results and "patterns_found" in analysis_results["summary"]:
            sections.append(self._create_patterns_section(
                analysis_results["summary"]["patterns_found"]
            ))
            
        # File metrics section
        if "files" in analysis_results:
            sections.append(self._create_files_section(analysis_results["files"]))
            
        # Issues section
        if "files" in analysis_results:
            all_issues = []
            for f in analysis_results["files"]:
                for issue in f.get("issues", []):
                    all_issues.append({**issue, "file": f.get("file", "Unknown")})
            if all_issues:
                sections.append(self._create_issues_section(all_issues))
        
        # Write dashboard HTML
        self._write_dashboard(output_path, sections)
        
        logger.info(f"Dashboard created: {output_path}")
        
        return output_path
        
    def _create_header_section(self, results: Dict[str, Any]) -> str:
        """Create dashboard header."""
        target = results.get("target", "Unknown")
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        return f"""
        <div class="header">
            <h1>🔬 Code Analysis Dashboard</h1>
            <p class="subtitle">
                <strong>Target:</strong> {target} | 
                <strong>Generated:</strong> {timestamp}
            </p>
        </div>
        """
        
    def _create_summary_section(self, summary: Dict[str, Any]) -> str:
        """Create summary section HTML with metric cards."""
        metrics = [
            ("📁", "Files Analyzed", summary.get("total_files", 0)),
            ("📝", "Lines of Code", summary.get("total_lines", 0)),
            ("⚡", "Functions", summary.get("total_functions", 0)),
            ("🏗️", "Classes", summary.get("total_classes", 0)),
            ("⚠️", "Issues", summary.get("total_issues", 0)),
            ("📊", "Avg Lines/File", f"{summary.get('average_lines_per_file', 0):.1f}"),
        ]
        
        cards = ""
        for icon, label, value in metrics:
            cards += f"""
            <div class="metric-card">
                <span class="metric-icon">{icon}</span>
                <span class="metric-value">{value}</span>
                <span class="metric-label">{label}</span>
            </div>
            """
        
        return f"""
        <div class="section">
            <h2>📊 Summary Metrics</h2>
            <div class="metrics-grid">{cards}</div>
        </div>
        """
        
    def _create_patterns_section(self, patterns: Dict[str, int]) -> str:
        """Create patterns section with visual chart."""
        if not patterns:
            return ""
            
        # Sort by frequency
        sorted_patterns = sorted(patterns.items(), key=lambda x: x[1], reverse=True)
        max_count = max(patterns.values()) if patterns else 1
        
        bars = ""
        for pattern, count in sorted_patterns[:10]:
            width_pct = (count / max_count) * 100
            display_name = pattern.replace("_", " ").title()
            bars += f"""
            <div class="bar-row">
                <span class="bar-label">{display_name}</span>
                <div class="bar-container">
                    <div class="bar" style="width: {width_pct}%"></div>
                </div>
                <span class="bar-value">{count}</span>
            </div>
            """
        
        return f"""
        <div class="section">
            <h2>🎯 Patterns Detected</h2>
            <div class="bar-chart">{bars}</div>
        </div>
        """
        
    def _create_files_section(self, files: List[Dict]) -> str:
        """Create files table section HTML."""
        rows = ""
        for f in files[:20]:  # Limit to 20 files
            metrics = f.get("metrics", {})
            patterns = f.get("patterns", [])
            issues = f.get("issues", [])
            
            # Get file name from path
            file_path = f.get("file", "Unknown")
            file_name = Path(file_path).name if file_path else "Unknown"
            
            # Pattern badges
            pattern_badges = ""
            for p in patterns[:3]:
                pattern_badges += f'<span class="badge">{p}</span>'
            if len(patterns) > 3:
                pattern_badges += f'<span class="badge">+{len(patterns)-3}</span>'
            
            # Issue indicator
            issue_class = "issue-count-warning" if issues else "issue-count-ok"
            
            rows += f"""
            <tr>
                <td class="file-cell" title="{file_path}">{file_name}</td>
                <td class="number-cell">{metrics.get('lines_of_code', 0)}</td>
                <td class="number-cell">{metrics.get('functions', 0)}</td>
                <td class="number-cell">{metrics.get('classes', 0)}</td>
                <td class="patterns-cell">{pattern_badges}</td>
                <td class="number-cell {issue_class}">{len(issues)}</td>
            </tr>
            """
            
        return f"""
        <div class="section">
            <h2>📄 File Analysis</h2>
            <div class="table-container">
                <table>
                    <thead>
                        <tr>
                            <th>File</th>
                            <th>Lines</th>
                            <th>Functions</th>
                            <th>Classes</th>
                            <th>Patterns</th>
                            <th>Issues</th>
                        </tr>
                    </thead>
                    <tbody>{rows}</tbody>
                </table>
            </div>
            {f'<p class="muted">Showing {min(len(files), 20)} of {len(files)} files</p>' if len(files) > 20 else ''}
        </div>
        """
        
    def _create_issues_section(self, issues: List[Dict]) -> str:
        """Create issues summary section."""
        if not issues:
            return ""
            
        # Group by severity
        by_severity: Dict[str, List[Dict]] = {}
        for issue in issues:
            severity = issue.get("severity", "info")
            if severity not in by_severity:
                by_severity[severity] = []
            by_severity[severity].append(issue)
            
        severity_colors = {
            "error": "#e94560",
            "warning": "#ffa500",
            "info": "#667eea",
        }
        
        items = ""
        for issue in issues[:15]:
            severity = issue.get("severity", "info")
            color = severity_colors.get(severity, "#888")
            file_name = Path(issue.get("file", "")).name
            
            items += f"""
            <div class="issue-item">
                <span class="issue-severity" style="background: {color}">{severity.upper()}</span>
                <span class="issue-file">{file_name}:{issue.get('line', 0)}</span>
                <span class="issue-message">{issue.get('message', 'No message')}</span>
            </div>
            """
        
        return f"""
        <div class="section">
            <h2>⚠️ Issues Found ({len(issues)})</h2>
            <div class="issues-list">{items}</div>
            {f'<p class="muted">Showing 15 of {len(issues)} issues</p>' if len(issues) > 15 else ''}
        </div>
        """
        
    def _generate_metrics_chart(self, metrics: Dict[str, Any], config: ChartConfig) -> str:
        """Generate a simple bar chart for metrics."""
        bars = ""
        max_val = max(metrics.values()) if metrics else 1
        
        for key, value in metrics.items():
            if isinstance(value, (int, float)):
                width_pct = (value / max_val) * 100
                label = key.replace("_", " ").title()
                bars += f"""
                <div class="bar-row">
                    <span class="bar-label">{label}</span>
                    <div class="bar-container">
                        <div class="bar" style="width: {width_pct}%"></div>
                    </div>
                    <span class="bar-value">{value}</span>
                </div>
                """
                
        return f"""<!DOCTYPE html>
<html>
<head>
    <title>{config.title}</title>
    <style>
        body {{
            font-family: sans-serif;
            background: {self.colors['background']};
            color: {self.colors['text']};
            padding: 20px;
        }}
        .chart-title {{ font-size: 1.5em; margin-bottom: 20px; }}
        .bar-row {{ display: flex; align-items: center; margin: 10px 0; }}
        .bar-label {{ width: 150px; }}
        .bar-container {{
            flex: 1;
            background: {self.colors['surface']};
            border-radius: 4px;
            margin: 0 10px;
        }}
        .bar {{
            background: linear-gradient(90deg, {self.colors['primary']}, {self.colors['secondary']});
            height: 24px;
            border-radius: 4px;
        }}
        .bar-value {{ width: 60px; text-align: right; }}
    </style>
</head>
<body>
    <h1 class="chart-title">{config.title}</h1>
    <div class="bar-chart">{bars}</div>
</body>
</html>
"""
        
    def _write_dashboard(self, path: Path, sections: List[str]) -> None:
        """Write dashboard HTML file with modern styling."""
        html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Analysis Dashboard</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, {self.colors['background']} 0%, #0f0f23 100%);
            color: {self.colors['text']};
            min-height: 100vh;
            padding: 20px;
        }}
        
        .header {{
            background: linear-gradient(135deg, {self.colors['primary']} 0%, {self.colors['secondary']} 100%);
            padding: 40px;
            border-radius: 16px;
            margin-bottom: 30px;
            text-align: center;
        }}
        
        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
        }}
        
        .header .subtitle {{
            opacity: 0.9;
            font-size: 1.1em;
        }}
        
        .section {{
            background: {self.colors['surface']};
            padding: 24px;
            margin-bottom: 20px;
            border-radius: 12px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.3);
        }}
        
        .section h2 {{
            margin-bottom: 20px;
            font-size: 1.4em;
            border-bottom: 2px solid {self.colors['primary']};
            padding-bottom: 10px;
        }}
        
        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
            gap: 16px;
        }}
        
        .metric-card {{
            background: {self.colors['background']};
            padding: 20px;
            border-radius: 12px;
            text-align: center;
            border: 1px solid rgba(255,255,255,0.1);
            transition: transform 0.2s, box-shadow 0.2s;
        }}
        
        .metric-card:hover {{
            transform: translateY(-4px);
            box-shadow: 0 8px 24px rgba(102, 126, 234, 0.3);
        }}
        
        .metric-icon {{
            font-size: 1.8em;
            display: block;
            margin-bottom: 8px;
        }}
        
        .metric-value {{
            font-size: 2em;
            font-weight: bold;
            color: {self.colors['primary']};
            display: block;
        }}
        
        .metric-label {{
            color: {self.colors['muted']};
            font-size: 0.9em;
        }}
        
        .bar-chart {{
            padding: 10px 0;
        }}
        
        .bar-row {{
            display: flex;
            align-items: center;
            margin: 12px 0;
        }}
        
        .bar-label {{
            width: 140px;
            font-size: 0.95em;
        }}
        
        .bar-container {{
            flex: 1;
            background: {self.colors['background']};
            border-radius: 6px;
            margin: 0 12px;
            height: 24px;
            overflow: hidden;
        }}
        
        .bar {{
            background: linear-gradient(90deg, {self.colors['primary']}, {self.colors['secondary']});
            height: 100%;
            border-radius: 6px;
            transition: width 0.3s ease;
        }}
        
        .bar-value {{
            width: 50px;
            text-align: right;
            color: {self.colors['accent']};
            font-weight: bold;
        }}
        
        .table-container {{
            overflow-x: auto;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
        }}
        
        th {{
            background: {self.colors['primary']};
            color: white;
            padding: 14px;
            text-align: left;
            font-weight: 600;
        }}
        
        td {{
            padding: 12px 14px;
            border-bottom: 1px solid rgba(255,255,255,0.1);
        }}
        
        tr:hover {{
            background: rgba(102, 126, 234, 0.1);
        }}
        
        .file-cell {{
            max-width: 200px;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
        }}
        
        .number-cell {{
            text-align: center;
            font-family: monospace;
        }}
        
        .patterns-cell {{
            display: flex;
            gap: 4px;
            flex-wrap: wrap;
        }}
        
        .badge {{
            background: {self.colors['primary']};
            color: white;
            padding: 2px 8px;
            border-radius: 10px;
            font-size: 0.75em;
        }}
        
        .issue-count-warning {{
            color: {self.colors['accent']};
            font-weight: bold;
        }}
        
        .issue-count-ok {{
            color: #4ade80;
        }}
        
        .issues-list {{
            display: flex;
            flex-direction: column;
            gap: 8px;
        }}
        
        .issue-item {{
            background: {self.colors['background']};
            padding: 12px;
            border-radius: 8px;
            display: flex;
            align-items: center;
            gap: 12px;
        }}
        
        .issue-severity {{
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 0.7em;
            font-weight: bold;
            color: white;
        }}
        
        .issue-file {{
            font-family: monospace;
            color: {self.colors['muted']};
            min-width: 150px;
        }}
        
        .issue-message {{
            flex: 1;
        }}
        
        .muted {{
            color: {self.colors['muted']};
            font-size: 0.9em;
            margin-top: 10px;
        }}
    </style>
</head>
<body>
    {''.join(sections)}
</body>
</html>
"""
        path.write_text(html)

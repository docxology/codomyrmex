"""Report generator using codomyrmex documentation capabilities.

Demonstrates integration with codomyrmex.documentation for
generating analysis reports in multiple formats (HTML, JSON, Markdown).

Example:
    >>> from pathlib import Path
    >>> from src.reporter import ReportGenerator, ReportConfig
    >>> 
    >>> generator = ReportGenerator()
    >>> config = ReportConfig(title="Analysis Report", format="html")
    >>> report_path = generator.generate(analysis_results, config)
"""

from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import json

# Real codomyrmex imports - no fallback for mega-seed project
from codomyrmex.logging_monitoring import get_logger

HAS_CODOMYRMEX_LOGGING = True  # Exported for integration tests

logger = get_logger(__name__)


@dataclass
class ReportConfig:
    """Configuration for report generation.
    
    Attributes:
        title: Report title.
        format: Output format (html, json, markdown).
        include_visualizations: Whether to embed visualizations.
        include_metrics: Whether to include detailed metrics.
        author: Report author name.
        
    Example:
        >>> config = ReportConfig(title="My Report", format="markdown")
    """
    
    title: str = "Analysis Report"
    format: str = "html"  # html, json, markdown
    include_visualizations: bool = True
    include_metrics: bool = True
    include_file_details: bool = True
    author: str = "Codomyrmex Test Project"
    max_files: int = 50
    
    @property
    def is_html(self) -> bool:
        return self.format == "html"
    
    @property
    def is_json(self) -> bool:
        return self.format == "json"
    
    @property
    def is_markdown(self) -> bool:
        return self.format == "markdown"


class ReportGenerator:
    """Generator for analysis reports.
    
    Creates formatted reports from analysis results using
    codomyrmex.documentation module capabilities.
    
    Supports multiple output formats:
    - HTML: Styled web reports with visualizations
    - JSON: Machine-readable structured data
    - Markdown: Documentation-friendly format
    
    Attributes:
        output_dir: Directory for generated reports.
        
    Example:
        >>> generator = ReportGenerator(output_dir=Path("reports"))
        >>> path = generator.generate(results, ReportConfig(format="html"))
    """
    
    def __init__(self, output_dir: Optional[Path] = None):
        """Initialize the report generator.
        
        Args:
            output_dir: Directory for generated reports.
                       Defaults to "reports/output".
        """
        self.output_dir = output_dir or Path("reports/output")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def generate(
        self,
        analysis_results: Dict[str, Any],
        config: Optional[ReportConfig] = None
    ) -> Path:
        """Generate report from analysis results.
        
        Args:
            analysis_results: Results from ProjectAnalyzer.analyze().
            config: Report configuration options.
            
        Returns:
            Path to generated report file.
            
        Example:
            >>> path = generator.generate(results, ReportConfig(format="html"))
            >>> print(f"Report saved to: {path}")
        """
        config = config or ReportConfig()
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"report_{timestamp}.{config.format}"
        if config.format == "markdown":
            filename = f"report_{timestamp}.md"
        output_path = self.output_dir / filename
        
        logger.info(f"Generating {config.format} report: {output_path}")
        
        if config.is_json:
            self._generate_json_report(analysis_results, output_path, config)
        elif config.is_markdown:
            self._generate_markdown_report(analysis_results, output_path, config)
        else:
            self._generate_html_report(analysis_results, output_path, config)
            
        logger.info(f"Report generated: {output_path}")
        return output_path
    
    def generate_all_formats(
        self,
        analysis_results: Dict[str, Any],
        base_config: Optional[ReportConfig] = None
    ) -> Dict[str, Path]:
        """Generate reports in all supported formats.
        
        Args:
            analysis_results: Results from ProjectAnalyzer.
            base_config: Base configuration to use.
            
        Returns:
            Dictionary mapping format to generated file path.
        """
        base_config = base_config or ReportConfig()
        paths = {}
        
        for fmt in ["html", "json", "markdown"]:
            config = ReportConfig(
                title=base_config.title,
                format=fmt,
                include_visualizations=base_config.include_visualizations,
                include_metrics=base_config.include_metrics,
                author=base_config.author,
            )
            paths[fmt] = self.generate(analysis_results, config)
            
        return paths

    def _truncation_notice(self, files: list, config: "ReportConfig") -> str:
        """Generate truncation notice HTML if files exceed max limit."""
        if len(files) > config.max_files:
            shown = min(len(files), config.max_files)
            total = len(files)
            return (
                f'<p style="color: var(--muted); margin-top: 16px;">'
                f'Showing {shown} of {total} files</p>'
            )
        return ''
        
    def _generate_json_report(
        self,
        results: Dict[str, Any],
        path: Path,
        config: ReportConfig
    ) -> None:
        """Generate JSON format report."""
        report = {
            "metadata": {
                "title": config.title,
                "author": config.author,
                "generated_at": datetime.now().isoformat(),
                "format_version": "1.0",
            },
            "target": results.get("target", "Unknown"),
            "summary": results.get("summary", {}),
        }
        
        if config.include_file_details:
            files = results.get("files", [])
            if len(files) > config.max_files:
                report["files"] = files[:config.max_files]
                report["files_truncated"] = True
                report["total_files_count"] = len(files)
            else:
                report["files"] = files
        
        path.write_text(json.dumps(report, indent=2, default=str))
        
    def _generate_markdown_report(
        self,
        results: Dict[str, Any],
        path: Path,
        config: ReportConfig
    ) -> None:
        """Generate Markdown format report."""
        summary = results.get("summary", {})
        target = results.get("target", "Unknown")
        
        content = f"""# {config.title}

**Generated**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}  
**Author**: {config.author}  
**Target**: `{target}`

---

## 📊 Summary

| Metric | Value |
| :--- | ---: |
| Files Analyzed | {summary.get('total_files', 0)} |
| Total Lines | {summary.get('total_lines', 0):,} |
| Non-Empty Lines | {summary.get('total_non_empty_lines', 0):,} |
| Functions | {summary.get('total_functions', 0)} |
| Classes | {summary.get('total_classes', 0)} |
| Issues Found | {summary.get('total_issues', 0)} |
| Avg Lines/File | {summary.get('average_lines_per_file', 0):.1f} |

"""
        
        # Patterns section
        patterns = summary.get("patterns_found", {})
        if patterns:
            content += """## 🎯 Patterns Detected

| Pattern | Count |
| :--- | ---: |
"""
            for pattern, count in sorted(patterns.items(), key=lambda x: x[1], reverse=True):
                display_name = pattern.replace("_", " ").title()
                content += f"| {display_name} | {count} |\n"
            content += "\n"
        
        # Files section
        if config.include_file_details:
            files = results.get("files", [])
            content += f"""## 📄 File Analysis

"""
            for f in files[:config.max_files]:
                file_path = f.get("file", "Unknown")
                metrics = f.get("metrics", {})
                patterns = f.get("patterns", [])
                issues = f.get("issues", [])
                
                content += f"""### `{Path(file_path).name}`

- **Lines**: {metrics.get('lines_of_code', 0)}
- **Functions**: {metrics.get('functions', 0)}
- **Classes**: {metrics.get('classes', 0)}
- **Patterns**: {', '.join(patterns) if patterns else 'None'}
- **Issues**: {len(issues)}

"""
                
            if len(files) > config.max_files:
                content += f"\n*...and {len(files) - config.max_files} more files*\n"
        
        # Issues section
        all_issues = []
        for f in results.get("files", []):
            for issue in f.get("issues", []):
                all_issues.append({**issue, "file": f.get("file", "Unknown")})
                
        if all_issues:
            content += """## ⚠️ Issues

| File | Line | Severity | Message |
| :--- | ---: | :--- | :--- |
"""
            for issue in all_issues[:20]:
                file_name = Path(issue.get("file", "")).name
                line_num = issue.get('line', 0)
                severity = issue.get('severity', 'info')
                message = issue.get('message', '')
                content += f"| {file_name} | {line_num} | {severity} | {message} |\n"
            
            if len(all_issues) > 20:
                content += f"\n*...and {len(all_issues) - 20} more issues*\n"
        
        content += "\n---\n\n*Generated by Codomyrmex Test Project*\n"
        
        path.write_text(content)
        
    def _generate_html_report(
        self,
        results: Dict[str, Any],
        path: Path,
        config: ReportConfig
    ) -> None:
        """Generate HTML format report with modern styling."""
        summary = results.get("summary", {})
        target = results.get("target", "Unknown")
        
        # Build file rows
        file_rows = ""
        files = results.get("files", [])
        for f in files[:config.max_files]:
            metrics = f.get("metrics", {})
            patterns = f.get("patterns", [])
            issues = f.get("issues", [])
            
            file_path = f.get("file", "Unknown")
            file_name = Path(file_path).name if file_path else "Unknown"
            
            pattern_badges = " ".join(
                f'<span class="badge">{p}</span>' for p in patterns[:3]
            )
            if len(patterns) > 3:
                pattern_badges += f' <span class="badge">+{len(patterns)-3}</span>'
            
            issue_class = "warning" if issues else "success"
            
            file_rows += f"""
                <tr>
                    <td class="file-cell" title="{file_path}">{file_name}</td>
                    <td class="num">{metrics.get('lines_of_code', 0):,}</td>
                    <td class="num">{metrics.get('functions', 0)}</td>
                    <td class="num">{metrics.get('classes', 0)}</td>
                    <td>{pattern_badges or '-'}</td>
                    <td class="num {issue_class}">{len(issues)}</td>
                </tr>
            """
        
        # Build pattern chart
        patterns = summary.get("patterns_found", {})
        pattern_bars = ""
        if patterns:
            max_count = max(patterns.values())
            for pattern, count in sorted(patterns.items(), key=lambda x: x[1], reverse=True)[:10]:
                width = (count / max_count) * 100
                display_name = pattern.replace("_", " ").title()
                pattern_bars += f"""
                    <div class="bar-row">
                        <span class="label">{display_name}</span>
                        <div class="bar-bg"><div class="bar" style="width: {width}%"></div></div>
                        <span class="value">{count}</span>
                    </div>
                """
        
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{config.title}</title>
    <style>
        :root {{
            --primary: #667eea;
            --secondary: #764ba2;
            --accent: #e94560;
            --bg: #f8fafc;
            --surface: #ffffff;
            --text: #1e293b;
            --muted: #64748b;
            --border: #e2e8f0;
        }}
        
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        
        body {{
            font-family: 'Segoe UI', system-ui, sans-serif;
            background: var(--bg);
            color: var(--text);
            line-height: 1.6;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 40px 20px;
        }}
        
        .header {{
            background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
            color: white;
            padding: 60px 40px;
            border-radius: 16px;
            margin-bottom: 40px;
            box-shadow: 0 10px 40px rgba(102, 126, 234, 0.3);
        }}
        
        .header h1 {{
            font-size: 2.5rem;
            margin-bottom: 10px;
        }}
        
        .header .meta {{
            opacity: 0.9;
        }}
        
        .card {{
            background: var(--surface);
            border-radius: 12px;
            padding: 30px;
            margin-bottom: 24px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            border: 1px solid var(--border);
        }}
        
        .card h2 {{
            font-size: 1.5rem;
            margin-bottom: 24px;
            color: var(--primary);
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        
        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
            gap: 20px;
        }}
        
        .metric {{
            background: linear-gradient(135deg, #f0f4ff 0%, #fdf4ff 100%);
            padding: 24px;
            border-radius: 12px;
            text-align: center;
        }}
        
        .metric .icon {{
            font-size: 2rem;
            margin-bottom: 8px;
        }}
        
        .metric .value {{
            font-size: 2.5rem;
            font-weight: 700;
            color: var(--primary);
        }}
        
        .metric .label {{
            color: var(--muted);
            font-size: 0.9rem;
        }}
        
        .bar-row {{
            display: flex;
            align-items: center;
            margin: 12px 0;
        }}
        
        .bar-row .label {{
            width: 160px;
            font-size: 0.95rem;
        }}
        
        .bar-bg {{
            flex: 1;
            background: var(--border);
            border-radius: 8px;
            height: 28px;
            margin: 0 16px;
            overflow: hidden;
        }}
        
        .bar {{
            background: linear-gradient(90deg, var(--primary), var(--secondary));
            height: 100%;
            border-radius: 8px;
            transition: width 0.3s;
        }}
        
        .bar-row .value {{
            width: 40px;
            text-align: right;
            font-weight: 600;
            color: var(--primary);
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
        }}
        
        th {{
            background: var(--primary);
            color: white;
            padding: 16px;
            text-align: left;
            font-weight: 600;
        }}
        
        td {{
            padding: 14px 16px;
            border-bottom: 1px solid var(--border);
        }}
        
        tr:hover {{
            background: #f8fafc;
        }}
        
        .file-cell {{
            max-width: 200px;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
            font-family: 'SF Mono', monospace;
            font-size: 0.9rem;
        }}
        
        .num {{
            text-align: center;
            font-family: 'SF Mono', monospace;
        }}
        
        .num.warning {{
            color: var(--accent);
            font-weight: 600;
        }}
        
        .num.success {{
            color: #10b981;
        }}
        
        .badge {{
            background: var(--primary);
            color: white;
            padding: 3px 10px;
            border-radius: 12px;
            font-size: 0.75rem;
            margin-right: 4px;
        }}
        
        .footer {{
            text-align: center;
            padding: 40px;
            color: var(--muted);
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 {config.title}</h1>
            <p class="meta">
                <strong>Target:</strong> {target} | 
                <strong>Generated:</strong> {datetime.now().strftime("%Y-%m-%d %H:%M:%S")} | 
                <strong>Author:</strong> {config.author}
            </p>
        </div>
        
        <div class="card">
            <h2>📈 Summary Metrics</h2>
            <div class="metrics-grid">
                <div class="metric">
                    <div class="icon">📁</div>
                    <div class="value">{summary.get('total_files', 0)}</div>
                    <div class="label">Files Analyzed</div>
                </div>
                <div class="metric">
                    <div class="icon">📝</div>
                    <div class="value">{summary.get('total_lines', 0):,}</div>
                    <div class="label">Lines of Code</div>
                </div>
                <div class="metric">
                    <div class="icon">⚡</div>
                    <div class="value">{summary.get('total_functions', 0)}</div>
                    <div class="label">Functions</div>
                </div>
                <div class="metric">
                    <div class="icon">🏗️</div>
                    <div class="value">{summary.get('total_classes', 0)}</div>
                    <div class="label">Classes</div>
                </div>
                <div class="metric">
                    <div class="icon">⚠️</div>
                    <div class="value">{summary.get('total_issues', 0)}</div>
                    <div class="label">Issues Found</div>
                </div>
                <div class="metric">
                    <div class="icon">📊</div>
                    <div class="value">{summary.get('average_lines_per_file', 0):.0f}</div>
                    <div class="label">Avg Lines/File</div>
                </div>
            </div>
        </div>
        
        {f'''
        <div class="card">
            <h2>🎯 Patterns Detected</h2>
            {pattern_bars}
        </div>
        ''' if pattern_bars else ''}
        
        <div class="card">
            <h2>📄 File Analysis</h2>
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
                <tbody>
                    {file_rows}
                </tbody>
            </table>
            {self._truncation_notice(files, config)}
        </div>
        
        <div class="footer">
            <p>Generated by <strong>Codomyrmex Test Project</strong></p>
        </div>
    </div>
</body>
</html>
"""
        path.write_text(html)

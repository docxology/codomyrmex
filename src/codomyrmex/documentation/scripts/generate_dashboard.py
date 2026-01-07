#!/usr/bin/env python3
"""
Documentation Dashboard Generator for Codomyrmex.

Generates an interactive HTML dashboard showing documentation quality metrics,
validation results, and progress tracking.
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

try:
    from codomyrmex.logging_monitoring.logger_config import get_logger, setup_logging
    setup_logging()
    logger = get_logger(__name__)
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)


class DocumentationDashboard:
    """Generates interactive documentation quality dashboard."""
    
    def __init__(self, repo_root: Path):
        """Initialize dashboard generator."""
        self.repo_root = repo_root.resolve()
        self.output_dir = repo_root / 'output'
        
    def load_validation_results(self) -> Dict:
        """Load all validation results."""
        results = {}
        
        # Load link validation results
        link_file = self.output_dir / 'link_validation_results.json'
        if link_file.exists():
            try:
                results['links'] = json.loads(link_file.read_text())
                logger.info("Loaded link validation results")
            except Exception as e:
                logger.warning(f"Error loading link validation: {e}")
                results['links'] = None
        else:
            logger.warning("Link validation results not found")
            results['links'] = None
        
        # Load content quality results
        quality_file = self.output_dir / 'content_quality_report.json'
        if quality_file.exists():
            try:
                results['quality'] = json.loads(quality_file.read_text())
                logger.info("Loaded content quality results")
            except Exception as e:
                logger.warning(f"Error loading quality report: {e}")
                results['quality'] = None
        else:
            logger.warning("Content quality results not found")
            results['quality'] = None
        
        # Load AGENTS.md structure validation
        agents_file = self.output_dir / 'agents_structure_validation.json'
        if agents_file.exists():
            try:
                results['agents'] = json.loads(agents_file.read_text())
                logger.info("Loaded AGENTS.md validation results")
            except Exception as e:
                logger.warning(f"Error loading AGENTS validation: {e}")
                results['agents'] = None
        else:
            logger.warning("AGENTS.md validation results not found")
            results['agents'] = None
        
        return results
    
    def generate_dashboard(self, output_path: Path) -> Path:
        """Generate HTML dashboard."""
        logger.info("Generating documentation dashboard...")
        
        # Load all validation results
        results = self.load_validation_results()
        
        # Generate HTML
        html = self._generate_html(results)
        
        # Write dashboard
        dashboard_file = output_path / 'documentation_dashboard.html'
        dashboard_file.write_text(html)
        
        logger.info(f"Dashboard generated: {dashboard_file}")
        return dashboard_file
    
    def _generate_html(self, results: Dict) -> str:
        """Generate HTML dashboard content."""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Codomyrmex Documentation Dashboard</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            background: #f5f5f5;
            padding: 20px;
        }}
        .container {{ max-width: 1400px; margin: 0 auto; }}
        header {{
            background: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin-bottom: 30px;
        }}
        h1 {{ color: #333; margin-bottom: 10px; }}
        .subtitle {{ color: #666; font-size: 14px; }}
        .grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .card {{
            background: white;
            border-radius: 8px;
            padding: 25px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .card h2 {{
            color: #333;
            margin-bottom: 20px;
            font-size: 18px;
            border-bottom: 2px solid #4CAF50;
            padding-bottom: 10px;
        }}
        .metric {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 15px 0;
            border-bottom: 1px solid #eee;
        }}
        .metric:last-child {{ border-bottom: none; }}
        .metric-label {{ color: #666; font-size: 14px; }}
        .metric-value {{
            font-size: 24px;
            font-weight: bold;
        }}
        .metric-value.good {{ color: #4CAF50; }}
        .metric-value.warning {{ color: #FF9800; }}
        .metric-value.error {{ color: #F44336; }}
        .progress-bar {{
            width: 100%;
            height: 30px;
            background: #eee;
            border-radius: 15px;
            overflow: hidden;
            margin: 10px 0;
        }}
        .progress-fill {{
            height: 100%;
            background: linear-gradient(90deg, #4CAF50 0%, #8BC34A 100%);
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: bold;
            font-size: 14px;
            transition: width 0.3s ease;
        }}
        .status-badge {{
            display: inline-block;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: bold;
        }}
        .status-badge.good {{ background: #4CAF50; color: white; }}
        .status-badge.warning {{ background: #FF9800; color: white; }}
        .status-badge.error {{ background: #F44336; color: white; }}
        .section {{ margin-bottom: 30px; }}
        .priority-list {{
            list-style: none;
            padding: 0;
        }}
        .priority-item {{
            padding: 12px;
            background: #f9f9f9;
            margin: 8px 0;
            border-radius: 4px;
            border-left: 4px solid #F44336;
        }}
        .priority-item code {{
            background: #e0e0e0;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: 'Courier New', monospace;
        }}
        footer {{
            text-align: center;
            color: #666;
            margin-top: 40px;
            padding: 20px;
            font-size: 12px;
        }}
        .chart-placeholder {{
            background: #f0f0f0;
            height: 200px;
            display: flex;
            align-items: center;
            justify-content: center;
            border-radius: 4px;
            color: #999;
            margin: 20px 0;
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>📚 Codomyrmex Documentation Dashboard</h1>
            <p class="subtitle">Comprehensive documentation quality and validation metrics</p>
            <p class="subtitle">Generated: {timestamp}</p>
        </header>
"""
        
        # Overall status section
        html += self._generate_overall_status(results)
        
        # Metrics cards
        html += '<div class="grid">'
        html += self._generate_link_validation_card(results.get('links'))
        html += self._generate_quality_metrics_card(results.get('quality'))
        html += self._generate_agents_validation_card(results.get('agents'))
        html += '</div>'
        
        # Priority actions
        html += self._generate_priority_actions(results)
        
        # Footer
        html += f"""
        <footer>
            <p>Codomyrmex Documentation Quality Dashboard</p>
            <p>For more information, see <a href="../README.md">Project README</a></p>
        </footer>
    </div>
</body>
</html>
"""
        
        return html
    
    def _generate_overall_status(self, results: Dict) -> str:
        """Generate overall status section."""
        # Calculate overall completion percentage
        scores = []
        
        if results.get('quality'):
            avg_score = results['quality'].get('average_score', 0)
            scores.append(avg_score)
        
        if results.get('agents'):
            total = results['agents'].get('total_files', 1)
            valid = results['agents'].get('valid_files', 0)
            agents_score = (valid / total * 100) if total > 0 else 0
            scores.append(agents_score)
        
        if results.get('links'):
            total_links = results['links'].get('total_links', 1)
            broken = len(results['links'].get('broken_links', []))
            link_score = ((total_links - broken) / total_links * 100) if total_links > 0 else 0
            scores.append(link_score)
        
        overall_completion = sum(scores) / len(scores) if scores else 0
        
        status_class = 'good' if overall_completion >= 80 else 'warning' if overall_completion >= 60 else 'error'
        status_text = 'Excellent' if overall_completion >= 80 else 'Good' if overall_completion >= 60 else 'Needs Attention'
        
        html = f"""
        <div class="card">
            <h2>Overall Documentation Status</h2>
            <div class="metric">
                <span class="metric-label">Overall Completion</span>
                <span class="metric-value {status_class}">{overall_completion:.1f}%</span>
            </div>
            <div class="progress-bar">
                <div class="progress-fill" style="width: {overall_completion}%">
                    {overall_completion:.1f}%
                </div>
            </div>
            <div class="metric">
                <span class="metric-label">Status</span>
                <span class="status-badge {status_class}">{status_text}</span>
            </div>
        </div>
"""
        return html
    
    def _generate_link_validation_card(self, link_data: Optional[Dict]) -> str:
        """Generate link validation metrics card."""
        if not link_data:
            return """
        <div class="card">
            <h2>🔗 Link Validation</h2>
            <p style="color: #999; text-align: center; padding: 40px 0;">
                No link validation data available.<br>
                Run: <code>python scripts/documentation/validate_links_comprehensive.py</code>
            </p>
        </div>
"""
        
        total_files = link_data.get('total_files', 0)
        total_links = link_data.get('total_links', 0)
        broken_links = len(link_data.get('broken_links', []))
        
        status_class = 'good' if broken_links == 0 else 'warning' if broken_links < 10 else 'error'
        
        html = f"""
        <div class="card">
            <h2>🔗 Link Validation</h2>
            <div class="metric">
                <span class="metric-label">Files Scanned</span>
                <span class="metric-value">{total_files}</span>
            </div>
            <div class="metric">
                <span class="metric-label">Total Links</span>
                <span class="metric-value">{total_links}</span>
            </div>
            <div class="metric">
                <span class="metric-label">Broken Links</span>
                <span class="metric-value {status_class}">{broken_links}</span>
            </div>
        </div>
"""
        return html
    
    def _generate_quality_metrics_card(self, quality_data: Optional[Dict]) -> str:
        """Generate content quality metrics card."""
        if not quality_data:
            return """
        <div class="card">
            <h2>📊 Content Quality</h2>
            <p style="color: #999; text-align: center; padding: 40px 0;">
                No quality data available.<br>
                Run: <code>python scripts/documentation/analyze_content_quality.py</code>
            </p>
        </div>
"""
        
        total_files = quality_data.get('total_files', 0)
        avg_score = quality_data.get('average_score', 0)
        total_placeholders = quality_data.get('total_placeholders', 0)
        needs_attention = len(quality_data.get('files_needing_attention', []))
        
        score_class = 'good' if avg_score >= 80 else 'warning' if avg_score >= 60 else 'error'
        
        html = f"""
        <div class="card">
            <h2>📊 Content Quality</h2>
            <div class="metric">
                <span class="metric-label">Files Analyzed</span>
                <span class="metric-value">{total_files}</span>
            </div>
            <div class="metric">
                <span class="metric-label">Average Score</span>
                <span class="metric-value {score_class}">{avg_score:.1f}/100</span>
            </div>
            <div class="metric">
                <span class="metric-label">Placeholder Count</span>
                <span class="metric-value {'warning' if total_placeholders > 0 else 'good'}">{total_placeholders}</span>
            </div>
            <div class="metric">
                <span class="metric-label">Needs Attention</span>
                <span class="metric-value {'warning' if needs_attention > 0 else 'good'}">{needs_attention}</span>
            </div>
        </div>
"""
        return html
    
    def _generate_agents_validation_card(self, agents_data: Optional[Dict]) -> str:
        """Generate AGENTS.md validation card."""
        if not agents_data:
            return """
        <div class="card">
            <h2>🤖 AGENTS.md Structure</h2>
            <p style="color: #999; text-align: center; padding: 40px 0;">
                No AGENTS.md validation data available.<br>
                Run: <code>python scripts/documentation/validate_agents_structure.py</code>
            </p>
        </div>
"""
        
        total_files = agents_data.get('total_files', 0)
        valid_files = agents_data.get('valid_files', 0)
        invalid_files = agents_data.get('invalid_files', 0)
        validation_rate = (valid_files / total_files * 100) if total_files > 0 else 0
        
        status_class = 'good' if validation_rate >= 90 else 'warning' if validation_rate >= 75 else 'error'
        
        html = f"""
        <div class="card">
            <h2>🤖 AGENTS.md Structure</h2>
            <div class="metric">
                <span class="metric-label">Total Files</span>
                <span class="metric-value">{total_files}</span>
            </div>
            <div class="metric">
                <span class="metric-label">Valid Files</span>
                <span class="metric-value good">{valid_files}</span>
            </div>
            <div class="metric">
                <span class="metric-label">Invalid Files</span>
                <span class="metric-value {'warning' if invalid_files > 0 else 'good'}">{invalid_files}</span>
            </div>
            <div class="metric">
                <span class="metric-label">Validation Rate</span>
                <span class="metric-value {status_class}">{validation_rate:.1f}%</span>
            </div>
        </div>
"""
        return html
    
    def _generate_priority_actions(self, results: Dict) -> str:
        """Generate priority actions section."""
        actions = []
        
        # Check for critical issues
        if results.get('links'):
            broken = len(results['links'].get('broken_links', []))
            if broken > 0:
                actions.append(f"Fix {broken} broken links in documentation")
        
        if results.get('quality'):
            needs_attention = results['quality'].get('files_needing_attention', [])
            if len(needs_attention) > 0:
                actions.append(f"Improve {len(needs_attention)} files with quality score < 60")
                # Add top 5 files
                for file_path in needs_attention[:5]:
                    actions.append(f"  → <code>{file_path}</code>")
        
        if results.get('agents'):
            invalid = results['agents'].get('invalid_files', 0)
            if invalid > 0:
                actions.append(f"Fix {invalid} invalid AGENTS.md files")
        
        if not actions:
            actions.append("✅ No critical issues found!")
        
        html = """
        <div class="card section">
            <h2>🎯 Priority Actions</h2>
            <ul class="priority-list">
"""
        
        for action in actions:
            html += f'                <li class="priority-item">{action}</li>\n'
        
        html += """
            </ul>
        </div>
"""
        return html


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate documentation quality dashboard")
    parser.add_argument('--repo-root', type=Path, default=Path.cwd(),
                       help='Repository root directory')
    parser.add_argument('--output', type=Path, default=Path('output'),
                       help='Output directory for dashboard')
    
    args = parser.parse_args()
    
    # Create output directory
    args.output.mkdir(parents=True, exist_ok=True)
    
    # Generate dashboard
    dashboard = DocumentationDashboard(args.repo_root)
    dashboard_file = dashboard.generate_dashboard(args.output)
    
    print("\n" + "="*80)
    print("DOCUMENTATION DASHBOARD GENERATED")
    print("="*80)
    print(f"Dashboard: {dashboard_file}")
    print("\nOpen the dashboard in your browser to view documentation metrics.")
    print("="*80)
    print("\n✅ Dashboard generation complete!")
    
    sys.exit(0)


if __name__ == '__main__':
    main()



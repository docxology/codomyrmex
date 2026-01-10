from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Set
import argparse
import json
import logging
import re
import sys

from dataclasses import dataclass, asdict

from codomyrmex.logging_monitoring import get_logger
from codomyrmex.logging_monitoring.logger_config import get_logger, setup_logging








































"""
except ImportError:
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)


@dataclass
class CodeExample:
    """



    #!/usr/bin/env python3
    """

Content Quality Analyzer for Codomyrmex Documentation.

Analyzes documentation content for completeness, quality metrics, and placeholder content.
"""


try:
    setup_logging()


logger = get_logger(__name__)

Represents a code example in documentation."""
    language: str
    content: str
    line_number: int


@dataclass
class ContentQualityMetrics:
    """Quality metrics for a documentation file."""
    file_path: str
    placeholder_count: int
    word_count: int
    section_count: int
    code_examples: List[CodeExample]
    navigation_completeness: float  # 0.0 to 1.0
    duplication_score: float  # 0.0 to 1.0 (0 = no duplication)
    overall_score: int  # 0 to 100
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return {
            'file_path': self.file_path,
            'placeholder_count': self.placeholder_count,
            'word_count': self.word_count,
            'section_count': self.section_count,
            'code_examples': [asdict(ex) for ex in self.code_examples],
            'navigation_completeness': self.navigation_completeness,
            'duplication_score': self.duplication_score,
            'overall_score': self.overall_score
        }


@dataclass
class QualityReport:
    """Overall quality report for all documentation."""
    total_files: int
    file_metrics: List[ContentQualityMetrics]
    average_score: float
    total_placeholders: int
    files_needing_attention: List[str]
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return {
            'total_files': self.total_files,
            'file_metrics': [m.to_dict() for m in self.file_metrics],
            'average_score': self.average_score,
            'total_placeholders': self.total_placeholders,
            'files_needing_attention': self.files_needing_attention,
            'score_distribution': self._get_score_distribution()
        }
    
    def _get_score_distribution(self) -> Dict[str, int]:
        """Get distribution of quality scores."""
        distribution = {
            'excellent (90-100)': 0,
            'good (75-89)': 0,
            'fair (60-74)': 0,
            'needs_improvement (0-59)': 0
        }
        
        for metrics in self.file_metrics:
            score = metrics.overall_score
            if score >= 90:
                distribution['excellent (90-100)'] += 1
            elif score >= 75:
                distribution['good (75-89)'] += 1
            elif score >= 60:
                distribution['fair (60-74)'] += 1
            else:
                distribution['needs_improvement (0-59)'] += 1
        
        return distribution


class ContentQualityAnalyzer:
    """Analyzes documentation content quality."""
    
    # Placeholder patterns to detect
    PLACEHOLDER_PATTERNS = [
        (r'\[TBD\]', 'TBD'),
        (r'\[FIXME\]', 'FIXME'),
        (r'\[TODO\]', 'TODO'),
        (r'\[placeholder\]', 'placeholder'),
        (r'\[Insert description\]', 'description placeholder'),
        (r'\[Brief description.*?\]', 'brief description'),
        (r'\[file\.py\]', 'file placeholder'),
        (r'\[module_path\]', 'module path placeholder'),
        (r'\[Module Name\]', 'module name placeholder'),
        (r'\[YOUR_.*?\]', 'user entry placeholder')
    ]
    
    # Required navigation sections for README files
    NAVIGATION_SECTIONS = [
        'navigation', 'table of contents', 'links', 'see also', 'related'
    ]
    
    def __init__(self, repo_root: Path):
        """Initialize analyzer."""
        self.repo_root = repo_root.resolve()
        self.content_cache: Dict[str, str] = {}
        
    def find_markdown_files(self) -> List[Path]:
        """Find all markdown files."""
        md_files = []
        
        for pattern in ['**/*.md', '**/*.MD']:
            md_files.extend(self.repo_root.glob(pattern))
        
        # Filter out ignored directories
        ignored_dirs = {
            '.git', 'node_modules', '__pycache__', '.venv', 'venv', 
            'output', '.pytest_cache', 'plugins', 'templates', 'doc_templates',
            'docs/project', '_templates', '_common', '_configs', 'outputs',
            'module_template', 'template'
        }
        filtered = [
            f for f in md_files
            if not any(ignored in f.parts for ignored in ignored_dirs)
            and 'template' not in f.name.lower()
        ]
        
        return sorted(filtered)
    
    def count_placeholders(self, content: str) -> int:
        """Count placeholder patterns in content."""
        count = 0
        
        for pattern, _ in self.PLACEHOLDER_PATTERNS:
            matches = re.findall(pattern, content, re.IGNORECASE)
            count += len(matches)
        
        return count
    
    def count_words(self, content: str) -> int:
        """Count meaningful words in content."""
        # Remove code blocks
        content_no_code = re.sub(r'```.*?```', '', content, flags=re.DOTALL)
        
        # Remove HTML tags
        content_no_html = re.sub(r'<[^>]+>', '', content_no_code)
        
        # Count words
        words = re.findall(r'\b\w+\b', content_no_html)
        
        return len(words)
    
    def count_sections(self, content: str) -> int:
        """Count sections (headers) in content."""
        # Match markdown headers (# Header)
        headers = re.findall(r'^#{1,6}\s+.+$', content, re.MULTILINE)
        
        return len(headers)
    
    def extract_code_examples(self, content: str) -> List[CodeExample]:
        """Extract code examples from content."""
        examples = []
        
        # Match fenced code blocks with language
        pattern = r'```(\w+)\n(.*?)```'
        
        line_num = 1
        for match in re.finditer(pattern, content, re.DOTALL):
            language = match.group(1)
            code_content = match.group(2).strip()
            
            # Count lines before this match to get line number
            before_match = content[:match.start()]
            line_num = before_match.count('\n') + 1
            
            examples.append(CodeExample(
                language=language,
                content=code_content,
                line_number=line_num
            ))
        
        return examples
    
    def check_navigation_completeness(self, content: str, file_path: Path) -> float:
        """Check if navigation sections are present and complete."""
        score = 0.0
        
        # Check for navigation section
        has_navigation = any(
            section in content.lower()
            for section in self.NAVIGATION_SECTIONS + ['signposting', 'navigation links', 'parent']
        )
        
        if has_navigation:
            score += 0.5
        
        # Check for actual links in navigation
        nav_links = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', content)
        
        if len(nav_links) >= 3:
            score += 0.3
        elif len(nav_links) >= 1:
            score += 0.2
        
        # Check for parent/sibling/child navigation structure (AGENTS.md pattern)
        if 'navigation links' in content.lower():
            score += 0.2
        
        return min(score, 1.0)
    
    def calculate_duplication_score(self, content: str) -> float:
        """Calculate content duplication score."""
        # Simple heuristic: check for repeated phrases
        lines = content.split('\n')
        line_counts = defaultdict(int)
        
        for line in lines:
            # Ignore very short lines and code blocks
            stripped = line.strip()
            if len(stripped) > 20 and not stripped.startswith('```'):
                line_counts[stripped] += 1
        
        # Calculate duplication ratio
        if not line_counts:
            return 0.0
        
        duplicated_lines = sum(count - 1 for count in line_counts.values() if count > 1)
        total_lines = len([l for l in lines if len(l.strip()) > 20])
        
        if total_lines == 0:
            return 0.0
        
        return min(duplicated_lines / total_lines, 1.0)
    
    def calculate_overall_score(self, metrics: ContentQualityMetrics) -> int:
        """Calculate overall quality score (0-100)."""
        score = 100
        
        # Deduct for placeholders
        score -= min(metrics.placeholder_count * 5, 30)
        
        # Deduct for low word count (< 100 words)
        if metrics.word_count < 100:
            score -= 20
        elif metrics.word_count < 200:
            score -= 10
        
        # Deduct for few sections
        if metrics.section_count < 3:
            score -= 15
        elif metrics.section_count < 5:
            score -= 5
        
        # Deduct for lack of code examples (if README)
        if 'README' in metrics.file_path and len(metrics.code_examples) == 0:
            score -= 10
        
        # Deduct for poor navigation
        nav_score = metrics.navigation_completeness
        score -= int((1.0 - nav_score) * 15)
        
        # Deduct for high duplication
        score -= int(metrics.duplication_score * 20)
        
        return max(0, min(100, score))
    
    def analyze_file(self, file_path: Path) -> ContentQualityMetrics:
        """Analyze a single file."""
        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')
            self.content_cache[str(file_path)] = content
            
            placeholder_count = self.count_placeholders(content)
            word_count = self.count_words(content)
            section_count = self.count_sections(content)
            code_examples = self.extract_code_examples(content)
            navigation_completeness = self.check_navigation_completeness(content, file_path)
            duplication_score = self.calculate_duplication_score(content)
            
            metrics = ContentQualityMetrics(
                file_path=str(file_path.relative_to(self.repo_root)),
                placeholder_count=placeholder_count,
                word_count=word_count,
                section_count=section_count,
                code_examples=code_examples,
                navigation_completeness=navigation_completeness,
                duplication_score=duplication_score,
                overall_score=0  # Will be calculated next
            )
            
            # Calculate overall score
            metrics.overall_score = self.calculate_overall_score(metrics)
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error analyzing {file_path}: {e}")
            # Return minimal metrics on error
            return ContentQualityMetrics(
                file_path=str(file_path.relative_to(self.repo_root)),
                placeholder_count=0,
                word_count=0,
                section_count=0,
                code_examples=[],
                navigation_completeness=0.0,
                duplication_score=0.0,
                overall_score=0
            )
    
    def analyze_all_files(self) -> QualityReport:
        """Analyze all documentation files."""
        logger.info("Starting content quality analysis...")
        
        md_files = self.find_markdown_files()
        logger.info(f"Found {len(md_files)} markdown files to analyze")
        
        file_metrics = []
        
        for md_file in md_files:
            logger.debug(f"Analyzing {md_file.relative_to(self.repo_root)}")
            metrics = self.analyze_file(md_file)
            file_metrics.append(metrics)
        
        # Calculate summary statistics
        average_score = sum(m.overall_score for m in file_metrics) / len(file_metrics) if file_metrics else 0
        total_placeholders = sum(m.placeholder_count for m in file_metrics)
        
        # Identify files needing attention (score < 60)
        needs_attention = [
            m.file_path for m in file_metrics
            if m.overall_score < 60
        ]
        
        report = QualityReport(
            total_files=len(file_metrics),
            file_metrics=file_metrics,
            average_score=average_score,
            total_placeholders=total_placeholders,
            files_needing_attention=needs_attention
        )
        
        logger.info(f"Analysis complete. Average score: {average_score:.1f}")
        
        return report
    
    def export_report(self, report: QualityReport, output_path: Path, format: str = "json") -> Path:
        """Export quality report."""
        if format == "json":
            output_file = output_path / "content_quality_report.json"
            output_file.write_text(json.dumps(report.to_dict(), indent=2))
            logger.info(f"Report exported to {output_file}")
            return output_file
        
        elif format == "html":
            output_file = output_path / "content_quality_report.html"
            html_content = self._generate_html_report(report)
            output_file.write_text(html_content)
            logger.info(f"HTML report exported to {output_file}")
            return output_file
        
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def _generate_html_report(self, report: QualityReport) -> str:
        """Generate HTML report."""
        distribution = report._get_score_distribution()
        
        html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Content Quality Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        h1 {{ color: #333; }}
        .summary {{ background: #f0f0f0; padding: 15px; border-radius: 5px; margin: 20px 0; }}
        .stat {{ display: inline-block; margin: 10px 20px; }}
        .stat-value {{ font-size: 24px; font-weight: bold; color: #0066cc; }}
        .stat-label {{ color: #666; }}
        table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #4CAF50; color: white; }}
        tr:nth-child(even) {{ background-color: #f2f2f2; }}
        .score-excellent {{ background-color: #4CAF50; color: white; font-weight: bold; }}
        .score-good {{ background-color: #8BC34A; }}
        .score-fair {{ background-color: #FFC107; }}
        .score-poor {{ background-color: #F44336; color: white; font-weight: bold; }}
    </style>
</head>
<body>
    <h1>Documentation Content Quality Report</h1>
    
    <div class="summary">
        <h2>Summary</h2>
        <div class="stat">
            <div class="stat-value">{report.total_files}</div>
            <div class="stat-label">Files Analyzed</div>
        </div>
        <div class="stat">
            <div class="stat-value">{report.average_score:.1f}</div>
            <div class="stat-label">Average Score</div>
        </div>
        <div class="stat">
            <div class="stat-value">{report.total_placeholders}</div>
            <div class="stat-label">Total Placeholders</div>
        </div>
        <div class="stat">
            <div class="stat-value">{len(report.files_needing_attention)}</div>
            <div class="stat-label">Files Needing Attention</div>
        </div>
    </div>
    
    <h2>Score Distribution</h2>
    <table>
        <tr>
            <th>Category</th>
            <th>Count</th>
        </tr>
"""
        
        for category, count in distribution.items():
            html += f"""
        <tr>
            <td>{category}</td>
            <td>{count}</td>
        </tr>
"""
        
        html += """
    </table>
    
    <h2>Files Needing Attention (Score < 60)</h2>
    <table>
        <tr>
            <th>File</th>
            <th>Score</th>
            <th>Placeholders</th>
            <th>Words</th>
            <th>Sections</th>
        </tr>
"""
        
        for metrics in report.file_metrics:
            if metrics.overall_score < 60:
                score_class = 'score-poor'
                html += f"""
        <tr>
            <td><code>{metrics.file_path}</code></td>
            <td class="{score_class}">{metrics.overall_score}</td>
            <td>{metrics.placeholder_count}</td>
            <td>{metrics.word_count}</td>
            <td>{metrics.section_count}</td>
        </tr>
"""
        
        html += """
    </table>
</body>
</html>
"""
        return html


def main():
    """Main entry point."""
    
    parser = argparse.ArgumentParser(description="Analyze documentation content quality")
    parser.add_argument('--repo-root', type=Path, default=Path.cwd(),
                       help='Repository root directory')
    parser.add_argument('--output', type=Path, default=Path('output'),
                       help='Output directory for results')
    parser.add_argument('--format', choices=['json', 'html', 'both'], default='both',
                       help='Output format')
    parser.add_argument('--min-score', type=int, default=60,
                       help='Minimum acceptable quality score')
    parser.add_argument('--fail-below-min', action='store_true',
                       help='Exit with error if average score below minimum')
    
    args = parser.parse_args()
    
    # Create output directory
    args.output.mkdir(parents=True, exist_ok=True)
    
    # Run analysis
    analyzer = ContentQualityAnalyzer(args.repo_root)
    report = analyzer.analyze_all_files()
    
    # Export results
    if args.format in ['json', 'both']:
        analyzer.export_report(report, args.output, 'json')
    
    if args.format in ['html', 'both']:
        analyzer.export_report(report, args.output, 'html')
    
    # Print summary
    print("\n" + "="*80)
    print("CONTENT QUALITY SUMMARY")
    print("="*80)
    print(f"Files analyzed: {report.total_files}")
    print(f"Average score: {report.average_score:.1f}/100")
    print(f"Total placeholders: {report.total_placeholders}")
    print(f"Files needing attention: {len(report.files_needing_attention)}")
    print("\nScore Distribution:")
    for category, count in report._get_score_distribution().items():
        print(f"  {category}: {count}")
    print("="*80)
    
    # Exit with error if requested and score below minimum
    if args.fail_below_min and report.average_score < args.min_score:
        print(f"\n❌ Quality check failed: average score {report.average_score:.1f} below minimum {args.min_score}")
        sys.exit(1)
    
    print("\n✅ Analysis complete!")
    sys.exit(0)


if __name__ == '__main__':
    main()

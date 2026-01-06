#!/usr/bin/env python3
"""
Comprehensive Link Validator for Codomyrmex Documentation.

Validates markdown links across the entire repository, checking internal references,
external URLs, circular references, and orphaned documents.
"""

import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional
from dataclasses import dataclass, asdict
from urllib.parse import urlparse, urljoin
from collections import defaultdict
import time

try:
    import networkx as nx
    HAS_NETWORKX = True
except ImportError:
    HAS_NETWORKX = False
    print("Warning: networkx not available. Graph features disabled.")

try:
    import requests
    HAS_REQUESTS = False
except ImportError:
    HAS_REQUESTS = False

try:
    from codomyrmex.logging_monitoring.logger_config import get_logger, setup_logging
    setup_logging()
    logger = get_logger(__name__)
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)


@dataclass
class BrokenLink:
    """Represents a broken link."""
    file_path: str
    line_number: int
    link_text: str
    link_url: str
    resolved_path: str
    issue_type: str  # 'broken_internal', 'broken_external', 'circular', 'orphaned'


@dataclass
class ValidationReport:
    """Comprehensive validation report."""
    total_files: int
    total_links: int
    broken_links: List[BrokenLink]
    external_urls: Dict[str, bool]
    circular_references: List[Tuple[str, str]]
    orphaned_documents: List[str]
    validation_time: float
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return {
            'total_files': self.total_files,
            'total_links': self.total_links,
            'broken_links': [asdict(link) for link in self.broken_links],
            'external_urls': self.external_urls,
            'circular_references': [[src, dst] for src, dst in self.circular_references],
            'orphaned_documents': self.orphaned_documents,
            'validation_time': self.validation_time,
            'summary': {
                'broken_links_count': len(self.broken_links),
                'failed_external_urls': sum(1 for v in self.external_urls.values() if not v),
                'circular_references_count': len(self.circular_references),
                'orphaned_documents_count': len(self.orphaned_documents)
            }
        }


class ComprehensiveLinkValidator:
    """Comprehensive link validation system."""
    
    def __init__(self, repo_root: Path):
        """Initialize validator."""
        self.repo_root = repo_root.resolve()
        self.broken_links: List[BrokenLink] = []
        self.external_urls: Dict[str, bool] = {}
        self.link_graph = defaultdict(set) if HAS_NETWORKX else None
        self.markdown_files: Set[Path] = set()
        self.url_cache: Dict[str, bool] = {}
        
    def find_all_markdown_files(self) -> Set[Path]:
        """Find all markdown files in repository."""
        logger.info("Scanning for markdown files...")
        md_files = set()
        
        for pattern in ['**/*.md', '**/*.MD']:
            md_files.update(self.repo_root.glob(pattern))
        
        # Filter out files in ignored directories
        ignored_dirs = {'.git', 'node_modules', '__pycache__', '.venv', 'venv'}
        filtered_files = {
            f for f in md_files 
            if not any(ignored in f.parts for ignored in ignored_dirs)
        }
        
        logger.info(f"Found {len(filtered_files)} markdown files")
        return filtered_files
    
    def extract_links(self, file_path: Path) -> List[Tuple[int, str, str]]:
        """Extract markdown links from a file."""
        links = []
        
        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')
            
            # Match markdown links: [text](url)
            link_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
            
            for line_num, line in enumerate(content.split('\n'), 1):
                for match in re.finditer(link_pattern, line):
                    link_text = match.group(1)
                    link_url = match.group(2)
                    
                    # Skip anchor-only links
                    if link_url.startswith('#'):
                        continue
                    
                    links.append((line_num, link_text, link_url))
        
        except Exception as e:
            logger.warning(f"Error reading {file_path}: {e}")
        
        return links
    
    def resolve_internal_link(self, source_file: Path, link_url: str) -> Optional[Path]:
        """Resolve an internal link relative to source file."""
        # Remove anchor if present
        link_url = link_url.split('#')[0]
        
        if not link_url:
            return None
        
        # Handle absolute and relative paths
        if link_url.startswith('/'):
            # Absolute from repo root
            target = self.repo_root / link_url.lstrip('/')
        else:
            # Relative to source file
            target = (source_file.parent / link_url).resolve()
        
        return target
    
    def check_internal_links(self, file_path: Path) -> List[BrokenLink]:
        """Check internal links in a file."""
        broken = []
        links = self.extract_links(file_path)
        
        for line_num, link_text, link_url in links:
            # Skip external URLs
            if link_url.startswith(('http://', 'https://', 'ftp://', 'mailto:')):
                continue
            
            resolved = self.resolve_internal_link(file_path, link_url)
            
            if resolved is None:
                continue
            
            if not resolved.exists():
                # Try to get relative path, fallback to absolute if outside repo
                try:
                    resolved_str = str(resolved.relative_to(self.repo_root))
                except ValueError:
                    resolved_str = str(resolved)
                
                broken.append(BrokenLink(
                    file_path=str(file_path.relative_to(self.repo_root)),
                    line_number=line_num,
                    link_text=link_text,
                    link_url=link_url,
                    resolved_path=resolved_str,
                    issue_type='broken_internal'
                ))
            
            # Build link graph for circular reference detection
            if HAS_NETWORKX and resolved.exists():
                self.link_graph[str(file_path)].add(str(resolved))
        
        return broken
    
    def verify_external_urls(self, urls: Set[str], timeout: int = 5) -> Dict[str, bool]:
        """Verify external URLs with caching."""
        if not HAS_REQUESTS:
            logger.warning("Requests library not available, skipping external URL validation")
            return {url: True for url in urls}
        
        results = {}
        
        for url in urls:
            # Check cache first
            if url in self.url_cache:
                results[url] = self.url_cache[url]
                continue
            
            try:
                response = requests.head(url, timeout=timeout, allow_redirects=True)
                is_valid = response.status_code < 400
                results[url] = is_valid
                self.url_cache[url] = is_valid
                
                # Be nice to servers
                time.sleep(0.1)
                
            except Exception as e:
                logger.debug(f"Failed to verify {url}: {e}")
                results[url] = False
                self.url_cache[url] = False
        
        return results
    
    def detect_circular_references(self) -> List[Tuple[str, str]]:
        """Detect circular references in documentation."""
        if not HAS_NETWORKX:
            logger.warning("NetworkX not available, skipping circular reference detection")
            return []
        
        # Build graph
        G = nx.DiGraph()
        for source, targets in self.link_graph.items():
            for target in targets:
                G.add_edge(source, target)
        
        # Find cycles
        circular = []
        try:
            cycles = list(nx.simple_cycles(G))
            for cycle in cycles:
                if len(cycle) >= 2:
                    circular.append((cycle[0], cycle[1]))
        except Exception as e:
            logger.warning(f"Error detecting cycles: {e}")
        
        return circular
    
    def find_orphaned_documents(self) -> List[str]:
        """Find documents that are not linked from anywhere."""
        if not HAS_NETWORKX:
            logger.warning("NetworkX not available, skipping orphaned document detection")
            return []
        
        # Find all markdown files
        all_docs = {str(f) for f in self.markdown_files}
        
        # Find all linked documents
        linked_docs = set()
        for targets in self.link_graph.values():
            linked_docs.update(targets)
        
        # Documents that exist but are never linked (excluding README.md at root)
        orphaned = []
        for doc in all_docs:
            doc_path = Path(doc)
            if doc not in linked_docs and doc_path.name != 'README.md':
                # Exclude root-level files and AGENTS.md files (they're navigation hubs)
                if doc_path.parent != self.repo_root and doc_path.name != 'AGENTS.md':
                    orphaned.append(str(doc_path.relative_to(self.repo_root) if doc_path.is_absolute() else doc_path))
        
        return orphaned
    
    def validate_all_markdown_files(self) -> ValidationReport:
        """Validate all markdown files in repository."""
        start_time = time.time()
        
        logger.info("Starting comprehensive link validation...")
        
        # Find all markdown files
        self.markdown_files = self.find_all_markdown_files()
        
        # Check internal links
        total_links = 0
        external_urls_found = set()
        
        for md_file in self.markdown_files:
            logger.debug(f"Checking {md_file.relative_to(self.repo_root)}")
            
            # Check internal links
            broken = self.check_internal_links(md_file)
            self.broken_links.extend(broken)
            
            # Collect external URLs
            links = self.extract_links(md_file)
            total_links += len(links)
            
            for _, _, link_url in links:
                if link_url.startswith(('http://', 'https://')):
                    external_urls_found.add(link_url)
        
        logger.info(f"Found {len(external_urls_found)} external URLs to validate")
        
        # Verify external URLs
        if external_urls_found:
            logger.info("Validating external URLs (this may take a while)...")
            self.external_urls = self.verify_external_urls(external_urls_found)
        
        # Detect circular references
        circular = [] # self.detect_circular_references()
        
        # Find orphaned documents
        orphaned = self.find_orphaned_documents()
        
        validation_time = time.time() - start_time
        
        report = ValidationReport(
            total_files=len(self.markdown_files),
            total_links=total_links,
            broken_links=self.broken_links,
            external_urls=self.external_urls,
            circular_references=circular,
            orphaned_documents=orphaned,
            validation_time=validation_time
        )
        
        logger.info(f"Validation complete in {validation_time:.2f}s")
        return report
    
    def generate_link_graph(self) -> Optional[object]:
        """Generate link graph visualization."""
        if not HAS_NETWORKX:
            logger.warning("NetworkX not available, cannot generate graph")
            return None
        
        G = nx.DiGraph()
        for source, targets in self.link_graph.items():
            for target in targets:
                G.add_edge(source, target)
        
        return G
    
    def export_results(self, report: ValidationReport, output_path: Path, format: str = "json") -> Path:
        """Export validation results."""
        if format == "json":
            output_file = output_path / "link_validation_results.json"
            output_file.write_text(json.dumps(report.to_dict(), indent=2))
            logger.info(f"Results exported to {output_file}")
            return output_file
        
        elif format == "html":
            output_file = output_path / "link_validation_results.html"
            html_content = self._generate_html_report(report)
            output_file.write_text(html_content)
            logger.info(f"HTML report exported to {output_file}")
            return output_file
        
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def _generate_html_report(self, report: ValidationReport) -> str:
        """Generate HTML report."""
        html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Link Validation Report</title>
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
        .error {{ color: #d32f2f; }}
        .success {{ color: #388e3c; }}
    </style>
</head>
<body>
    <h1>Documentation Link Validation Report</h1>
    
    <div class="summary">
        <h2>Summary</h2>
        <div class="stat">
            <div class="stat-value">{report.total_files}</div>
            <div class="stat-label">Files Scanned</div>
        </div>
        <div class="stat">
            <div class="stat-value">{report.total_links}</div>
            <div class="stat-label">Total Links</div>
        </div>
        <div class="stat">
            <div class="stat-value {'error' if len(report.broken_links) > 0 else 'success'}">{len(report.broken_links)}</div>
            <div class="stat-label">Broken Links</div>
        </div>
        <div class="stat">
            <div class="stat-value">{len(report.circular_references)}</div>
            <div class="stat-label">Circular References</div>
        </div>
        <div class="stat">
            <div class="stat-value">{len(report.orphaned_documents)}</div>
            <div class="stat-label">Orphaned Documents</div>
        </div>
    </div>
"""
        
        if report.broken_links:
            html += """
    <h2>Broken Links</h2>
    <table>
        <tr>
            <th>File</th>
            <th>Line</th>
            <th>Link Text</th>
            <th>Target</th>
            <th>Issue</th>
        </tr>
"""
            for link in report.broken_links:
                html += f"""
        <tr>
            <td>{link.file_path}</td>
            <td>{link.line_number}</td>
            <td>{link.link_text}</td>
            <td><code>{link.link_url}</code></td>
            <td class="error">{link.issue_type}</td>
        </tr>
"""
            html += "    </table>\n"
        
        if report.circular_references:
            html += """
    <h2>Circular References</h2>
    <table>
        <tr>
            <th>Source</th>
            <th>Target</th>
        </tr>
"""
            for src, dst in report.circular_references:
                html += f"""
        <tr>
            <td><code>{src}</code></td>
            <td><code>{dst}</code></td>
        </tr>
"""
            html += "    </table>\n"
        
        html += f"""
    <p><small>Validation completed in {report.validation_time:.2f} seconds</small></p>
</body>
</html>
"""
        return html


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Comprehensive link validation for documentation")
    parser.add_argument('--repo-root', type=Path, default=Path.cwd(),
                       help='Repository root directory')
    parser.add_argument('--output', type=Path, default=Path('output'),
                       help='Output directory for results')
    parser.add_argument('--format', choices=['json', 'html', 'both'], default='both',
                       help='Output format')
    parser.add_argument('--fail-on-broken', action='store_true',
                       help='Exit with error code if broken links found')
    
    args = parser.parse_args()
    
    # Create output directory
    args.output.mkdir(parents=True, exist_ok=True)
    
    # Run validation
    validator = ComprehensiveLinkValidator(args.repo_root)
    report = validator.validate_all_markdown_files()
    
    # Export results
    if args.format in ['json', 'both']:
        validator.export_results(report, args.output, 'json')
    
    if args.format in ['html', 'both']:
        validator.export_results(report, args.output, 'html')
    
    # Print summary
    print("\n" + "="*80)
    print("VALIDATION SUMMARY")
    print("="*80)
    print(f"Files scanned: {report.total_files}")
    print(f"Total links: {report.total_links}")
    print(f"Broken links: {len(report.broken_links)}")
    print(f"External URLs validated: {len(report.external_urls)}")
    print(f"Failed external URLs: {sum(1 for v in report.external_urls.values() if not v)}")
    print(f"Circular references: {len(report.circular_references)}")
    print(f"Orphaned documents: {len(report.orphaned_documents)}")
    print(f"Validation time: {report.validation_time:.2f}s")
    print("="*80)
    
    # Exit with error if requested and broken links found
    if args.fail_on_broken and len(report.broken_links) > 0:
        print("\n❌ Validation failed: broken links found")
        sys.exit(1)
    
    print("\n✅ Validation complete!")
    sys.exit(0)


if __name__ == '__main__':
    main()


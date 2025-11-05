#!/usr/bin/env python3
"""
Comprehensive Documentation and Signposting Audit Script

This script performs a complete audit of documentation across the Codomyrmex repository,
checking for:
- Missing README.md and AGENTS.md files
- Broken internal links
- Duplicate content
- Examples migration references
- AGENTS.md structure consistency
- Navigation and cross-reference issues
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional
from collections import defaultdict
import sys


class DocumentationAudit:
    def __init__(self, repo_root: Path):
        self.repo_root = repo_root.resolve()
        self.issues = {
            'missing_readme': [],
            'missing_agents': [],
            'broken_links': [],
            'duplicate_content': [],
            'examples_migration': [],
            'agents_structure': [],
            'navigation_issues': [],
            'cross_reference_issues': []
        }
        
    def scan_structure(self):
        """Scan for missing README.md and AGENTS.md files in expected locations."""
        print("📁 Scanning repository structure...")
        
        # Directories that should have README.md
        expected_readme_dirs = {
            'docs',
            'docs/getting-started',
            'docs/getting-started/tutorials',
            'docs/development',
            'docs/modules',
            'docs/integration',
            'docs/project',
            'docs/reference',
            'docs/deployment',
            'scripts',
            'src',
            'src/codomyrmex',
            'testing',
            'projects',
            'examples',
            'tools',
            'config',
            'output'
        }
        
        # Directories that should have both README.md and AGENTS.md
        expected_agents_dirs = {
            'docs',
            'docs/getting-started',
            'docs/getting-started/tutorials',
            'docs/development',
            'docs/modules',
            'docs/integration',
            'docs/project',
            'docs/reference',
            'docs/deployment',
            'scripts',
            'src',
            'testing',
            'projects'
        }
        
        # Check for missing README.md
        for dir_path in expected_readme_dirs:
            full_path = self.repo_root / dir_path
            if full_path.exists() and full_path.is_dir():
                readme_path = full_path / 'README.md'
                if not readme_path.exists():
                    self.issues['missing_readme'].append(dir_path)
        
        # Check for missing AGENTS.md
        for dir_path in expected_agents_dirs:
            full_path = self.repo_root / dir_path
            if full_path.exists() and full_path.is_dir():
                agents_path = full_path / 'AGENTS.md'
                if not agents_path.exists():
                    self.issues['missing_agents'].append(dir_path)
    
    def validate_links(self):
        """Validate all markdown links in documentation."""
        print("🔗 Validating links...")
        
        def find_markdown_files(root: Path) -> List[Path]:
            """Find all markdown files."""
            markdown_files = []
            for path in root.rglob('*.md'):
                # Skip hidden directories and common ignore patterns
                if any(part.startswith('.') for part in path.parts):
                    continue
                if 'node_modules' in path.parts or '__pycache__' in path.parts:
                    continue
                markdown_files.append(path)
            return markdown_files
        
        def extract_links(content: str) -> List[Tuple[str, int, str]]:
            """Extract markdown links from content."""
            links = []
            link_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
            for line_num, line in enumerate(content.split('\n'), start=1):
                for match in re.finditer(link_pattern, line):
                    link_text = match.group(1)
                    link_url = match.group(2)
                    # Remove title if present
                    if link_url.startswith('"') and link_url.endswith('"'):
                        link_url = link_url[1:-1]
                    links.append((link_text, line_num, link_url))
            return links
        
        def resolve_link(link_url: str, from_file: Path) -> Tuple[bool, Optional[Path]]:
            """Resolve a link and check if it exists."""
            # Skip external links
            if link_url.startswith(('http://', 'https://', 'mailto:')):
                return (True, None)
            
            # Skip anchor-only links
            if link_url.startswith('#'):
                return (True, None)
            
            # Remove anchor
            if '#' in link_url:
                link_url = link_url.split('#')[0]
            
            # Handle relative paths
            if link_url.startswith('./'):
                link_url = link_url[2:]
            
            # Resolve relative to file
            if link_url.startswith('../'):
                levels_up = link_url.count('../')
                current_dir = from_file.parent
                for _ in range(levels_up):
                    if current_dir == self.repo_root:
                        break
                    current_dir = current_dir.parent
                link_url = link_url.lstrip('../')
                resolved = current_dir / link_url
            elif link_url.startswith('/'):
                resolved = self.repo_root / link_url.lstrip('/')
            else:
                resolved = from_file.parent / link_url
            
            # Check if exists
            if resolved.exists():
                return (True, resolved)
            
            # Check if directory exists (for links to directories)
            if resolved.suffix == '':
                if (self.repo_root / link_url).exists():
                    return (True, self.repo_root / link_url)
            
            return (False, resolved)
        
        markdown_files = find_markdown_files(self.repo_root)
        for file_path in markdown_files:
            try:
                content = file_path.read_text(encoding='utf-8')
                links = extract_links(content)
                
                for link_text, line_num, link_url in links:
                    exists, resolved = resolve_link(link_url, file_path)
                    if not exists:
                        rel_path = file_path.relative_to(self.repo_root)
                        self.issues['broken_links'].append({
                            'file': str(rel_path),
                            'line': line_num,
                            'text': link_text,
                            'url': link_url,
                            'resolved': str(resolved) if resolved else 'unknown'
                        })
            except Exception as e:
                rel_path = file_path.relative_to(self.repo_root)
                self.issues['broken_links'].append({
                    'file': str(rel_path),
                    'line': 0,
                    'text': '',
                    'url': '',
                    'resolved': f'error: {str(e)}'
                })
    
    def find_duplicates(self):
        """Find duplicate content sections."""
        print("🔄 Finding duplicate content...")
        
        # Check README.md for known duplicates
        readme_path = self.repo_root / 'README.md'
        if readme_path.exists():
            content = readme_path.read_text(encoding='utf-8')
            lines = content.split('\n')
            
            # Check for duplicate "What's Working Now" sections
            working_now_sections = []
            for i, line in enumerate(lines, 1):
                if 'What\'s Working Now' in line or '✅ What\'s Working Now' in line:
                    working_now_sections.append(i)
            
            if len(working_now_sections) > 1:
                self.issues['duplicate_content'].append({
                    'file': 'README.md',
                    'issue': 'Multiple "What\'s Working Now" sections',
                    'lines': working_now_sections
                })
            
            # Check for duplicate "Recent Enhancements" sections
            enhancements_sections = []
            for i, line in enumerate(lines, 1):
                if 'Recent Enhancements' in line or '🔄 Recent Enhancements' in line:
                    enhancements_sections.append(i)
            
            if len(enhancements_sections) > 1:
                self.issues['duplicate_content'].append({
                    'file': 'README.md',
                    'issue': 'Multiple "Recent Enhancements" sections',
                    'lines': enhancements_sections
                })
    
    def check_examples_migration(self):
        """Check for references to old examples/ paths."""
        print("📦 Checking examples migration...")
        
        def find_markdown_files(root: Path) -> List[Path]:
            """Find all markdown files."""
            markdown_files = []
            for path in root.rglob('*.md'):
                if any(part.startswith('.') for part in path.parts):
                    continue
                if 'node_modules' in path.parts or '__pycache__' in path.parts:
                    continue
                markdown_files.append(path)
            return markdown_files
        
        old_patterns = [
            r'\]\(examples/',
            r'\]\(\./examples/',
            r'\]\(\.\./examples/',
            r'\]\(\.\./\.\./examples/',
            r'\]\(\.\./\.\./\.\./examples/',
            r'\]\(/examples/',
        ]
        
        markdown_files = find_markdown_files(self.repo_root)
        for file_path in markdown_files:
            try:
                content = file_path.read_text(encoding='utf-8')
                for line_num, line in enumerate(content.split('\n'), start=1):
                    for pattern in old_patterns:
                        if re.search(pattern, line):
                            rel_path = file_path.relative_to(self.repo_root)
                            self.issues['examples_migration'].append({
                                'file': str(rel_path),
                                'line': line_num,
                                'content': line.strip()
                            })
            except Exception:
                pass
    
    def audit_agents_structure(self):
        """Audit AGENTS.md files for consistent structure."""
        print("🤖 Auditing AGENTS.md structure...")
        
        def find_agents_files(root: Path) -> List[Path]:
            """Find all AGENTS.md files."""
            agents_files = []
            for path in root.rglob('AGENTS.md'):
                if any(part.startswith('.') for part in path.parts):
                    continue
                if 'node_modules' in path.parts or '__pycache__' in path.parts:
                    continue
                agents_files.append(path)
            return agents_files
        
        required_sections = ['Purpose', 'Active Components', 'Operating Contracts']
        agents_files = find_agents_files(self.repo_root)
        
        for agents_path in agents_files:
            try:
                content = agents_path.read_text(encoding='utf-8')
                rel_path = agents_path.relative_to(self.repo_root)
                
                # Check for required sections
                missing_sections = []
                for section in required_sections:
                    if f'## {section}' not in content and f'# {section}' not in content:
                        missing_sections.append(section)
                
                if missing_sections:
                    self.issues['agents_structure'].append({
                        'file': str(rel_path),
                        'issue': f'Missing sections: {", ".join(missing_sections)}'
                    })
                
                # Check for navigation links
                if 'Navigation Links' not in content and 'navigation' not in content.lower():
                    # This is optional but recommended
                    pass
                    
            except Exception as e:
                rel_path = agents_path.relative_to(self.repo_root)
                self.issues['agents_structure'].append({
                    'file': str(rel_path),
                    'issue': f'Error reading file: {str(e)}'
                })
    
    def validate_navigation(self):
        """Validate navigation diagrams and user journey maps."""
        print("🧭 Validating navigation...")
        
        # Check if files referenced in navigation diagrams exist
        readme_path = self.repo_root / 'README.md'
        docs_readme_path = self.repo_root / 'docs' / 'README.md'
        
        for file_path in [readme_path, docs_readme_path]:
            if not file_path.exists():
                continue
            
            try:
                content = file_path.read_text(encoding='utf-8')
                
                # Extract links from markdown
                link_pattern = r'\]\(([^)]+)\)'
                links = re.findall(link_pattern, content)
                
                for link in links:
                    # Skip external links
                    if link.startswith(('http://', 'https://', 'mailto:')):
                        continue
                    
                    # Remove anchor
                    if '#' in link:
                        link = link.split('#')[0]
                    
                    # Resolve path
                    if link.startswith('./'):
                        link = link[2:]
                    
                    if link.startswith('../'):
                        # Relative to docs/README.md
                        levels_up = link.count('../')
                        base_dir = file_path.parent
                        for _ in range(levels_up):
                            base_dir = base_dir.parent
                        resolved = base_dir / link.lstrip('../')
                    elif link.startswith('/'):
                        resolved = self.repo_root / link.lstrip('/')
                    else:
                        resolved = file_path.parent / link
                    
                    if not resolved.exists():
                        rel_path = file_path.relative_to(self.repo_root)
                        self.issues['navigation_issues'].append({
                            'file': str(rel_path),
                            'broken_link': link,
                            'resolved': str(resolved)
                        })
            except Exception as e:
                rel_path = file_path.relative_to(self.repo_root)
                self.issues['navigation_issues'].append({
                    'file': str(rel_path),
                    'broken_link': 'unknown',
                    'resolved': f'error: {str(e)}'
                })
    
    def check_cross_references(self):
        """Check cross-references between documentation areas."""
        print("🔗 Checking cross-references...")
        
        # Check if docs/README.md references exist in src/ and scripts/
        docs_readme = self.repo_root / 'docs' / 'README.md'
        if docs_readme.exists():
            content = docs_readme.read_text(encoding='utf-8')
            
            # Find references to src/ or scripts/
            src_pattern = r'\]\(([^)]*src/[^)]+)\)'
            scripts_pattern = r'\]\(([^)]*scripts/[^)]+)\)'
            
            for pattern in [src_pattern, scripts_pattern]:
                matches = re.findall(pattern, content)
                for match in matches:
                    # Clean up the link
                    link = match.strip()
                    if link.startswith('./'):
                        link = link[2:]
                    if link.startswith('../'):
                        link = link.lstrip('../')
                    
                    resolved = self.repo_root / link
                    if not resolved.exists():
                        self.issues['cross_reference_issues'].append({
                            'file': 'docs/README.md',
                            'broken_reference': match,
                            'resolved': str(resolved)
                        })
    
    def run_all_checks(self):
        """Run all audit checks."""
        print("=" * 80)
        print("📚 Comprehensive Documentation Audit")
        print("=" * 80)
        print()
        
        self.scan_structure()
        self.validate_links()
        self.find_duplicates()
        self.check_examples_migration()
        self.audit_agents_structure()
        self.validate_navigation()
        self.check_cross_references()
        
        print()
        print("=" * 80)
        print("✅ Audit complete!")
        print("=" * 80)
    
    def generate_report(self) -> str:
        """Generate a comprehensive audit report."""
        report = []
        report.append("# Documentation and Signposting Audit Report\n")
        report.append(f"Generated: {Path(__file__).name}\n")
        report.append("=" * 80)
        report.append("\n")
        
        # Summary
        total_issues = sum(len(issues) for issues in self.issues.values())
        report.append("## Summary\n")
        report.append(f"**Total Issues Found**: {total_issues}\n")
        report.append("\n### Issue Breakdown\n")
        for category, issues in self.issues.items():
            if issues:
                report.append(f"- **{category.replace('_', ' ').title()}**: {len(issues)}\n")
        report.append("\n")
        
        # Detailed findings
        if self.issues['missing_readme']:
            report.append("## Missing README.md Files\n")
            for dir_path in self.issues['missing_readme']:
                report.append(f"- `{dir_path}/README.md`\n")
            report.append("\n")
        
        if self.issues['missing_agents']:
            report.append("## Missing AGENTS.md Files\n")
            for dir_path in self.issues['missing_agents']:
                report.append(f"- `{dir_path}/AGENTS.md`\n")
            report.append("\n")
        
        if self.issues['broken_links']:
            report.append("## Broken Links\n")
            for issue in self.issues['broken_links'][:50]:  # Limit to first 50
                report.append(f"- **{issue['file']}** (line {issue['line']}): `{issue['url']}`\n")
                report.append(f"  - Resolved to: `{issue['resolved']}`\n")
            if len(self.issues['broken_links']) > 50:
                report.append(f"\n*... and {len(self.issues['broken_links']) - 50} more broken links*\n")
            report.append("\n")
        
        if self.issues['duplicate_content']:
            report.append("## Duplicate Content\n")
            for issue in self.issues['duplicate_content']:
                report.append(f"- **{issue['file']}**: {issue['issue']}\n")
                report.append(f"  - Lines: {issue['lines']}\n")
            report.append("\n")
        
        if self.issues['examples_migration']:
            report.append("## Examples Migration Issues\n")
            report.append("Found references to old `examples/` paths that should be updated to `scripts/examples/`:\n")
            for issue in self.issues['examples_migration'][:30]:  # Limit to first 30
                report.append(f"- **{issue['file']}** (line {issue['line']}):\n")
                report.append(f"  ```\n  {issue['content'][:100]}...\n  ```\n")
            if len(self.issues['examples_migration']) > 30:
                report.append(f"\n*... and {len(self.issues['examples_migration']) - 30} more examples migration issues*\n")
            report.append("\n")
        
        if self.issues['agents_structure']:
            report.append("## AGENTS.md Structure Issues\n")
            for issue in self.issues['agents_structure']:
                report.append(f"- **{issue['file']}**: {issue['issue']}\n")
            report.append("\n")
        
        if self.issues['navigation_issues']:
            report.append("## Navigation Issues\n")
            for issue in self.issues['navigation_issues'][:30]:  # Limit to first 30
                report.append(f"- **{issue['file']}**: Broken link `{issue['broken_link']}`\n")
                report.append(f"  - Resolved to: `{issue['resolved']}`\n")
            if len(self.issues['navigation_issues']) > 30:
                report.append(f"\n*... and {len(self.issues['navigation_issues']) - 30} more navigation issues*\n")
            report.append("\n")
        
        if self.issues['cross_reference_issues']:
            report.append("## Cross-Reference Issues\n")
            for issue in self.issues['cross_reference_issues']:
                report.append(f"- **{issue['file']}**: Broken reference `{issue['broken_reference']}`\n")
                report.append(f"  - Resolved to: `{issue['resolved']}`\n")
            report.append("\n")
        
        # Recommendations
        report.append("## Recommendations\n")
        if total_issues > 0:
            report.append("1. Fix all broken links identified above\n")
            report.append("2. Remove duplicate content sections\n")
            report.append("3. Update examples migration references\n")
            report.append("4. Standardize AGENTS.md structure across all files\n")
            report.append("5. Add missing README.md and AGENTS.md files\n")
        else:
            report.append("✅ No issues found! Documentation is in excellent shape.\n")
        
        report.append("\n")
        report.append("=" * 80)
        
        return ''.join(report)


def main():
    """Main function."""
    script_dir = Path(__file__).parent
    repo_root = script_dir.parent.parent
    
    audit = DocumentationAudit(repo_root)
    audit.run_all_checks()
    
    # Generate report
    report = audit.generate_report()
    
    # Print summary
    print("\n" + report)
    
    # Save report
    report_path = repo_root / 'docs' / 'project' / 'documentation-audit-report.md'
    report_path.write_text(report, encoding='utf-8')
    print(f"\n📄 Full report saved to: {report_path.relative_to(repo_root)}")
    
    # Return exit code
    total_issues = sum(len(issues) for issues in audit.issues.values())
    return 1 if total_issues > 0 else 0


if __name__ == '__main__':
    sys.exit(main())


from collections import defaultdict
from datetime import datetime
from pathlib import Path
import os
import re


from codomyrmex.logging_monitoring import get_logger






























#!/usr/bin/env python3
"""Generate comprehensive documentation verification report."""


"""Main entry point and utility functions

This module provides generate_doc_verification_report functionality including:
- 3 functions: analyze_all_docs, generate_report, main
- 0 classes: 

Usage:
    # Example usage here
"""
logger = get_logger(__name__)
def analyze_all_docs(base_path: Path) -> dict:
    """Analyze all documentation files."""
    results = {
        'total_files': 0,
        'files_checked': 0,
        'broken_links': [],
        'missing_navigation': [],
        'missing_version': [],
        'missing_status': [],
        'placeholder_content': [],
        'summary': {}
    }
    
    doc_files = []
    for root, dirs, files in os.walk(base_path):
        dirs[:] = [d for d in dirs if not d.startswith('.') and 
                   d not in ['__pycache__', 'node_modules', 'venv', '.venv', '.git', '@output']]
        
        for file in files:
            if file in ['README.md', 'AGENTS.md', 'SPEC.md']:
                file_path = Path(root) / file
                doc_files.append(file_path)
    
    results['total_files'] = len(doc_files)
    
    for file_path in doc_files:
        results['files_checked'] += 1
        rel_path = str(file_path.relative_to(base_path))
        
        try:
            content = file_path.read_text(encoding='utf-8')
            
            # Check version
            if "**Version**" not in content and "Version" not in content:
                results['missing_version'].append(rel_path)
            
            # Check status
            if "**Status**" not in content and "Status" not in content:
                results['missing_status'].append(rel_path)
            
            # Check navigation
            file_name = file_path.name
            if file_name == "README.md":
                if "AGENTS.md" not in content and "AGENTS" not in content:
                    results['missing_navigation'].append(f"{rel_path}: missing AGENTS.md reference")
            elif file_name == "AGENTS.md":
                if "README.md" not in content and "README" not in content:
                    results['missing_navigation'].append(f"{rel_path}: missing README.md reference")
            elif file_name == "SPEC.md":
                if "README.md" not in content and "README" not in content:
                    results['missing_navigation'].append(f"{rel_path}: missing README.md reference")
            
            # Check placeholder content
            placeholders = [
                "[Architecture description if applicable]",
                "[Functional requirements for",
                "[Testing, documentation, performance, security requirements]",
                "[APIs, data structures, communication patterns]",
                "[How to implement within this directory]"
            ]
            for placeholder in placeholders:
                if placeholder in content:
                    results['placeholder_content'].append(f"{rel_path}: {placeholder}")
                    break
            
            # Check links
            link_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
            for match in re.finditer(link_pattern, content):
                link_url = match.group(2)
                if link_url.startswith(('http://', 'https://', 'mailto:', '#')):
                    continue
                
                # Resolve path
                clean_url = link_url.split('#')[0]
                if clean_url.startswith('./'):
                    clean_url = clean_url[2:]
                
                if clean_url.startswith('../'):
                    levels_up = clean_url.count('../')
                    base_dir = file_path.parent
                    for _ in range(levels_up):
                        base_dir = base_dir.parent
                    resolved = base_dir / clean_url.lstrip('../')
                elif clean_url.startswith('/'):
                    resolved = base_path / clean_url.lstrip('/')
                else:
                    resolved = file_path.parent / clean_url
                
                if not resolved.exists():
                    results['broken_links'].append({
                        'file': rel_path,
                        'text': match.group(1),
                        'url': link_url,
                        'resolved': str(resolved)
                    })
        except Exception as e:
            results['broken_links'].append({
                'file': rel_path,
                'error': str(e)
            })
    
    # Generate summary
    results['summary'] = {
        'total_files': results['total_files'],
        'broken_links_count': len(results['broken_links']),
        'missing_navigation_count': len(results['missing_navigation']),
        'missing_version_count': len(results['missing_version']),
        'missing_status_count': len(results['missing_status']),
        'placeholder_content_count': len(results['placeholder_content'])
    }
    
    return results

def generate_report(results: dict, output_path: Path):
    """Generate markdown report."""
    report = f"""# Documentation Verification Report

**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Summary

- **Total Files Checked**: {results['summary']['total_files']}
- **Broken Links**: {results['summary']['broken_links_count']}
- **Missing Navigation**: {results['summary']['missing_navigation_count']}
- **Missing Version**: {results['summary']['missing_version_count']}
- **Missing Status**: {results['summary']['missing_status_count']}
- **Placeholder Content**: {results['summary']['placeholder_content_count']}

## Broken Links

"""
    
    if results['broken_links']:
        for link in results['broken_links'][:50]:  # Limit to first 50
            report += f"- **{link['file']}**: `{link.get('text', 'N/A')}` -> `{link.get('url', 'N/A')}`\n"
        if len(results['broken_links']) > 50:
            report += f"\n... and {len(results['broken_links']) - 50} more broken links\n"
    else:
        report += "No broken links found.\n"
    
    report += "\n## Missing Navigation\n\n"
    if results['missing_navigation']:
        for nav in results['missing_navigation'][:30]:
            report += f"- {nav}\n"
        if len(results['missing_navigation']) > 30:
            report += f"\n... and {len(results['missing_navigation']) - 30} more\n"
    else:
        report += "All files have proper navigation links.\n"
    
    report += "\n## Missing Version/Status\n\n"
    if results['missing_version']:
        report += f"**Missing Version**: {len(results['missing_version'])} files\n"
    if results['missing_status']:
        report += f"**Missing Status**: {len(results['missing_status'])} files\n"
    
    report += "\n## Placeholder Content\n\n"
    if results['placeholder_content']:
        for placeholder in results['placeholder_content'][:20]:
            report += f"- {placeholder}\n"
    else:
        report += "No placeholder content found.\n"
    
    output_path.write_text(report, encoding='utf-8')
    print(f"Report generated: {output_path}")

def main():
    """Generate comprehensive report."""
    base_path = Path("/Users/mini/Documents/GitHub/codomyrmex")
    results = analyze_all_docs(base_path)
    
    report_path = base_path / "output" / "documentation_verification_report.md"
    report_path.parent.mkdir(exist_ok=True)
    generate_report(results, report_path)
    
    print(f"\n=== VERIFICATION SUMMARY ===")
    print(f"Total files: {results['summary']['total_files']}")
    print(f"Broken links: {results['summary']['broken_links_count']}")
    print(f"Missing navigation: {results['summary']['missing_navigation_count']}")
    print(f"Missing version: {results['summary']['missing_version_count']}")
    print(f"Missing status: {results['summary']['missing_status_count']}")
    print(f"Placeholder content: {results['summary']['placeholder_content_count']}")

if __name__ == "__main__":
    main()


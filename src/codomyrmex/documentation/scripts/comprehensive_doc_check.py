from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Tuple
import os
import re


from codomyrmex.logging_monitoring import get_logger






























#!/usr/bin/env python3
"""Comprehensive documentation verification script."""


"""Main entry point and utility functions

This module provides comprehensive_doc_check functionality including:
- 6 functions: check_placeholder_content, check_navigation_links, check_version_status...
- 0 classes: 

Usage:
    # Example usage here
"""
logger = get_logger(__name__)
def check_placeholder_content(content: str) -> List[str]:
    """Check for placeholder content."""
    issues = []
    placeholders = [
        "[Architecture description if applicable]",
        "[Functional requirements for",
        "[Testing, documentation, performance, security requirements]",
        "[APIs, data structures, communication patterns]",
        "[How to implement within this directory]",
        "## Purpose\n\n## Overview",
        "## Purpose\n\n\n## Overview"
    ]
    for placeholder in placeholders:
        if placeholder in content:
            issues.append(f"Placeholder content found: {placeholder}")
    return issues

def check_navigation_links(content: str, file_path: Path, base_path: Path) -> List[str]:
    """Check navigation link completeness."""
    issues = []
    file_name = file_path.name
    
    # Check for cross-references to sibling files
    if file_name == "README.md":
        if "AGENTS.md" not in content and "AGENTS" not in content:
            issues.append("Missing reference to AGENTS.md")
        if "SPEC.md" not in content and "SPEC" not in content:
            issues.append("Missing reference to SPEC.md")
    elif file_name == "AGENTS.md":
        if "README.md" not in content and "README" not in content:
            issues.append("Missing reference to README.md")
        if "SPEC.md" not in content and "SPEC" not in content:
            issues.append("Missing reference to SPEC.md")
    elif file_name == "SPEC.md":
        if "README.md" not in content and "README" not in content:
            issues.append("Missing reference to README.md")
        if "AGENTS.md" not in content and "AGENTS" not in content:
            issues.append("Missing reference to AGENTS.md")
    
    # Check for Navigation section
    if "## Navigation" not in content and "## Navigation Links" not in content:
        issues.append("Missing Navigation section")
    
    return issues

def check_version_status(content: str) -> List[str]:
    """Check for version and status information."""
    issues = []
    if "**Version**" not in content and "Version" not in content:
        issues.append("Missing version information")
    if "**Status**" not in content and "Status" not in content:
        issues.append("Missing status information")
    return issues

def verify_relative_path(link_url: str, from_file: Path, base_path: Path) -> Tuple[bool, str]:
    """Verify if a relative path is correct."""
    if link_url.startswith(('http://', 'https://', 'mailto:', '#')):
        return (True, "")  # External links and anchors are OK
    
    # Remove anchor
    clean_url = link_url.split('#')[0]
    if not clean_url:
        return (True, "")
    
    # Resolve path
    if clean_url.startswith('./'):
        clean_url = clean_url[2:]
    
    if clean_url.startswith('../'):
        levels_up = clean_url.count('../')
        base_dir = from_file.parent
        for _ in range(levels_up):
            base_dir = base_dir.parent
        resolved = base_dir / clean_url.lstrip('../')
    elif clean_url.startswith('/'):
        resolved = base_path / clean_url.lstrip('/')
    else:
        resolved = from_file.parent / clean_url
    
    exists = resolved.exists()
    if not exists:
        return (False, f"Path does not exist: {resolved}")
    
    return (True, "")

def analyze_file(file_path: Path, base_path: Path) -> Dict:
    """Analyze a single documentation file."""
    if not file_path.exists():
        return None
    
    try:
        content = file_path.read_text(encoding='utf-8')
        rel_path = str(file_path.relative_to(base_path))
        
        result = {
            'path': rel_path,
            'issues': [],
            'broken_links': [],
            'placeholder_content': [],
            'navigation_issues': [],
            'structure_issues': []
        }
        
        # Check placeholder content
        result['placeholder_content'] = check_placeholder_content(content)
        
        # Check navigation
        result['navigation_issues'] = check_navigation_links(content, file_path, base_path)
        
        # Check version/status
        result['structure_issues'].extend(check_version_status(content))
        
        # Check links
        link_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
        matches = re.finditer(link_pattern, content)
        
        for match in matches:
            link_text = match.group(1)
            link_url = match.group(2)
            is_valid, error = verify_relative_path(link_url, file_path, base_path)
            if not is_valid:
                result['broken_links'].append({
                    'text': link_text,
                    'url': link_url,
                    'error': error
                })
        
        # Only return if there are issues
        if (result['broken_links'] or result['placeholder_content'] or 
            result['navigation_issues'] or result['structure_issues']):
            return result
        return None
    except Exception as e:
        return {
            'path': str(file_path.relative_to(base_path)),
            'error': str(e)
        }

def main():
    """Run comprehensive documentation check."""
    base_path = Path("/Users/mini/Documents/GitHub/codomyrmex")
    
    doc_files = []
    for root, dirs, files in os.walk(base_path):
        dirs[:] = [d for d in dirs if not d.startswith('.') and 
                   d not in ['__pycache__', 'node_modules', 'venv', '.venv', '.git', '@output']]
        
        for file in files:
            if file in ['README.md', 'AGENTS.md', 'SPEC.md']:
                file_path = Path(root) / file
                doc_files.append(file_path)
    
    print(f"Checking {len(doc_files)} documentation files...\n")
    
    results = []
    for file_path in doc_files:
        result = analyze_file(file_path, base_path)
        if result:
            results.append(result)
    
    # Categorize issues
    broken_links_count = sum(len(r.get('broken_links', [])) for r in results)
    placeholder_count = sum(len(r.get('placeholder_content', [])) for r in results)
    navigation_count = sum(len(r.get('navigation_issues', [])) for r in results)
    structure_count = sum(len(r.get('structure_issues', [])) for r in results)
    
    print(f"\n=== SUMMARY ===")
    print(f"Files with issues: {len(results)}")
    print(f"Total broken links: {broken_links_count}")
    print(f"Files with placeholder content: {placeholder_count}")
    print(f"Files with navigation issues: {navigation_count}")
    print(f"Files with structure issues: {structure_count}")
    
    # Show top issues
    print(f"\n=== TOP ISSUES ===")
    for result in sorted(results, key=lambda x: len(x.get('broken_links', [])), reverse=True)[:20]:
        print(f"\n{result['path']}:")
        if result.get('broken_links'):
            print(f"  Broken links: {len(result['broken_links'])}")
            for link in result['broken_links'][:3]:
                print(f"    - {link['text']} -> {link['url']}")
        if result.get('placeholder_content'):
            print(f"  Placeholder content: {result['placeholder_content']}")
        if result.get('navigation_issues'):
            print(f"  Navigation issues: {result['navigation_issues']}")
        if result.get('structure_issues'):
            print(f"  Structure issues: {result['structure_issues']}")

if __name__ == "__main__":
    main()


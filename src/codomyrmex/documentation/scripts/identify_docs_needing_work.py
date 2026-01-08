from pathlib import Path
from typing import List, Dict
import os
import re




#!/usr/bin/env python3
"""Identify documentation files needing improvement."""


def check_placeholder_content(content: str) -> bool:
    """Check if content has placeholder text."""
    placeholders = [
        "[Architecture description if applicable]",
        "[Functional requirements for",
        "[Testing, documentation, performance, security requirements]",
        "[APIs, data structures, communication patterns]",
        "[How to implement within this directory]",
        "## Purpose\n\n## Overview",
        "## Purpose\n\n\n## Overview"
    ]
    return any(placeholder in content for placeholder in placeholders)

def check_broken_links(content: str, file_path: Path) -> List[str]:
    """Check for broken relative links."""
    base_path = Path("/Users/mini/Documents/GitHub/codomyrmex")
    broken = []
    
    # Find all markdown links
    pattern = r'\[([^\]]+)\]\(([^\)]+)\)'
    matches = re.findall(pattern, content)
    
    for link_text, link_path in matches:
        if link_path.startswith('http') or link_path.startswith('#'):
            continue
        
        try:
            target = (file_path.parent / link_path).resolve()
            if not target.exists():
                broken.append(f"{link_text} -> {link_path}")
        except Exception:
            broken.append(f"{link_text} -> {link_path}")
    
    return broken

def analyze_directory(dir_path: Path) -> Dict:
    """Analyze a directory's documentation."""
    result = {
        'path': str(dir_path.relative_to(Path("/Users/mini/Documents/GitHub/codomyrmex"))),
        'readme_issues': [],
        'agents_issues': [],
        'spec_issues': []
    }
    
    readme = dir_path / "README.md"
    agents = dir_path / "AGENTS.md"
    spec = dir_path / "SPEC.md"
    
    if readme.exists():
        content = readme.read_text(encoding='utf-8')
        broken = check_broken_links(content, readme)
        if broken:
            result['readme_issues'].append(f"Broken links: {', '.join(broken[:3])}")
    
    if agents.exists():
        content = agents.read_text(encoding='utf-8')
        broken = check_broken_links(content, agents)
        if broken:
            result['agents_issues'].append(f"Broken links: {', '.join(broken[:3])}")
    
    if spec.exists():
        content = spec.read_text(encoding='utf-8')
        if check_placeholder_content(content):
            result['spec_issues'].append("Has placeholder content")
        broken = check_broken_links(content, spec)
        if broken:
            result['spec_issues'].append(f"Broken links: {', '.join(broken[:3])}")
    
    # Only return if there are issues
    if result['readme_issues'] or result['agents_issues'] or result['spec_issues']:
        return result
    return None

def main():
    """Identify directories needing work."""
    base_path = Path("/Users/mini/Documents/GitHub/codomyrmex")
    issues = []
    
    for root, dirs, files in os.walk(base_path):
        dirs[:] = [d for d in dirs if not d.startswith('.') and 
                   d not in ['__pycache__', 'node_modules', 'venv', '.venv', '.git']]
        
        current_dir = Path(root)
        if current_dir == base_path:
            continue
        
        result = analyze_directory(current_dir)
        if result:
            issues.append(result)
    
    print(f"Found {len(issues)} directories with documentation issues\n")
    
    # Group by issue type
    placeholder_specs = [i for i in issues if 'Has placeholder content' in i.get('spec_issues', [])]
    broken_links = [i for i in issues if any('Broken links' in issue for issue in i.get('readme_issues', []) + i.get('agents_issues', []) + i.get('spec_issues', []))]
    
    print(f"SPEC.md with placeholder content: {len(placeholder_specs)}")
    print(f"Files with broken links: {len(broken_links)}\n")
    
    print("Sample directories needing work:")
    for item in issues[:20]:
        print(f"\n{item['path']}:")
        if item['readme_issues']:
            print(f"  README: {item['readme_issues'][0]}")
        if item['agents_issues']:
            print(f"  AGENTS: {item['agents_issues'][0]}")
        if item['spec_issues']:
            print(f"  SPEC: {item['spec_issues'][0]}")

if __name__ == "__main__":
    main()


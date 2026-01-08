from pathlib import Path
from typing import List, Dict
import os
import re




#!/usr/bin/env python3
"""Comprehensive placeholder content check and fix."""


# Enhanced placeholder patterns
PLACEHOLDER_PATTERNS = [
    (r'\[Architecture description if applicable\]', 'Architecture description placeholder'),
    (r'\[Functional requirements for', 'Functional requirements placeholder'),
    (r'\[Testing, documentation, performance, security requirements\]', 'Requirements placeholder'),
    (r'\[APIs, data structures, communication patterns\]', 'Interface placeholder'),
    (r'\[How to implement within this directory\]', 'Implementation placeholder'),
    (r'\[Brief description', 'Brief description placeholder'),
    (r'\[Module Name\]', 'Module name placeholder'),
    (r'\[MainClass\]', 'Main class placeholder'),
    (r'\[module_name\]', 'Module name variable placeholder'),
    (r'Contains components for the src system', 'Generic placeholder description'),
    (r'Documentation files and guides\.', 'Generic documentation placeholder'),
    (r'Test files and validation suites\.', 'Generic test placeholder'),
]

def find_placeholders(content: str, file_path: Path) -> List[Dict]:
    """Find placeholder content in file."""
    issues = []
    for pattern, description in PLACEHOLDER_PATTERNS:
        matches = re.finditer(pattern, content, re.IGNORECASE)
        for match in matches:
            # Get context (50 chars before and after)
            start = max(0, match.start() - 50)
            end = min(len(content), match.end() + 50)
            context = content[start:end]
            
            issues.append({
                'pattern': pattern,
                'description': description,
                'match': match.group(0),
                'position': match.start(),
                'context': context
            })
    return issues

def fix_generic_placeholders(content: str, file_path: Path) -> str:
    """Fix generic placeholder descriptions."""
    # Get directory name for context
    dir_name = file_path.parent.name
    
    # Fix "Contains components for the src system"
    if 'Contains components for the src system' in content:
        # Try to infer purpose from directory name
        if 'docs' in dir_name.lower():
            replacement = f"Documentation files and guides for {dir_name}."
        elif 'test' in dir_name.lower():
            replacement = f"Test files and validation suites for {dir_name}."
        elif 'example' in dir_name.lower():
            replacement = f"Example implementations and demonstrations for {dir_name}."
        else:
            replacement = f"Module components and implementation for {dir_name}."
        content = content.replace('Contains components for the src system', replacement)
    
    # Fix "Documentation files and guides."
    if 'Documentation files and guides.' in content and 'docs' not in dir_name.lower():
        replacement = f"Documentation files and guides for {dir_name}."
        content = content.replace('Documentation files and guides.', replacement)
    
    # Fix "Test files and validation suites."
    if 'Test files and validation suites.' in content and 'test' not in dir_name.lower():
        replacement = f"Test files and validation suites for {dir_name}."
        content = content.replace('Test files and validation suites.', replacement)
    
    return content

def main():
    """Run comprehensive placeholder check."""
    base_path = Path("/Users/mini/Documents/GitHub/codomyrmex")
    
    doc_files = []
    for root, dirs, files in os.walk(base_path):
        dirs[:] = [d for d in dirs if not d.startswith('.') and 
                   d not in ['__pycache__', 'node_modules', 'venv', '.venv', '.git', '@output']]
        
        for file in ['README.md', 'AGENTS.md', 'SPEC.md']:
            file_path = Path(root) / file
            if file_path.exists():
                doc_files.append(file_path)
    
    print(f"Checking {len(doc_files)} files for placeholders...\n")
    
    total_issues = 0
    fixed_count = 0
    
    for file_path in doc_files:
        try:
            content = file_path.read_text(encoding='utf-8')
            original = content
            
            # Find placeholders
            issues = find_placeholders(content, file_path)
            
            if issues:
                total_issues += len(issues)
                print(f"\n{file_path.relative_to(base_path)}: {len(issues)} placeholder(s)")
                for issue in issues[:3]:  # Show first 3
                    print(f"  - {issue['description']}: {issue['match'][:50]}")
            
            # Fix generic placeholders
            content = fix_generic_placeholders(content, file_path)
            
            if content != original:
                file_path.write_text(content, encoding='utf-8')
                fixed_count += 1
                print(f"  Fixed generic placeholders")
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
    
    print(f"\n=== SUMMARY ===")
    print(f"Total placeholder issues found: {total_issues}")
    print(f"Files with generic placeholders fixed: {fixed_count}")

if __name__ == "__main__":
    main()


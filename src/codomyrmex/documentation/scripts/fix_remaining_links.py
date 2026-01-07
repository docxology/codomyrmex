#!/usr/bin/env python3
"""Fix remaining broken links in documentation."""

import os
import re
from pathlib import Path

def fix_self_referential_links(content: str, file_path: Path) -> str:
    """Fix self-referential directory links."""
    base_path = Path("/Users/mini/Documents/GitHub/codomyrmex")
    rel_path = file_path.parent.relative_to(base_path)
    current_dir_name = file_path.parent.name
    
    # Fix patterns like [docs](../../../docs/README.md) when already in docs/
    patterns = [
        # Self-referential directory links
        (rf'\[{re.escape(current_dir_name)}\]\(\.\.\/\.\.\/\.\.\/{re.escape(current_dir_name)}\/README\.md\)', f'[{current_dir_name}](../README.md)'),
        (rf'\[{re.escape(current_dir_name)}\]\(\.\.\/\.\.\/{re.escape(current_dir_name)}\/README\.md\)', f'[{current_dir_name}](../README.md)'),
        
        # Parent directory references that are wrong
        (r'\[projects\]\(\.\.\/\.\.\/\.\.\/projects\/README\.md\)', '[projects](../README.md)'),
        (r'\[testing\]\(\.\.\/\.\.\/\.\.\/testing\/README\.md\)', '[testing](../README.md)'),
        (r'\[docs\]\(\.\.\/\.\.\/\.\.\/docs\/README\.md\)', '[docs](../README.md)'),
        (r'\[config\]\(\.\.\/\.\.\/\.\.\/config\/README\.md\)', '[config](../README.md)'),
        (r'\[cursorrules\]\(\.\.\/\.\.\/\.\.\/cursorrules\/README\.md\)', '[cursorrules](../README.md)'),
    ]
    
    for pattern, replacement in patterns:
        content = re.sub(pattern, replacement, content)
    
    return content

def fix_relative_path_links(content: str, file_path: Path) -> str:
    """Fix relative path links that don't start with ../ or ./."""
    base_path = Path("/Users/mini/Documents/GitHub/codomyrmex")
    
    # Find links that look like relative paths but don't start with ./
    pattern = r'\[([^\]]+)\]\(([^\)]+)\)'
    
    def fix_link(match):
        link_text, link_path = match.groups()
        
        # Skip external links and anchors
        if link_path.startswith('http') or link_path.startswith('#') or link_path.startswith('./') or link_path.startswith('../'):
            return match.group(0)
        
        # If it's a relative path without ./ or ../, it might be wrong
        # Check if it should be relative to current directory or parent
        if '/' in link_path and not link_path.startswith('./'):
            # Try to resolve it
            try:
                target = (file_path.parent / link_path).resolve()
                if target.exists():
                    # Calculate correct relative path
                    rel = os.path.relpath(target, file_path.parent)
                    return f'[{link_text}]({rel.replace(chr(92), "/")})'
            except Exception:
                pass
        
        return match.group(0)
    
    content = re.sub(pattern, fix_link, content)
    return content

def process_file(file_path: Path) -> bool:
    """Process a documentation file."""
    if not file_path.exists():
        return False
    
    try:
        content = file_path.read_text(encoding='utf-8')
        original = content
        
        # Fix self-referential links
        content = fix_self_referential_links(content, file_path)
        
        # Fix relative path links
        content = fix_relative_path_links(content, file_path)
        
        if content != original:
            file_path.write_text(content, encoding='utf-8')
            return True
        return False
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False

def main():
    """Fix remaining broken links."""
    base_path = Path("/Users/mini/Documents/GitHub/codomyrmex")
    fixed_count = 0
    
    for root, dirs, files in os.walk(base_path):
        dirs[:] = [d for d in dirs if not d.startswith('.') and 
                   d not in ['__pycache__', 'node_modules', 'venv', '.venv', '.git']]
        
        for file in ['README.md', 'AGENTS.md', 'SPEC.md']:
            file_path = Path(root) / file
            if file_path.exists() and file_path.parent != base_path:
                if process_file(file_path):
                    fixed_count += 1
                    if fixed_count % 20 == 0:
                        print(f"Fixed {fixed_count} files...")
    
    print(f"\nCompleted: Fixed {fixed_count} files")

if __name__ == "__main__":
    main()


from pathlib import Path
from typing import List, Tuple
import os
import re

from codomyrmex.logging_monitoring import get_logger




















#!/usr/bin/env python3
"""
def find_markdown_links(content: str) -> List[Tuple[str, str]]:
    """



    #!/usr/bin/env python3
    """Validate links in documentation files."""

logger = get_logger(__name__)

Find all markdown links in content."""
    # Pattern for markdown links: [text](path)
    pattern = r'\[([^\]]+)\]\(([^\)]+)\)'
    matches = re.findall(pattern, content)
    return matches

def validate_link(base_path: Path, link_path: str) -> bool:
    """Validate if a link path exists."""
    # Handle different link types
    if link_path.startswith('http://') or link_path.startswith('https://'):
        return True  # External links - can't validate
    
    if link_path.startswith('#'):
        return True  # Anchor links - assume valid
    
    # Resolve relative path
    try:
        target = (base_path / link_path).resolve()
        return target.exists()
    except Exception:
        return False

def validate_file_links(file_path: Path) -> List[Tuple[str, str, bool]]:
    """Validate all links in a file."""
    if not file_path.exists():
        return []
    
    try:
        content = file_path.read_text(encoding='utf-8')
        links = find_markdown_links(content)
        results = []
        
        for link_text, link_path in links:
            is_valid = validate_link(file_path.parent, link_path)
            results.append((link_text, link_path, is_valid))
        
        return results
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return []

def main():
    """Validate links in all documentation files."""
    base_path = Path("/Users/mini/Documents/GitHub/codomyrmex")
    broken_links = []
    total_links = 0
    files_checked = 0
    
    for root, dirs, files in os.walk(base_path):
        dirs[:] = [d for d in dirs if not d.startswith('.') and 
                   d not in ['__pycache__', 'node_modules', 'venv', '.venv', '.git']]
        
        for file in files:
            if file in ['README.md', 'AGENTS.md', 'SPEC.md']:
                file_path = Path(root) / file
                results = validate_file_links(file_path)
                files_checked += 1
                
                for link_text, link_path, is_valid in results:
                    total_links += 1
                    if not is_valid and not link_path.startswith('http'):
                        broken_links.append((str(file_path.relative_to(base_path)), link_text, link_path))
    
    print(f"Checked {files_checked} files with {total_links} total links")
    print(f"Found {len(broken_links)} broken links")
    
    if broken_links:
        print("\nBroken links (first 20):")
        for file_path, link_text, link_path in broken_links[:20]:
            print(f"  {file_path}: [{link_text}]({link_path})")
    
    return len(broken_links) == 0

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)

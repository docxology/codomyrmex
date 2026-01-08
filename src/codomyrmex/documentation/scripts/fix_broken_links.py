from pathlib import Path
from typing import List, Tuple
import re

from codomyrmex.logging_monitoring import get_logger




















#!/usr/bin/env python3
"""
Fix broken links in documentation files.

This script fixes common broken link patterns found during documentation scanning.
"""


#!/usr/bin/env python3
"""


logger = get_logger(__name__)

def fix_links_in_file(file_path: Path, repo_root: Path) -> List[str]:
    """Fix broken links in a single file."""
    fixes = []
    
    try:
        content = file_path.read_text(encoding='utf-8')
        original_content = content
        file_dir = file_path.parent
        
        # Pattern for markdown links
        link_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
        
        def replace_link(match):
            link_text = match.group(1)
            link_url = match.group(2)
            
            # Skip external links
            if link_url.startswith(('http://', 'https://', 'mailto:')):
                return match.group(0)
            
            # Skip anchor-only links
            if link_url.startswith('#'):
                return match.group(0)
            
            # Remove anchor for path resolution
            anchor = ''
            if '#' in link_url:
                anchor = '#' + link_url.split('#', 1)[1]
                link_url = link_url.split('#')[0]
            
            # Fix common broken link patterns
            new_url = link_url
            
            # Fix examples/ references (should be scripts/examples/)
            if link_url.startswith('examples/'):
                # Calculate relative path from file to scripts/examples
                rel_path = Path(file_dir).relative_to(repo_root)
                # Go up to repo root, then to scripts/examples
                levels_up = len(rel_path.parts)
                new_url = '../' * levels_up + 'scripts/examples/' + link_url[9:]  # Remove 'examples/'
                fixes.append(f"Fixed: {link_url} -> {new_url}")
            elif link_url == 'examples/':
                rel_path = Path(file_dir).relative_to(repo_root)
                levels_up = len(rel_path.parts)
                new_url = '../' * levels_up + 'scripts/examples/'
                fixes.append(f"Fixed: {link_url} -> {new_url}")
            
            # Fix docs/README.md references from project/ directory
            if link_url == 'docs/README.md' and 'project' in str(file_dir):
                new_url = '../README.md'
                fixes.append(f"Fixed: {link_url} -> {new_url}")
            
            # Fix ./reference/ references from project/ directory
            if link_url.startswith('./reference/') and 'project' in str(file_dir):
                new_url = '../reference/' + link_url[12:]  # Remove './reference/'
                fixes.append(f"Fixed: {link_url} -> {new_url}")
            
            # Fix development/documentation.md from project/ directory
            if link_url == 'development/documentation.md' and 'project' in str(file_dir):
                new_url = '../development/documentation.md'
                fixes.append(f"Fixed: {link_url} -> {new_url}")
            
            if new_url != link_url:
                return f'[{link_text}]({new_url}{anchor})'
            
            return match.group(0)
        
        # Apply replacements
        new_content = re.sub(link_pattern, replace_link, content)
        
        if new_content != original_content:
            file_path.write_text(new_content, encoding='utf-8')
            return fixes
    
    except Exception as e:
        return [f"Error processing {file_path}: {e}"]
    
    return fixes


def main():
    """Main function."""
    repo_root = Path(__file__).parent.parent.parent
    docs_dir = repo_root / 'docs'
    
    if not docs_dir.exists():
        print(f"Error: Documentation directory not found: {docs_dir}")
        return 1
    
    print("Fixing broken links in documentation...")
    print("=" * 80)
    
    all_fixes = []
    md_files = list(docs_dir.rglob("*.md"))
    
    for md_file in md_files:
        fixes = fix_links_in_file(md_file, repo_root)
        if fixes:
            all_fixes.extend([(md_file, fix) for fix in fixes])
    
    if all_fixes:
        print(f"\nFixed {len(all_fixes)} broken links:\n")
        for file_path, fix in all_fixes:
            print(f"  {file_path.relative_to(repo_root)}: {fix}")
    else:
        print("\nNo broken links found to fix.")
    
    return 0


if __name__ == '__main__':
    exit(main())

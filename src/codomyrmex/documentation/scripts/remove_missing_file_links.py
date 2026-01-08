from pathlib import Path
import os
import re















#!/usr/bin/env python3
"""Remove or fix links to missing files."""


def check_and_fix_missing_links(file_path: Path, base_path: Path) -> bool:
    """Check and fix links to missing files."""
    if not file_path.exists():
        return False
    
    try:
        content = file_path.read_text(encoding='utf-8')
        original = content
        
        # Find all markdown links
        link_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
        matches = list(re.finditer(link_pattern, content))
        
        for match in reversed(matches):  # Reverse to maintain positions
            link_text = match.group(1)
            link_url = match.group(2)
            
            # Skip external links and anchors
            if link_url.startswith(('http://', 'https://', 'mailto:', '#')):
                continue
            
            # Resolve the link path
            if link_url.startswith('./'):
                link_url = link_url[2:]
            
            if link_url.startswith('../'):
                # Count levels up
                levels_up = link_url.count('../')
                base_dir = file_path.parent
                for _ in range(levels_up):
                    base_dir = base_dir.parent
                resolved = base_dir / link_url.lstrip('../')
            elif link_url.startswith('/'):
                resolved = base_path / link_url.lstrip('/')
            else:
                resolved = file_path.parent / link_url
            
            # Check if file exists
            if not resolved.exists():
                # Check if it's a common missing file pattern
                if 'API_SPECIFICATION.md' in link_url or 'USAGE_EXAMPLES.md' in link_url:
                    # Remove the link, keeping just the text
                    content = content[:match.start()] + link_text + content[match.end():]
                elif 'SPEC.md' in link_url and 'scripts/' in str(file_path):
                    # For scripts SPEC.md files, remove the library spec link if it doesn't exist
                    if 'Library Spec' in link_text or 'library spec' in link_text.lower():
                        # Remove the entire line
                        line_start = content.rfind('\n', 0, match.start()) + 1
                        line_end = content.find('\n', match.end())
                        if line_end == -1:
                            line_end = len(content)
                        line = content[line_start:line_end]
                        if link_url in line:
                            content = content[:line_start] + content[line_end+1:]
        
        if content != original:
            file_path.write_text(content, encoding='utf-8')
            return True
        return False
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False

def main():
    """Remove links to missing files."""
    base_path = Path("/Users/mini/Documents/GitHub/codomyrmex")
    fixed_count = 0
    
    # Process examples directory
    examples_dir = base_path / "examples"
    for module_dir in examples_dir.iterdir():
        if module_dir.is_dir():
            readme = module_dir / "README.md"
            if readme.exists():
                if check_and_fix_missing_links(readme, base_path):
                    fixed_count += 1
                    print(f"Fixed: {readme.relative_to(base_path)}")
    
    # Process scripts directory SPEC.md files
    scripts_dir = base_path / "scripts"
    for subdir in scripts_dir.iterdir():
        if subdir.is_dir():
            spec = subdir / "SPEC.md"
            if spec.exists():
                if check_and_fix_missing_links(spec, base_path):
                    fixed_count += 1
                    print(f"Fixed: {spec.relative_to(base_path)}")
    
    print(f"\nCompleted: Fixed {fixed_count} files with missing file links")

if __name__ == "__main__":
    main()


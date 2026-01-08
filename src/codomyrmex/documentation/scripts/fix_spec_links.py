from pathlib import Path
import os
import re















#!/usr/bin/env python3
"""Fix broken links in SPEC.md files."""


def calculate_relative_path(from_dir: Path, to_file: Path) -> str:
    """Calculate relative path from directory to file."""
    try:
        rel_path = os.path.relpath(to_file, from_dir)
        return rel_path.replace('\\', '/')
    except ValueError:
        # If paths are on different drives (Windows), return absolute
        return str(to_file)

def fix_spec_file(spec_path: Path):
    """Fix links in a SPEC.md file."""
    base_path = Path("/Users/mini/Documents/GitHub/codomyrmex")
    
    if not spec_path.exists():
        return False
    
    try:
        content = spec_path.read_text(encoding='utf-8')
        original_content = content
        
        # Calculate correct relative paths
        dir_path = spec_path.parent
        rel_to_root = dir_path.relative_to(base_path)
        depth = len(rel_to_root.parts)
        
        # Fix repository root links
        root_readme = base_path / "README.md"
        root_spec = base_path / "SPEC.md"
        
        root_readme_rel = calculate_relative_path(dir_path, root_readme)
        root_spec_rel = calculate_relative_path(dir_path, root_spec)
        
        # Replace incorrect root paths
        content = re.sub(
            r'- \*\*Repository Root\*\*: \[.*?README\.md\]\([^)]+\)',
            f'- **Repository Root**: [{root_readme_rel}]({root_readme_rel})',
            content
        )
        
        if depth > 0:  # Only add SPEC link if not at root
            content = re.sub(
                r'- \*\*Repository SPEC\*\*: \[.*?SPEC\.md\]\([^)]+\)',
                f'- **Repository SPEC**: [{root_spec_rel}]({root_spec_rel})',
                content
            )
        else:
            # Remove SPEC link if at root
            content = re.sub(
                r'- \*\*Repository SPEC\*\*: \[.*?SPEC\.md\]\([^)]+\)\n',
                '',
                content
            )
        
        # Fix parent directory links
        if depth > 0:
            parent_dir = dir_path.parent
            parent_readme = parent_dir / "README.md"
            parent_readme_rel = calculate_relative_path(dir_path, parent_readme)
            parent_name = parent_dir.name
            
            # Replace parent directory links
            content = re.sub(
                r'- \*\*Parent Directory\*\*: \[.*?\]\([^)]+\)',
                f'- **Parent Directory**: [{parent_name}](../README.md)',
                content
            )
        
        if content != original_content:
            spec_path.write_text(content, encoding='utf-8')
            return True
        
        return False
    except Exception as e:
        print(f"Error fixing {spec_path}: {e}")
        return False

def main():
    """Fix links in all SPEC.md files."""
    base_path = Path("/Users/mini/Documents/GitHub/codomyrmex")
    fixed_count = 0
    
    for root, dirs, files in os.walk(base_path):
        dirs[:] = [d for d in dirs if not d.startswith('.') and 
                   d not in ['__pycache__', 'node_modules', 'venv', '.venv', '.git']]
        
        if 'SPEC.md' in files:
            spec_path = Path(root) / 'SPEC.md'
            if fix_spec_file(spec_path):
                fixed_count += 1
                if fixed_count % 10 == 0:
                    print(f"Fixed {fixed_count} files...")
    
    print(f"\nCompleted: Fixed {fixed_count} SPEC.md files")

if __name__ == "__main__":
    main()


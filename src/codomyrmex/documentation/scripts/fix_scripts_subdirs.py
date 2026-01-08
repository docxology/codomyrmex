from pathlib import Path
import os
import re

from codomyrmex.logging_monitoring import get_logger




















#!/usr/bin/env python3
"""
def fix_scripts_subdir_readme(file_path: Path) -> bool:
    """



    #!/usr/bin/env python3
    """Fix relative paths in scripts/*/README.md files."""

logger = get_logger(__name__)

Fix relative paths in a scripts subdirectory README."""
    if not file_path.exists():
        return False
    
    try:
        content = file_path.read_text(encoding='utf-8')
        original = content
        
        # Fix common broken patterns
        # ../../../scripts/README.md should be ../README.md (scripts/{subdir} is 1 level below scripts)
        content = re.sub(r'\(\.\./\.\./\.\./scripts/README\.md\)', r'(../README.md)', content)
        content = re.sub(r'\[scripts\]\(\.\./\.\./\.\./scripts/README\.md\)', r'[scripts](../README.md)', content)
        
        # ../../../cursorrules/ should be ../cursorrules/
        content = re.sub(r'\(\.\./\.\./\.\./cursorrules/', r'(../cursorrules/', content)
        
        # ../../../docs/ should be ../docs/
        content = re.sub(r'\(\.\./\.\./\.\./docs/', r'(../docs/', content)
        
        # ../../../testing/ should be ../testing/
        content = re.sub(r'\(\.\./\.\./\.\./testing/', r'(../testing/', content)
        
        if content != original:
            file_path.write_text(content, encoding='utf-8')
            return True
        return False
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False

def main():
    """Fix all scripts subdirectory READMEs."""
    base_path = Path("/Users/mini/Documents/GitHub/codomyrmex")
    scripts_dir = base_path / "scripts"
    fixed_count = 0
    
    for subdir in scripts_dir.iterdir():
        if subdir.is_dir() and not subdir.name.startswith('_'):
            readme = subdir / "README.md"
            if readme.exists():
                if fix_scripts_subdir_readme(readme):
                    fixed_count += 1
                    print(f"Fixed: {readme.relative_to(base_path)}")
    
    print(f"\nCompleted: Fixed {fixed_count} scripts subdirectory README files")

if __name__ == "__main__":
    main()

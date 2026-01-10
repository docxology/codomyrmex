from pathlib import Path
import os
import re

from codomyrmex.logging_monitoring import get_logger




















"""
def fix_examples_module_readme(file_path: Path) -> bool:
    """



    #!/usr/bin/env python3
    """Fix relative paths in all examples/{module}/README.md files."""

logger = get_logger(__name__)

Fix relative paths in an examples module README."""
    if not file_path.exists():
        return False
    
    try:
        content = file_path.read_text(encoding='utf-8')
        original = content
        
        # Fix common broken patterns
        # ../src/ should be ../../src/ (examples/{module} is 2 levels from root)
        content = re.sub(r'\(\.\./src/', r'(../../src/', content)
        
        # ../../../src/ should be ../../src/
        content = re.sub(r'\(\.\./\.\./\.\./src/', r'(../../src/', content)
        
        # ../examples/ should be ../ (same level)
        content = re.sub(r'\(\.\./examples/', r'(../', content)
        
        # ../../multi_module/ should be ../multi_module/
        content = re.sub(r'\(\.\./\.\./multi_module/', r'(../multi_module/', content)
        
        if content != original:
            file_path.write_text(content, encoding='utf-8')
            return True
        return False
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False

def main():
    """Fix all examples module READMEs."""
    base_path = Path("/Users/mini/Documents/GitHub/codomyrmex")
    examples_dir = base_path / "examples"
    fixed_count = 0
    
    for module_dir in examples_dir.iterdir():
        if module_dir.is_dir() and not module_dir.name.startswith('_'):
            readme = module_dir / "README.md"
            if readme.exists():
                if fix_examples_module_readme(readme):
                    fixed_count += 1
                    print(f"Fixed: {readme.relative_to(base_path)}")
    
    print(f"\nCompleted: Fixed {fixed_count} examples module README files")

if __name__ == "__main__":
    main()

from pathlib import Path
import re















#!/usr/bin/env python3
"""Fix all src/README.md links in module subdirectories."""


def calculate_correct_path(from_file: Path, base_path: Path) -> str:
    """Calculate correct relative path to src/README.md."""
    rel_path = from_file.parent.relative_to(base_path)
    depth = len(rel_path.parts)
    return "../" * depth + "src/README.md"

def fix_src_links(file_path: Path, base_path: Path) -> bool:
    """Fix src/README.md links in a file."""
    if not file_path.exists():
        return False
    
    try:
        content = file_path.read_text(encoding='utf-8')
        original = content
        
        # Calculate correct path
        correct_path = calculate_correct_path(file_path, base_path)
        
        # Fix all variations of src/README.md links
        # Match [src](../../src/README.md) or [src](../../../src/README.md) etc.
        pattern = r'\[src\]\(\.\./\.\.(/\.\.)*/src/README\.md\)'
        replacement = f'[src]({correct_path})'
        content = re.sub(pattern, replacement, content)
        
        if content != original:
            file_path.write_text(content, encoding='utf-8')
            return True
        return False
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False

def main():
    """Fix all src links in module subdirectories."""
    base_path = Path("/Users/mini/Documents/GitHub/codomyrmex")
    fixed_count = 0
    
    # Fix in all module subdirectories
    modules_dir = base_path / "src/codomyrmex"
    for readme in modules_dir.rglob("README.md"):
        if fix_src_links(readme, base_path):
            fixed_count += 1
            if fixed_count % 10 == 0:
                print(f"Fixed {fixed_count} files...")
    
    print(f"\nCompleted: Fixed {fixed_count} files")

if __name__ == "__main__":
    main()


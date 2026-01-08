from pathlib import Path
import re















#!/usr/bin/env python3
"""Fix src/README.md links in deeply nested documentation directories."""


def calculate_correct_path(from_file: Path, base_path: Path) -> str:
    """Calculate correct relative path to src/README.md."""
    # Calculate depth from root
    rel_path = from_file.parent.relative_to(base_path)
    depth = len(rel_path.parts)
    
    # Build correct path: go up depth levels, then to src/README.md
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
        
        # Fix the link pattern [src](../../src/README.md)
        # Match various patterns
        patterns = [
            (r'\[src\]\(\.\./\.\./src/README\.md\)', f'[src]({correct_path})'),
            (r'\[src\]\(\.\./\.\./\.\./src/README\.md\)', f'[src]({correct_path})'),
            (r'\[src\]\(\.\./\.\./\.\./\.\./src/README\.md\)', f'[src]({correct_path})'),
            (r'\[src\]\(\.\./\.\./\.\./\.\./\.\./src/README\.md\)', f'[src]({correct_path})'),
            (r'\[src\]\(\.\./\.\./\.\./\.\./\.\./\.\./src/README\.md\)', f'[src]({correct_path})'),
            (r'\[src\]\(\.\./\.\./\.\./\.\./\.\./\.\./\.\./src/README\.md\)', f'[src]({correct_path})'),
            (r'\[src\]\(\.\./\.\./\.\./\.\./\.\./\.\./\.\./\.\./src/README\.md\)', f'[src]({correct_path})'),
        ]
        
        for pattern, replacement in patterns:
            content = re.sub(pattern, replacement, content)
        
        if content != original:
            file_path.write_text(content, encoding='utf-8')
            return True
        return False
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False

def main():
    """Fix src links in documentation directory."""
    base_path = Path("/Users/mini/Documents/GitHub/codomyrmex")
    doc_dir = base_path / "src/codomyrmex/documentation"
    fixed_count = 0
    
    for readme in doc_dir.rglob("README.md"):
        if fix_src_links(readme, base_path):
            fixed_count += 1
            print(f"Fixed: {readme.relative_to(base_path)}")
    
    print(f"\nCompleted: Fixed {fixed_count} files")

if __name__ == "__main__":
    main()


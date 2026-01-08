
import sys
from pathlib import Path
try:
    import codomyrmex
except ImportError:
    # Add project root to sys.path
    project_root = Path(__file__).resolve().parent.parent.parent
    src_path = project_root / "src"
    sys.path.insert(0, str(src_path))
import os
import re
from pathlib import Path

ROOT_DIR = Path("/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex")

CORRUPTION_PATTERNS = [
    # Pattern 1: Core functionality/business logic/Testing utilities block nested
    # Matches: """\n"""Core ... """
    re.compile(r'"""\n"""(Core (functionality module|business logic)|Testing utilities and test helpers).*?Usage:\n\s+# Example usage here\n"""\n', re.DOTALL),
    
    # Pattern 2: Just the inner block if it's not preceded by """
    # Matches: """Core ... """ or """Testing ... """
    re.compile(r'"""(Core (functionality module|business logic)|Testing utilities and test helpers).*?Usage:\n\s+# Example usage here\n"""\n', re.DOTALL),
    
    # Pattern 3: Nested Brief description docstrings (indented or not)
    # Matches: """Brief description of ... Returns: ... """
    re.compile(r'\s*"""Brief description of.*?Returns: Description of return value\n"""', re.DOTALL),
]

def fix_file(file_path):
    try:
        content = file_path.read_text(encoding="utf-8")
    except Exception as e:
        print(f"Skipping {file_path}: {e}")
        return

    original_content = content
    new_content = content
    
    for pattern in CORRUPTION_PATTERNS:
        new_content = pattern.sub("", new_content)

    if new_content != original_content:
        # Check if we created a syntax error by leaving a dangling """ or empty space that matters
        # But generally removing these blocks is safe as they are usually insertions.
        print(f"Fixed {file_path}")
        file_path.write_text(new_content, encoding="utf-8")

def main():
    print(f"Scanning {ROOT_DIR}...")
    for file_path in ROOT_DIR.rglob("*.py"):
        fix_file(file_path)
    print("Done.")

if __name__ == "__main__":
    main()

import sys
from pathlib import Path
try:
    import codomyrmex
except ImportError:
    # Add project root to sys.path
    project_root = Path(__file__).resolve().parent.parent.parent
    src_path = project_root / "src"
    sys.path.insert(0, str(src_path))
import glob
from pathlib import Path
import re

def fix_imports(file_path):
    try:
        content = file_path.read_text()
    except Exception:
        return False
    
    # We want to remove lines that import FunctionName, ClassName
    # Pattern: from <module> import FunctionName, ClassName
    # Or: from . import FunctionName, ClassName
    
    # Simple line-based filtering is safer than regex for this specific case
    lines = content.splitlines()
    new_lines = []
    modified = False
    
    for line in lines:
        if "import FunctionName, ClassName" in line:
            # Check if it's a suspicious import
            if line.strip().startswith("from ") or line.strip().startswith("import "):
                 modified = True
                 continue # Skip this line
        new_lines.append(line)
        
    if modified:
        # Reconstruct file with original line endings (newlines are stripped by splitlines)
        # But we can just join with \n.
        new_content = "\n".join(new_lines) + "\n"
        file_path.write_text(new_content)
        print(f"Fixed imports in {file_path}")
        return True
            
    return False

def main():
    repo_root = Path(".")
    # Scan src folder
    count = 0
    for f in repo_root.glob("src/**/*.py"):
        if fix_imports(f):
            count += 1
            
    print(f"Fixed {count} files.")

if __name__ == "__main__":
    main()
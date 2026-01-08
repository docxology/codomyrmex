
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

def fix_broken_imports(file_path):
    try:
        content = file_path.read_text()
    except Exception:
        return False
        
    lines = content.splitlines()
    new_lines = []
    i = 0
    modified = False
    
    while i < len(lines):
        line = lines[i]
        
        # Check for start of import block
        if line.strip().endswith("import ("):
            if i + 1 < len(lines):
                next_line = lines[i+1]
                if next_line.strip().startswith("from ") or next_line.strip().startswith("import "):
                    # Found broken import!
                    # Move next_line before current line
                    new_lines.append(next_line)
                    new_lines.append(line)
                    modified = True
                    i += 2 # Skip both
                    continue
        
        new_lines.append(line)
        i += 1
        
    if modified:
        # Reconstruct file
        new_content = "\n".join(new_lines) + "\n"
        file_path.write_text(new_content)
        print(f"Fixed broken imports in {file_path}")
        return True
    return False

def main():
    repo_root = Path(".")
    count = 0
    for f in repo_root.glob("src/**/*.py"):
        if fix_broken_imports(f):
            count += 1
            
    print(f"Fixed {count} files.")

if __name__ == "__main__":
    main()

import glob
from pathlib import Path

SYSPATH_SETUP = """
import sys
from pathlib import Path
try:
    import codomyrmex
except ImportError:
    # Add project root to sys.path
    project_root = Path(__file__).resolve().parent.parent.parent
    src_path = project_root / "src"
    sys.path.insert(0, str(src_path))
"""

def ensure_sys_path(file_path):
    try:
        content = file_path.read_text()
    except Exception:
        return False
        
    if "sys.path.insert" in content and "src" in content:
        return False
        
    # We want to insert this after imports?
    # Or at the very top (after shebang/docstring)?
    
    lines = content.splitlines()
    insert_idx = 0
    
    # Skip shebang
    if lines and lines[0].startswith("#!"):
        insert_idx += 1
        
    # Skip docstrings
    in_docstring = False
    i = insert_idx
    while i < len(lines):
        line = lines[i].strip()
        if line.startswith('"""') or line.startswith("'''"):
            if line.count('"""') == 2 or line.count("'''") == 2:
                # Single line docstring
                pass
            else:
                in_docstring = not in_docstring
        
        elif not in_docstring and line:
            # Found first code line
            insert_idx = i
            break
        i += 1
        
    # If we reached end, append?
    if i == len(lines):
        insert_idx = i
        
    # Insert code
    new_content = "\n".join(lines[:insert_idx]) + SYSPATH_SETUP + "\n".join(lines[insert_idx:])
    file_path.write_text(new_content)
    print(f"Added sys.path setup to {file_path}")
    return True

def main():
    repo_root = Path(".")
    count = 0
    for f in repo_root.glob("scripts/**/*.py"):
        if f.name == "run_all_scripts.py" or f.name == "ensure_sys_path.py" or f.name == "fix_garbage.py":
            continue
        if ensure_sys_path(f):
            count += 1
            
    print(f"Fixed {count} files.")

if __name__ == "__main__":
    main()


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

def fix_tangled_imports(file_path):
    try:
        content = file_path.read_text()
    except Exception:
        return False
        
    lines = content.splitlines()
    new_lines = []
    
    in_import_block = False
    extracted_lines = [] # Lines to move AFTER the block
    
    modified = False
    
    for line in lines:
        stripped = line.strip()
        
        if in_import_block:
            # Check for end of block
            if stripped.startswith(")") or stripped.endswith(")"):
                # End of block
                in_import_block = False
                new_lines.append(line)
                # Append extracted lines immediately after
                new_lines.extend(extracted_lines)
                extracted_lines = []
            else:
                # Check for invalid lines inside block
                is_invalid = False
                if stripped.startswith("from ") or stripped.startswith("import "):
                    is_invalid = True
                elif stripped.startswith("try:") or stripped.startswith("except ") or stripped.startswith("except:"):
                    is_invalid = True
                elif stripped.startswith("logger ="):
                    is_invalid = True
                elif stripped.startswith("if "): 
                     is_invalid = True
                elif stripped.startswith("@"): 
                     is_invalid = True
                elif stripped.startswith("def ") or stripped.startswith("class "):
                     is_invalid = True
                
                if is_invalid:
                    extracted_lines.append(line)
                    modified = True
                else:
                    new_lines.append(line)
        else:
            new_lines.append(line)
            # Check for start of block
            if stripped.startswith("from ") and stripped.endswith("import ("):
                in_import_block = True
    
    if in_import_block:
        # File ended inside a block?
        # Just append extracted lines at the end?
        new_lines.extend(extracted_lines)
    
    if modified:
        # Reconstruct
        new_content = "\n".join(new_lines) + "\n"
        file_path.write_text(new_content)
        print(f"Fixed tangled imports in {file_path}")
        return True
    return False

def main():
    repo_root = Path(".")
    count = 0
    for f in repo_root.glob("src/**/*.py"):
        if fix_tangled_imports(f):
            count += 1
    for f in repo_root.glob("scripts/**/*.py"):
         if fix_tangled_imports(f):
             count += 1
            
    print(f"Fixed {count} files.")

if __name__ == "__main__":
    main()
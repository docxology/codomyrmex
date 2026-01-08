
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

def fix_missing_opening_quote(file_path):
    try:
        content = file_path.read_text()
    except Exception:
        return False
        
    lines = content.splitlines()
    
    # Locate the first lines that are NOT imports/comments/shebang/empty
    # And check if they look like text ending with """
    
    # We look for a line that ends with """ or a line that is solely """ 
    # and preceded by text lines that are NOT code.
    
    # This is tricky to get perfect.
    # Let's focus on the specific pattern from rest_api.py and doc_generator.py:
    # They have imports, then empty lines, then Text.
    
    start_idx = 0
    first_triple_quote = -1
    
    for i, line in enumerate(lines):
        if '"""' in line:
            first_triple_quote = i
            break
            
    if first_triple_quote == -1:
        return False
        
    # Check if this triple quote is closing or opening.
    # If the file has valid syntax, it's fine.
    # But here we assume syntax error.
    
    # Count quotes up to this point?
    # No, let's look at lines BEFORE first_triple_quote.
    
    # Go backwards from first_triple_quote
    # Find start of "text block"
    
    text_start = -1
    is_malformed = False
    
    for i in range(first_triple_quote, -1, -1):
        line = lines[i].strip()
        if not line:
            continue
            
        if i == first_triple_quote:
             # This line has """
             # If it starts with """, it's likely closing if we find text before.
             if line.startswith('"""'):
                 # It might be opening if it's the start of docstring.
                 pass
        
        # Check if line looks like code
        if line.startswith("import ") or line.startswith("from ") or line.startswith("#"):
            # Boundary hit
            break
        
        # If line contains code like symbols =, :, def, class
        if "def " in line or "class " in line or " = " in line:
             break
             
        # It seems to be text
        text_start = i
        
    if text_start != -1:
        # Check if text_start already has """
        if '"""' in lines[text_start]:
            return False # It has opening quote
            
        # Check if prev line has """
        if text_start > 0 and '"""' in lines[text_start-1]:
            return False 
            
        # So we have a block starting at text_start, ending at first_triple_quote (inclusive or not)
        # We should insert """ before text_start.
        
        # Verify it really is text.
        # Check if it has SyntaxError when compiled? 
        # But we are fixing syntax error.
        
        # Apply fix
        lines.insert(text_start, '"""')
        
        # Reconstruct
        new_content = "\n".join(lines) + "\n"
        file_path.write_text(new_content)
        print(f"Fixed missing opening quote in {file_path}")
        return True

    return False

def main():
    repo_root = Path(".")
    count = 0
    for f in repo_root.glob("src/**/*.py"):
        if fix_missing_opening_quote(f):
            count += 1
            
    print(f"Fixed {count} files.")

if __name__ == "__main__":
    main()

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

def fix_file_syntax(file_path):
    content = file_path.read_text()
    
    # Check for the specific broken pattern: imports, empty lines, logger, text, closing quotes
    # Pattern:
    # 1. Imports at start
    # 2. Many newlines
    # 3. logger = get_logger(__name__)
    # 4. Text that SHOULD be in a docstring
    # 5. """ (closing quote)
    
    # Regex to capture the parts
    # match group 1: imports
    # match group 2: docstring content (including the line "This module...")
    # match group 3: rest of code
    
    # We look for logger = get_logger... then text then """
    pattern = r'^(.*?)(\n\s*)*logger = get_logger\(__name__\)\n([\s\S]+?)\"\"\"([\s\S]*)$'
    
    match = re.search(pattern, content, re.MULTILINE)
    if match:
        imports_block = match.group(1).strip()
        docstring_content = match.group(3).strip()
        rest_of_code = match.group(4).strip()
        
        # Reconstruct
        new_content = f"""#!/usr/bin/env python3
\"\"\"
{docstring_content}
\"\"\"
{imports_block}

from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)

{rest_of_code}
"""
        # Clean up double imports of logger if present
        if "from codomyrmex.logging_monitoring import get_logger" in imports_block:
             new_content = new_content.replace(f"{imports_block}\n\nfrom codomyrmex.logging_monitoring import get_logger", imports_block)

        file_path.write_text(new_content)
        print(f"Fixed syntax in {file_path}")
        return True
    
    return False

def main():
    # Target specific directories where we saw errors
    dirs = [
        "src/codomyrmex/documentation/scripts",
        "scripts/documentation",
    ]
    
    count = 0
    repo_root = Path(".")
    
    for d in dirs:
        dir_path = repo_root / d
        if not dir_path.exists():
            continue
            
        for f in dir_path.glob("*.py"):
            try:
                if fix_file_syntax(f):
                    count += 1
            except Exception as e:
                print(f"Failed to process {f}: {e}")
                
    print(f"Fixed {count} files.")

if __name__ == "__main__":
    main()
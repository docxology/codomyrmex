
import sys
from pathlib import Path
try:
    import codomyrmex
except ImportError:
    # Add project root to sys.path
    project_root = Path(__file__).resolve().parent.parent.parent
    src_path = project_root / "src"
    sys.path.insert(0, str(src_path))
import re
from pathlib import Path

def fix_file(file_path):
    content = file_path.read_text()
    
    # Regex to capture the entire try-except block importing _orchestrator_utils
    # We iterate to find all imports inside the parens
    pattern = r'try:\s+from _orchestrator_utils import \(([\s\S]+?)\)\s+except ImportError:[\s\S]+?from _orchestrator_utils import \(([\s\S]+?)\)'
    
    match = re.search(pattern, content)
    if match:
        imports_str = match.group(1)
        # Clean up imports
        imports = [line.strip().rstrip(',') for line in imports_str.split('\n') if line.strip()]
        
        # Build new block
        new_block = "from codomyrmex.utils.cli_helpers import (\n"
        for imp in imports:
            new_block += f"    {imp},\n"
        new_block += ")"
        
        # Replace
        new_content = content.replace(match.group(0), new_block)
        
        file_path.write_text(new_content)
        print(f"Fixed {file_path}")
        return True
    
    # Check for non-try-except version (just in case)
    pattern_simple = r'from _orchestrator_utils import \(([\s\S]+?)\)'
    match_simple = re.search(pattern_simple, content)
    if match_simple and "codomyrmex" not in content:
         # Only replace if it hasn't been replaced yet (the check above handles most)
         pass

    return False

def main():
    scripts_dir = Path(__file__).parent
    files = list(scripts_dir.glob("**/orchestrate.py"))
    
    count = 0
    for f in files:
        if fix_file(f):
            count += 1
            
    print(f"Fixed {count} files.")

if __name__ == "__main__":
    main()
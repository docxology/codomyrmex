
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

def fix_file_syntax(file_path):
    try:
        content = file_path.read_text()
    except Exception:
        return False
    
    marker = "logger = get_logger(__name__)"
    if marker not in content:
        return False

    parts = content.split(marker)
    if len(parts) >= 2:
        pre_marker = parts[0]
        post_marker = marker.join(parts[1:])
        
        quote_idx = post_marker.find('"""')
        if quote_idx == -1:
            return False
            
        docstring_text = post_marker[:quote_idx].strip()
        rest_of_code = post_marker[quote_idx+3:].strip()
        
        imports = pre_marker.strip()
        
        new_content = f"""#!/usr/bin/env python3
\"\"\"
{docstring_text}
\"\"\"
{imports}

from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)

{rest_of_code}
"""
        # Remove duplicate logger import if in imports
        if "from codomyrmex.logging_monitoring import get_logger" in imports:
            new_content = new_content.replace(f"{imports}\n\nfrom codomyrmex.logging_monitoring import get_logger", imports)
            
        file_path.write_text(new_content)
        print(f"Fixed syntax in {file_path}")
        return True
             
    return False

def main():
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
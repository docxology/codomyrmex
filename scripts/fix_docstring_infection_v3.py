
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

def fix_garbage_docstrings(content):
    # Pattern 1: The garbage block
    # Matches: """Title... This module provides ... Usage: ... """
    
    # We look for the specific signature "This module provides ... functionality including:" 
    # and "Usage: ... Example usage here"
    
    pattern = r'"""[^\n]+\n+This module provides [\w\s]+ functionality including:[\s\S]+?Usage:\s+# Example usage here\s+"""'
    
    modified = False
    if re.search(pattern, content):
        content = re.sub(pattern, "", content)
        modified = True
        while re.search(pattern, content):
            content = re.sub(pattern, "", content)
            
    # Also catch the specific "Core functionality module" if the above regex was too strict about newlines
    pattern2 = r''
    if re.search(pattern2, content):
         content = re.sub(pattern2, "", content)
         modified = True

    return content, modified

def robust_fix(file_path):
    try:
        content = file_path.read_text()
    except Exception:
        return False
        
    original_content = content
    content, fixed1 = fix_garbage_docstrings(content)
    
    lines = content.splitlines()
    new_lines = []
    i = 0
    modified_indent = False
    
    last_def_indent = -1
    
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        
        if stripped == "":
            new_lines.append(line)
            i += 1
            continue
            
        indent = len(line) - len(line.lstrip())
        
        if (stripped.startswith("def ") or stripped.startswith("class ") or stripped.startswith("async def ")) and stripped.endswith(":"):
            last_def_indent = indent
        elif stripped.startswith('"""') and last_def_indent != -1:
            if indent <= last_def_indent:
                # Fix indentation
                target_indent = last_def_indent + 4
                indent_diff = target_indent - indent
                
                # Fix start line
                new_lines.append(" " * indent_diff + line)
                modified_indent = True
                
                # Fix subsequent lines
                i += 1
                while i < len(lines):
                    sub_line = lines[i]
                    if sub_line.strip() == "":
                        new_lines.append(sub_line)
                    else:
                        if sub_line.strip().startswith('"""') or sub_line.strip().endswith('"""'):
                             new_lines.append(" " * indent_diff + sub_line)
                             if sub_line.strip().endswith('"""'):
                                 break
                        else:
                             new_lines.append(" " * indent_diff + sub_line)
                    i += 1
                
                last_def_indent = -1
                i += 1
                continue
            else:
                last_def_indent = -1
        else:
            last_def_indent = -1
            
        new_lines.append(line)
        i += 1
        
    content = "\n".join(new_lines) + "\n"
    
    if fixed1 or modified_indent:
        content = re.sub(r'\n{4,}', '\n\n', content)
        file_path.write_text(content)
        print(f"Fixed {file_path}")
        return True
        
    return False

def main():
    repo_root = Path(".")
    count = 0
    for f in repo_root.glob("src/**/*.py"):
        if robust_fix(f):
            count += 1
            
    print(f"Fixed {count} files.")

if __name__ == "__main__":
    main()

import glob
from pathlib import Path
import re

def remove_garbage_from_file(file_path):
    try:
        content = file_path.read_text()
    except Exception:
        return False
        
    original_content = content
    lines = content.splitlines()
    new_lines = []
    
    # regexes for garbage
    garbage_import_re = re.compile(r"from .* import FunctionName, ClassName")
    garbage_docstring_start_re = re.compile(r'"""Brief description of')
    garbage_docstring_core_re = re.compile(r'No-op context manager')

    i = 0
    while i < len(lines):
        line = lines[i]
        
        # 1. Check for garbage import
        if garbage_import_re.search(line):
            print(f"  Removing garbage import: {line.strip()}")
            i += 1
            continue
            
        # 2. Check for garbage docstrings
        # They seem to be multi-line blocks. We need to skip until the closing """
        # OR they are specific one-liners or blocks we can identify.
        
        # "Brief description of..."
        if garbage_docstring_start_re.search(line):
            print(f"  Removing docstring block starting at {i}: {line.strip()}")
            # consume until closing """
            if line.count('"""') == 2:
                 i += 1
                 continue
            # Else find end
            i += 1
            while i < len(lines):
                if '"""' in lines[i]:
                    i += 1
                    break
                i += 1
            continue
            
        # "Core functionality module"
        if garbage_docstring_core_re.search(line):
             print(f"  Removing Core functionality docstring block starting at {i}")
             # consume until closing """
             if line.count('"""') == 2:
                 i += 1
                 continue
             i += 1
             while i < len(lines):
                 if '"""' in lines[i]:
                     i += 1
                     break
                 i += 1
             continue
             
        # "Core business logic"
        if "Core business logic" in line and '"""' in line:
             print(f"  Removing Core business logic docstring block starting at {i}")
             if line.count('"""') == 2:
                 i += 1
                 continue
             i += 1
             while i < len(lines):
                 if '"""' in lines[i]:
                     i += 1
                     break
                 i += 1
             continue
             
        # "Testing utilities"
        if "Testing utilities" in line and '"""' in line:
             print(f"  Removing Testing utilities docstring block starting at {i}")
             if line.count('"""') == 2:
                 i += 1
                 continue
             i += 1
             while i < len(lines):
                 if '"""' in lines[i]:
                     i += 1
                     break
                 i += 1
             continue

        new_lines.append(line)
        i += 1
    
    # Check for empty class member indentation issues (performance/__init__.py)
    # If we removed a docstring inside a class/def and left it empty, we might need a 'pass'
    cleaned_content = "\n".join(new_lines) + "\n"
    
    # Specific fix for performance/__init__.py context manager
    if "performance/__init__.py" in str(file_path):
        if "def __init__(self, *args, **kwargs): pass" in cleaned_content:
             # It likely has just passes now, which is fine, but check indentation
             pass
    
    if cleaned_content != original_content:
        file_path.write_text(cleaned_content)
        print(f"Cleaned {file_path}")
        return True
        
    return False

def main():
    repo_root = Path(".")
    count = 0
    print("Scanning src directory for garbage...")
    targets = list(repo_root.glob("src/**/*.py"))
    
    for p in targets:
        if p.exists():
            if remove_garbage_from_file(p):
                count += 1
            
    print(f"Cleaned {count} files.")

if __name__ == "__main__":
    main()

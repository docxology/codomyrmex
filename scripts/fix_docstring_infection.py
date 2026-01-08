
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
    # # Regex to find this block. It starts with # It usually appears after the real docstring.
    
    pattern = r''
    if re.search(pattern, content):
        content = re.sub(pattern, "", content)
        # Iterate to remove multiple occurrences if any
        while re.search(pattern, content):
            content = re.sub(pattern, "", content)
        return content, True
    return content, False

def fix_indentation(content):
    lines = content.splitlines()
    new_lines = []
    modified = False
    
    # Track expected indentation
    # We look for lines ending in : (def/class)
    
    last_indent = 0
    expecting_docstring = False
    
    for i, line in enumerate(lines):
        stripped = line.strip()
        indent = len(line) - len(line.lstrip())
        
        if expecting_docstring:
            if stripped.startswith('"""') or stripped.startswith("'''"):
                # Check indentation
                if indent < last_indent:
                    # Fix indentation
                    fixed_line = " " * last_indent + line.lstrip()
                    new_lines.append(fixed_line)
                    modified = True
                    # If it's a one-line docstring, we are done expecting
                    if stripped.count('"""') < 2 and stripped.count("'''") < 2:
                         # It is multi-line, so subsquent lines need fixing too
                         # But simplistic approach: just fix the start?
                         # The subsequent lines of the docstring usually follow the start indentation?
                         # Or maybe they are also unindented?
                         pass
                else:
                    new_lines.append(line)
            else:
                # Not a docstring, just append
                new_lines.append(line)
            expecting_docstring = False
            continue
            
        # Normal processing
        if stripped.startswith("def ") or stripped.startswith("class ") or stripped.startswith("async def "):
             if stripped.endswith(":"):
                 last_indent = indent + 4
                 expecting_docstring = True
        
        new_lines.append(line)
        
    if modified:
        return "\n".join(new_lines) + "\n", True
    return content, False

def fix_docstring_body_indentation(content):
    # This is harder because we need to know we are INSIDE a docstring.
    # The previous function only fixed the FIRST line.
    # If the BODY is unindented, we need to fix that too.
    # But let's rely on the fact that usually only the start is unindented if it was naively inserted?
    # Let's check the examples.
    # The example in cli_helpers.py showed the whole block unindented.
    
    # Alternative approach:
    # Use AST to find docstrings and re-format them? Too complex.
    # Regex approach:
    # Find `def .*:` then next line `"""` with wrong indentation.
    
    lines = content.splitlines()
    new_lines = []
    modified = False
    
    current_indent_fix = 0
    in_fix_block = False
    
    for line in lines:
        stripped = line.strip()
        indent = len(line) - len(line.lstrip())
        
        # Detect start of fix block
        # If previous line was def/class, and this line is """ and under-indented
        if len(new_lines) > 0:
            prev_line = new_lines[-1]
            prev_stripped = prev_line.strip()
            if (prev_stripped.startswith("def ") or prev_stripped.startswith("class ")) and prev_stripped.endswith(":"):
                expected_indent = len(prev_line) - len(prev_line.lstrip()) + 4
                if stripped.startswith('"""') and indent < expected_indent:
                    in_fix_block = True
                    current_indent_fix = expected_indent - indent
                    # Fix this line
                    line = " " * current_indent_fix + line
                    modified = True
        
        if in_fix_block:
            # We are in a block that needs indenting
            # But wait, if we process line by line, we might double indent?
            # No, because we only set in_fix_block if we detected start.
            # But for subsequent lines?
            if stripped.endswith('"""') and stripped != '"""': # End of docstring same line
                 in_fix_block = False
            elif stripped == '"""': # End of docstring next line
                 if not line.strip().startswith('"""'): # If it was modified above, it starts with spaces then """
                     # Check if this line ENDS the block
                     pass
                 
                 # Logic is getting messy.
                 pass
    
    # Let's stick to a simpler logic:
    # If we find `"""Brief description...` at column 4, but it should be at column 8.
    # We replace `    """` with `        """`.
    # And specifically for the known broken signature `"""Brief description`.
    
    pattern = r'(\n[ ]{4})"""Brief description'
    # This matches 4 spaces. If we want 8 spaces?
    # The broken files seem to have 4 spaces when they need 8.
    
    if re.search(pattern, content):
        # We need to be careful.
        pass
        
    return content, False

def robust_fix(file_path):
    try:
        content = file_path.read_text()
    except Exception:
        return False
        
    original_content = content
    
    # 1. Fix garbage docstrings
    content, fixed1 = fix_garbage_docstrings(content)
    
    # 2. Fix specific known indentation issues
    # The pattern in cli_helpers.py was:
    #     def decorator(func):
    #     """Brief description
    # 4 spaces for def, 4 spaces for docstring. Python needs 8 spaces for docstring.
    
    # We can use regex to find `def .*:\n\s*"""` and check indent.
    
    def replacer(match):
        def_indent = match.group(1)
        func_def = match.group(2)
        doc_indent = match.group(3)
        doc_start = match.group(4)
        
        if len(doc_indent) <= len(def_indent):
            # It is under-indented. Fix it.
            new_indent = def_indent + "    "
            return f"{def_indent}{func_def}\n{new_indent}{doc_start}"
        return match.group(0)

    # Regex:
    # Group 1: indent of def
    # Group 2: def ... :
    # Group 3: indent of docstring (next line)
    # Group 4: """...
    pattern = r'^([ ]*)(def .+?:)\n([ ]*)("""[\s\S]+?)$'
    # This regex is single-line match for the start.
    # But we need multi-line match.
    
    # Iterative replacement
    lines = content.splitlines()
    new_lines = []
    i = 0
    modified_indent = False
    
    while i < len(lines):
        line = lines[i]
        
        if i > 0:
            prev_line = lines[i-1]
            if prev_line.strip().startswith("def ") and prev_line.strip().endswith(":"):
                prev_indent = len(prev_line) - len(prev_line.lstrip())
                curr_indent = len(line) - len(line.lstrip())
                
                if line.strip().startswith('"""') and curr_indent <= prev_indent:
                    # Fix indentation for the whole docstring block
                    target_indent = prev_indent + 4
                    indent_diff = target_indent - curr_indent
                    
                    # Fix start line
                    new_lines.append(" " * indent_diff + line)
                    modified_indent = True
                    
                    # Fix subsequent lines until """
                    i += 1
                    while i < len(lines):
                        sub_line = lines[i]
                        sub_indent = len(sub_line) - len(sub_line.lstrip())
                        if sub_line.strip() == "": # Empty line
                            new_lines.append(sub_line)
                        else:
                            # If it matches the docstring closing, we fix and break
                            if sub_line.strip() == '"""' or sub_line.strip().endswith('"""'):
                                new_lines.append(" " * indent_diff + sub_line)
                                break
                            else:
                                new_lines.append(" " * indent_diff + sub_line)
                        i += 1
                    i += 1
                    continue

        new_lines.append(line)
        i += 1
        
    content = "\n".join(new_lines) + "\n"
    
    if fixed1 or modified_indent:
        # Also clean up double newlines that might result from garbage removal
        content = re.sub(r'\n{4,}', '\n\n', content)
        file_path.write_text(content)
        print(f"Fixed {file_path}")
        return True
        
    return False

def main():
    repo_root = Path(".")
    count = 0
    # Scan src folder
    for f in repo_root.glob("src/**/*.py"):
        if robust_fix(f):
            count += 1
            
    print(f"Fixed {count} files.")

if __name__ == "__main__":
    main()

import os
import re
from pathlib import Path

def clean_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except Exception as e:
        print(f"Skipping binary or unreadable file: {file_path}")
        return

    original_content = "".join(lines)
    new_lines = []
    modified = False
    
    # 1. Remove "Core functionality module" blocks
    # Pattern: # This might be at start of file or anywhere
    content = "".join(lines)
    
    # Regex for "Core functionality module" block
    # Matches """Core func...""" including newlines
    garbage_pattern = re.compile(r'\s*', re.DOTALL)
    
    if garbage_pattern.search(content):
        # print(f"Removing 'Core functionality module' from: {file_path}")
        content = garbage_pattern.sub('', content)
        modified = True

    # 2. Fix broken header docstrings (Execution Monitoring case)
    # Pattern: Line starts with "Execution Monitoring", has no opening """, ends with """ later
    # Heuristic: If first few non-empty lines are text and then """ follows, wrap it.
    if "src/codomyrmex/coding/monitoring/execution_monitor.py" in str(file_path):
        # Specific patch for this known failure
        if content.startswith("from typing") and "Execution Monitoring" in content:
            # check if syntax error likely
            pass # Too risky to regex broadly, relying on specific file matching or detailed parse?
            # Actually, let's just use replace for this known file string
            if "\nExecution Monitoring\n" in content:
                 content = content.replace("\nExecution Monitoring\n", '\n"""\nExecution Monitoring\n')
                 modified = True

    # 3. Indentation fix for rogue docstrings
    # Process line by line to handle indentation
    
    # We need to reconstruct lines from 'content' first if modified
    lines = content.splitlines(keepends=True)
    final_lines = []
    
    i = 0
    while i < len(lines):
        line = lines[i]
        
        # Check for def/class definition
        # Regex to capture indent
        def_match = re.match(r'^(\s*)(def|class)\s+', line)
        if def_match:
            final_lines.append(line)
            def_indent = def_match.group(1)
            target_indent = def_indent + "    "
            
            # Check next line
            if i + 1 < len(lines):
                next_line = lines[i+1]
                # If next line starts with """ and has SAME indentation as def (bad)
                # Matches """Brief description... or similar
                if next_line.startswith(def_indent + '"""') and not next_line.startswith(target_indent):
                    # Found under-indented docstring!
                    # print(f"Fixing indentation in {file_path} at line {i+2}")
                    modified = True
                    
                    # Indent this line and subsequent lines until closing """
                    # Note: closing """ might be on same line or later
                    
                    # Indent the first line
                    final_lines.append(target_indent + next_line.lstrip())
                    i += 1
                    
                    # If single line docstring, we are done
                    if next_line.strip().count('"""') >= 2 and next_line.strip().endswith('"""'):
                        continue
                        
                    # Multi-line: consume until closing """
                    while i + 1 < len(lines):
                        curr_doc_line = lines[i+1]
                        # Indent it
                        final_lines.append(target_indent + curr_doc_line)
                        i += 1
                        if '"""' in curr_doc_line:
                            break
                    continue
                else:
                    pass
        else:
            final_lines.append(line)
        i += 1
        
    if modified:
        print(f"Fixed {file_path}")
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write("".join(final_lines))

def main():
    roots = ['src', 'scripts']
    for root in roots:
        for path in Path(root).rglob('*.py'):
            clean_file(path)

if __name__ == "__main__":
    main()

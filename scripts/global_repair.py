
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
    content = original_content
    modified = False
    
    # 1. Remove "Core functionality module" blocks
    garbage_pattern = re.compile(r'\s*', re.DOTALL)
    if garbage_pattern.search(content):
        # print(f"Removing 'Core functionality module' from: {file_path}")
        content = garbage_pattern.sub('', content)
        modified = True

    # 4. Remove Docstrings INSIDE arguments
    # Pattern: def func(\n   """Doc..."""\n
    # Regex: Look for ( followed by newline, then optional whitespace, then """, then content, then """, then newline
    # Be careful not to match valid strings.
    # The corruption seems to be:
    # def func(
    #     """Brief...
    #     ...
    #     """
    # """  <-- sometimes extra quote
    #     arg1,
    
    # Regex for standard "Brief description" inside args
    # Matches: ( \n \s* """ ... """ \n
    inside_args_pattern = re.compile(r'(\(\s*\n)\s*"""(?:Brief description|From Dict|With Overrides|Return a string|Convert the exception|Initialize).*?"""\s*\n', re.DOTALL)
    
    if inside_args_pattern.search(content):
        print(f"Fixing docstring-inside-args in: {file_path}")
        content = inside_args_pattern.sub(r'\1', content)
        modified = True
        
    # Also check for the double-quote issue seen in exceptions.py where there was an extra """ line
    # Pattern: """\n"""\n inside args? Or just after the docstring?
    # In exceptions.py it was: """Brief...\n...\n"""\n"""\n
    inside_args_double_pattern = re.compile(r'(\(\s*\n)\s*"""(?:Brief description).*?"""\n"""\s*\n', re.DOTALL)
    if inside_args_double_pattern.search(content):
         print(f"Fixing double-docstring-inside-args in: {file_path}")
         content = inside_args_double_pattern.sub(r'\1', content)
         modified = True

    # 2. Fix broken header docstrings (Execution Monitoring case)
    if "src/codomyrmex/coding/monitoring/execution_monitor.py" in str(file_path):
        if content.startswith("from typing") and "\nExecution Monitoring\n" in content and '"""\nExecution Monitoring\n' not in content:
             content = content.replace("\nExecution Monitoring\n", '\n"""\nExecution Monitoring\n')
             modified = True

    # 3. Indentation fix for rogue docstrings (ONLY if not inside args - difficult to distinguish with simple regex, but let's re-run it)
    # The previous logic for indentation was good for function bodies.
    # Re-running it on cleaned content.
    
    lines = content.splitlines(keepends=True)
    final_lines = []
    
    i = 0
    while i < len(lines):
        line = lines[i]
        def_match = re.match(r'^(\s*)(def|class)\s+', line)
        if def_match:
            final_lines.append(line)
            def_indent = def_match.group(1)
            target_indent = def_indent + "    "
            
            if i + 1 < len(lines):
                next_line = lines[i+1]
                if next_line.startswith(def_indent + '"""') and not next_line.startswith(target_indent):
                    # Found under-indented docstring!
                    modified = True
                    final_lines.append(target_indent + next_line.lstrip())
                    i += 1
                    if next_line.strip().count('"""') >= 2 and next_line.strip().endswith('"""'):
                        continue
                    while i + 1 < len(lines):
                        curr_doc_line = lines[i+1]
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
        
    content = "".join(final_lines)

    if modified:
        print(f"Fixed {file_path}")
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)

def main():
    roots = ['src', 'scripts']
    for root in roots:
        for path in Path(root).rglob('*.py'):
            clean_file(path)

if __name__ == "__main__":
    main()


import os
import re
from pathlib import Path

def check_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except:
        return

    for i, line in enumerate(lines):
        if re.match(r'\s*def\s+.*?\(\s*$', line.rstrip()):
            # Function def opening
            # Check next few lines for """
            j = i + 1
            while j < len(lines) and j < i + 10: # Check next 10 lines
                next_line = lines[j].strip()
                if next_line.startswith('"""'):
                    # Found docstring quote. Is it before closing paren?
                    # Naively, if we haven't seen ): yet.
                    # But checking if we are inside parens is better.
                    # Simple heuristic: if previous line ended with (, or , and this line starts with """, it's suspicious.
                    prev_line = lines[j-1].rstrip()
                    if prev_line.endswith('(') or prev_line.endswith(','):
                        print(f"SUSPICIOUS: {file_path}:{j+1} - Docstring inside args?")
                        print(f"  {lines[i].strip()}")
                        print(f"  {lines[j].strip()[:20]}...")
                if '):' in lines[j]:
                    break
                j += 1

def main():
    roots = ['src', 'scripts']
    for root in roots:
        for path in Path(root).rglob('*.py'):
            check_file(path)

if __name__ == "__main__":
    main()

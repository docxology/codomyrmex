import os
import re

def titleize(name):
    """Convert folder name like 'git_operations' to 'Git Operations'"""
    return " ".join(word.capitalize() for word in name.replace("-", "_").split("_"))

def fix_file(filepath, folder_name):
    title = titleize(folder_name)
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
        
    original = content
        
    # 1. Replace "Codomyrmex Root" with the actual title
    content = content.replace("Codomyrmex Root", title)
    
    # 2. Ensure version string exists or replace old ones
    version_string = "**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026\n"
    
    # Replace any existing version string
    content = re.sub(r'\*\*Version\*\*:.*?\n', '', content)
    
    # Insert version string after the first header if it's not a PAI.md (PAI.md has its own format we already fixed mostly, but we should fix nested ones too)
    lines = content.split('\n')
    for i, line in enumerate(lines):
        if line.startswith('# '):
            lines.insert(i + 1, '\n' + version_string)
            break
            
    content = '\n'.join(lines)
    
    # Clean up multiple newlines that might have been introduced
    content = re.sub(r'\n{3,}', '\n\n', content)
    
    if content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False

def main():
    base_dir = "src/codomyrmex"
    fixed_count = 0
    scanned_count = 0
    
    for root, dirs, files in os.walk(base_dir):
        # Skip the top-level Codomyrmex root itself, we just want subfolders
        if root == base_dir:
            continue
            
        folder_name = os.path.basename(root)
        if folder_name.startswith('__'):
            continue
            
        for file in files:
            if file in ("README.md", "AGENTS.md", "SPEC.md", "PAI.md"):
                filepath = os.path.join(root, file)
                scanned_count += 1
                if fix_file(filepath, folder_name):
                    fixed_count += 1
                    
                if scanned_count % 1000 == 0:
                    print(f"Scanned {scanned_count} files, fixed {fixed_count}...")
                    
    print(f"Done! Scanned {scanned_count} RASP files, fixed {fixed_count} files.")

if __name__ == "__main__":
    main()

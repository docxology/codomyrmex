import os
import re
import sys

from codomyrmex.utils.cli_helpers import print_info, print_success, setup_logging

def titleize(name):
    return " ".join(word.capitalize() for word in name.replace("-", "_").split("_"))

def fix_file(filepath, folder_name):
    title = titleize(folder_name)
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    original = content
    content = content.replace("Codomyrmex Root", title)
    version_string = "**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026\n"
    content = re.sub(r'\*\*Version\*\*:.*?\n', '', content)

    lines = content.split('\n')
    for i, line in enumerate(lines):
        if line.startswith('# '):
            lines.insert(i + 1, '\n' + version_string)
            break

    content = '\n'.join(lines)
    content = re.sub(r'\n{3,}', '\n\n', content)

    if content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False

def main() -> int:
    setup_logging()
    base_dir = "src/codomyrmex.llm"
    fixed_count = 0
    scanned_count = 0

    print_info(f"Scanning RASP files in {base_dir}...")
    for root, dirs, files in os.walk(base_dir):
        if "node_modules" in root or "vendor" in root:
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

    print_success(f"Done! Scanned {scanned_count} RASP files in codomyrmex.llm, fixed {fixed_count} files.")
    return 0

if __name__ == "__main__":
    sys.exit(main())

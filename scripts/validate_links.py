import os
import re
import urllib.parse
from pathlib import Path

def validate_links(root_dir):
    root_path = Path(root_dir).resolve()
    markdown_files = list(root_path.rglob("*.md"))
    
    # Regex for markdown links: [text](link)
    link_pattern = re.compile(r'\[([^\]]+)\]\(([^)]+)\)')
    
    broken_links = []
    checked_count = 0
    file_count = 0

    print(f"Scanning {len(markdown_files)} markdown files in {root_path}...")

    for md_file in markdown_files:
        file_count += 1
        try:
            content = md_file.read_text(encoding='utf-8')
        except Exception as e:
            print(f"Error reading {md_file}: {e}")
            continue

        matches = link_pattern.findall(content)
        for text, target in matches:
            # Ignore anchors only
            if target.startswith('#'):
                continue
            
            # Ignore absolute URLs (http, https, mailto)
            if re.match(r'^(http|https|mailto):', target):
                continue
            
            checked_count += 1
            
            # Handle anchors in file paths (e.g. file.md#section)
            target_file = target.split('#')[0]
            if not target_file:
                continue

            # Resolve path
            # If starts with /, it's relative to project root? Usually md links are relative to file.
            # But let's assume relative to file.
            
            if target_file.startswith('/'):
                 # Assuming absolute path on disk? No, usually not in git repos.
                 # Let's assume relative to root if it starts with / (uncommon in standard md but possible)
                 # Actually, standard markdown: / implies root.
                 potential_path = root_path / target_file.lstrip('/')
            else:
                potential_path = (md_file.parent / target_file).resolve()
            
            if not potential_path.exists():
                # Check if it is a directory?
                if not potential_path.is_dir() and not potential_path.is_file():
                     broken_links.append({
                         'file': str(md_file.relative_to(root_path)),
                         'link_text': text,
                         'target': target,
                         'resolved': str(potential_path)
                     })

    return broken_links, checked_count

if __name__ == "__main__":
    broken, count = validate_links(".")
    print(f"Checked {count} links.")
    if broken:
        print(f"Found {len(broken)} broken links:")
        for b in broken[:20]: # Show first 20
            print(f"  In {b['file']}: [{b['link_text']}]({b['target']}) -> Not found")
        if len(broken) > 20:
            print(f"... and {len(broken) - 20} more.")
        exit(1)
    else:
        print("All internal links validated successfully!")
        exit(0)

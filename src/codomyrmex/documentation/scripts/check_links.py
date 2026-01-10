from pathlib import Path
import os
import re
from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)

def find_markdown_files(root_dir):
    """Recursively find all markdown files in a directory."""
    return list(Path(root_dir).rglob("*.md"))

def check_links(root_dir):
    """
    Check for broken links in markdown files.

        root_dir: Directory to scan

    Returns:
        List of dictionaries containing broken link details
    """
    root_path = Path(root_dir).absolute()
    link_pattern = re.compile(r'\[([^\]]+)\]\(([^)]+)\)')
    broken_links = []
    
    for md_file in find_markdown_files(root_path):
        with open(md_file, "r", encoding="utf-8") as f:
            content = f.read()
            
        for match in link_pattern.finditer(content):
            text, link = match.groups()
            
            # Skip external links
            if link.startswith("http") or link.startswith("mailto:"):
                continue
            
            # Skip anchor links within same file (simplified)
            if link.startswith("#"):
                continue
                
            # Handle links with anchors
            clean_link = link.split("#")[0]
            if not clean_link:
                continue
                
            # Resolve target path relative to current markdown file
            target = (md_file.parent / clean_link).resolve()
            
            if not target.exists():
                broken_links.append({
                    "file": str(md_file.relative_to(root_path)),
                    "link": link,
                    "text": text,
                    "target": str(target)
                })
                
    return broken_links

if __name__ == "__main__":
    root = os.getcwd()
    print(f"Checking links in {root}...")
    broken = check_links(root)
    if broken:
        print(f"Found {len(broken)} broken links:")
        for b in broken:
            print(f"- {b['file']}: [{b['text']}]({b['link']}) -> {b['target']}")
    else:
        print("No broken links found!")

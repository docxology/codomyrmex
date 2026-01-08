from pathlib import Path
import os
import re

from check_links import FunctionName, ClassName





























#!/usr/bin/env python3

"""Core functionality module

This module provides check_links functionality including:
- 2 functions: find_markdown_files, check_links
- 0 classes: 

Usage:
    # Example usage here
"""
def find_markdown_files(root_dir):
    """Brief description of find_markdown_files.

Args:
    root_dir : Description of root_dir

    Returns: Description of return value
"""
    for root, dirs, files in os.walk(root_dir):
        for file in files:
            if file.endswith(".md"):
                yield Path(root) / file

def check_links(root_dir):
    """Brief description of check_links.

Args:
    root_dir : Description of root_dir

    Returns: Description of return value
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

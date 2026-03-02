import os
import re
import sys
from pathlib import Path

from codomyrmex.logging_monitoring import get_logger

"""
Documentation Link Validation Script

This script validates all internal markdown links in the documentation directory,
identifying broken links, missing files, and incorrect references.
"""




logger = get_logger(__name__)

def find_markdown_files(docs_dir: Path) -> list[Path]:
    """Find all markdown files in the documentation directory."""
    markdown_files = []
    for root, dirs, files in os.walk(docs_dir):
        # Skip hidden directories
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        for file in files:
            if file.endswith('.md'):
                markdown_files.append(Path(root) / file)
    return sorted(markdown_files)


def extract_links(content: str, file_path: Path) -> list[tuple[str, int, str]]:
    """
    Extract all markdown links from content.

    Returns: List of tuples (link_text, line_number, link_url)
    """
    links = []

    # Pattern for markdown links: [text](url) or [text](url "title")
    link_pattern = r'\[([^\]]+)\]\(([^)]+)\)'

    for line_num, line in enumerate(content.split('\n'), start=1):
        for match in re.finditer(link_pattern, line):
            link_text = match.group(1)
            link_url = match.group(2)
            # Remove title if present: "url" -> url
            if link_url.startswith('"') and link_url.endswith('"'):
                link_url = link_url[1:-1]
            links.append((link_text, line_num, link_url))

    return links


def resolve_link(link_url: str, from_file: Path, docs_root: Path) -> tuple[bool, str]:
    """
    Resolve a relative link to an absolute path and check if it exists.

    Returns: (exists, resolved_path)
    """
    # Skip external links
    if link_url.startswith('http://') or link_url.startswith('https://') or link_url.startswith('mailto:'):
        return (True, 'external')  # Assume external links are valid

    # Skip anchor-only links
    if link_url.startswith('#'):
        return (True, 'anchor')

    # Remove anchor from URL if present
    if '#' in link_url:
        link_url = link_url.split('#')[0]

    # Handle relative paths
    if link_url.startswith('./'):
        link_url = link_url[2:]

    # Get project root (parent of docs) - resolve to absolute path
    project_root = docs_root.parent.resolve()

    # Resolve relative to current file's directory
    if link_url.startswith('../'):
        # Count how many levels up by counting '../' sequences
        levels_up = link_url.count('../')
        current_dir = from_file.parent.resolve()
        # Go up the specified number of levels
        for _ in range(levels_up):
            # Stop if we've reached the project root (don't go beyond it)
            if current_dir == project_root:
                break
            parent = current_dir.parent
            # Only go up if we're still within the project root
            if str(parent).startswith(str(project_root)) or parent == project_root:
                current_dir = parent
            else:
                # Would go beyond project root, stop here
                break
        while link_url.startswith('../'):
            link_url = link_url.removeprefix('../')
        resolved = current_dir / link_url
    elif link_url.startswith('/'):
        # Absolute from docs root
        resolved = docs_root / link_url.lstrip('/')
    else:
        # Relative to current file's directory
        resolved = from_file.parent / link_url

    # Normalize path
    try:
        resolved = resolved.resolve()
        docs_root = docs_root.resolve()
    except Exception as e:
        # Path might not exist, but we can still check
        logger.debug("Path resolution failed for %s: %s", link_url, e)
        pass

    # Check if file or directory exists (allow both)
    exists = resolved.exists() and (resolved.is_file() or resolved.is_dir())

    # If path goes outside docs, check if it's within project root
    resolved_str = str(resolved)
    docs_root_str = str(docs_root)
    project_root_str = str(project_root.resolve())

    if not exists:
        if not resolved_str.startswith(docs_root_str) and resolved_str.startswith(project_root_str):
            # Link to file outside docs but within project - check if it exists
            exists = resolved.exists() and (resolved.is_file() or resolved.is_dir())
            if exists:
                return (True, f'external:{resolved.relative_to(project_root)}')
            else:
                # File doesn't exist, return the broken link info
                return (False, str(resolved))
    elif not resolved_str.startswith(docs_root_str) and resolved_str.startswith(project_root_str):
        # File exists and is outside docs but within project - valid external link
        return (True, f'external:{resolved.relative_to(project_root)}')

    return (exists, str(resolved.relative_to(docs_root)) if resolved_str.startswith(docs_root_str) else str(resolved))


def check_links(docs_dir: Path) -> dict[str, list[dict]]:
    """
    Check all links in documentation files.

    Returns: Dictionary with file paths as keys and list of link issues as values
    """
    issues = {}
    markdown_files = find_markdown_files(docs_dir)

    for file_path in markdown_files:
        try:
            content = file_path.read_text(encoding='utf-8')
            links = extract_links(content, file_path)

            file_issues = []
            for link_text, line_num, link_url in links:
                exists, resolved = resolve_link(link_url, file_path, docs_dir)
                if not exists:
                    file_issues.append({
                        'line': line_num,
                        'text': link_text,
                        'url': link_url,
                        'resolved': resolved,
                        'issue': 'broken_link'
                    })

            if file_issues:
                issues[str(file_path.relative_to(docs_dir))] = file_issues

        except Exception as e:
            issues[str(file_path.relative_to(docs_dir))] = [{
                'line': 0,
                'text': '',
                'url': '',
                'resolved': '',
                'issue': f'error_reading_file: {str(e)}'
            }]

    return issues


def main():
    """Main function to run link validation."""
    # Get docs directory (assume script is in scripts/documentation/)
    script_dir = Path(__file__).resolve().parent
    # Go up 5 levels: scripts -> documentation -> codomyrmex -> src -> codomyrmex -> repo_root
    # Wait, __file__ is src/codomyrmex/documentation/scripts/check_doc_links.py
    # 1. scripts
    # 2. documentation
    # 3. codomyrmex
    # 4. src
    # 5. REPO_ROOT
    project_root = script_dir.parent.parent.parent.parent
    docs_dir = project_root / 'docs'

    if not docs_dir.exists():
        print(f"Error: Documentation directory not found: {docs_dir}")
        sys.exit(1)

    print(f"Checking links in: {docs_dir}")
    print("=" * 80)

    issues = check_links(docs_dir)

    if not issues:
        print("✅ All links are valid!")
        return 0

    print(f"\n❌ Found {sum(len(v) for v in issues.values())} link issues in {len(issues)} files:\n")

    for file_path, file_issues in sorted(issues.items()):
        print(f"\n📄 {file_path}:")
        for issue in file_issues:
            if issue['issue'] == 'broken_link':
                print(f"  Line {issue['line']}: [{issue['text']}]({issue['url']})")
                print(f"    → Broken link to: {issue['resolved']}")
            else:
                print(f"  {issue['issue']}")

    return 0


if __name__ == '__main__':
    sys.exit(main())

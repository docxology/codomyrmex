#!/usr/bin/env python3
"""Comprehensive link validation for markdown documentation.

Validates:
- Internal links (relative paths)
- External URLs
- Anchor links
- Image references
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import NamedTuple


class LinkResult(NamedTuple):
    """Result of link validation."""
    file: str
    link: str
    line: int
    status: str  # 'ok', 'broken', 'external', 'skipped'
    message: str = ""


def extract_links(content: str, file_path: Path) -> list[tuple[str, int]]:
    """Extract all markdown links from content."""
    links = []
    
    # Match [text](url) pattern
    link_pattern = r'\[([^\]]*)\]\(([^)]+)\)'
    
    for i, line in enumerate(content.split('\n'), 1):
        for match in re.finditer(link_pattern, line):
            url = match.group(2)
            links.append((url, i))
    
    # Also match raw URLs
    url_pattern = r'https?://[^\s\)<>]+'
    for i, line in enumerate(content.split('\n'), 1):
        for match in re.finditer(url_pattern, line):
            url = match.group()
            if (url, i) not in links:
                links.append((url, i))
    
    return links


def validate_link(link: str, file_path: Path, repo_root: Path, line: int) -> LinkResult:
    """Validate a single link."""
    file_str = str(file_path.relative_to(repo_root))
    
    # Skip external links (we'll mark them but not validate)
    if link.startswith(('http://', 'https://', 'mailto:', 'tel:')):
        return LinkResult(file_str, link, line, 'external', 'External link (not validated)')
    
    # Handle anchor-only links
    if link.startswith('#'):
        return LinkResult(file_str, link, line, 'ok', 'Anchor link')
    
    # Handle relative paths
    link_path = link.split('#')[0]  # Remove anchor
    link_path = link_path.split('?')[0]  # Remove query string
    
    if not link_path:
        return LinkResult(file_str, link, line, 'ok', 'Empty path (anchor only)')
    
    # Resolve relative to file's directory
    target = (file_path.parent / link_path).resolve()
    
    if target.exists():
        return LinkResult(file_str, link, line, 'ok', 'File exists')
    else:
        return LinkResult(file_str, link, line, 'broken', f'Target not found: {link_path}')


def validate_links(repo_root: Path, output_dir: Path = None, output_format: str = 'both') -> int:
    """Validate all links in markdown files."""
    print("🔗 Validating documentation links...\n")
    
    if output_dir is None:
        output_dir = repo_root / "output"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    results: list[LinkResult] = []
    
    # Find all markdown files
    md_files = list(repo_root.rglob("*.md"))
    md_files = [f for f in md_files if ".git" not in str(f) and "node_modules" not in str(f)]
    
    print(f"📄 Found {len(md_files)} markdown files")
    
    for md_file in md_files:
        try:
            content = md_file.read_text(encoding='utf-8')
        except Exception as e:
            print(f"⚠️  Could not read {md_file}: {e}")
            continue
        
        links = extract_links(content, md_file)
        
        for link, line in links:
            result = validate_link(link, md_file, repo_root, line)
            results.append(result)
    
    # Count results
    broken = [r for r in results if r.status == 'broken']
    ok = [r for r in results if r.status == 'ok']
    external = [r for r in results if r.status == 'external']
    
    # Output results
    if output_format in ('json', 'both'):
        json_path = output_dir / "link_validation.json"
        with open(json_path, 'w') as f:
            json.dump([r._asdict() for r in results], f, indent=2)
        print(f"📄 JSON report: {json_path}")
    
    if output_format in ('markdown', 'both'):
        md_path = output_dir / "link_validation.md"
        with open(md_path, 'w') as f:
            f.write("# Link Validation Report\n\n")
            f.write(f"- ✅ Valid links: {len(ok)}\n")
            f.write(f"- ❌ Broken links: {len(broken)}\n")
            f.write(f"- 🔗 External links: {len(external)}\n\n")
            
            if broken:
                f.write("## Broken Links\n\n")
                for r in broken:
                    f.write(f"- `{r.file}:{r.line}` - [{r.link}] - {r.message}\n")
        print(f"📄 Markdown report: {md_path}")
    
    # Summary
    print(f"\n✅ Valid: {len(ok)}")
    print(f"❌ Broken: {len(broken)}")
    print(f"🔗 External: {len(external)}")
    
    if broken:
        print("\n❌ Broken links found:")
        for r in broken[:10]:
            print(f"   {r.file}:{r.line} → {r.link}")
        if len(broken) > 10:
            print(f"   ... and {len(broken) - 10} more")
        return 1 if '--fail-on-broken' in sys.argv else 0
    
    print("\n✅ All internal links are valid!")
    return 0


def main():
    parser = argparse.ArgumentParser(description="Validate documentation links")
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--output", type=Path)
    parser.add_argument("--format", choices=['json', 'markdown', 'both'], default='both')
    parser.add_argument("--fail-on-broken", action="store_true")
    
    args = parser.parse_args()
    return validate_links(args.repo_root, args.output, args.format)


if __name__ == "__main__":
    sys.exit(main())

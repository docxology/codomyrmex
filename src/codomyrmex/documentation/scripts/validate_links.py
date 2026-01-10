from pathlib import Path
from typing import List, Tuple
import re

from codomyrmex.logging_monitoring import get_logger




















"""
Validate all internal links in README.md and AGENTS.md files.
"""




logger = get_logger(__name__)

REPO_ROOT = Path(__file__).parent.parent.parent

def find_markdown_links(content: str) -> List[Tuple[str, str]]:
    """Find all markdown links in content."""
    # Pattern: [text](path)
    pattern = r'\[([^\]]+)\]\(([^)]+)\)'
    return re.findall(pattern, content)

def resolve_link(base_path: Path, link: str) -> Path:
    """Resolve a relative link to an absolute path."""
    # Remove anchors
    link = link.split('#')[0]
    
    if not link:
        return None
    
    # Absolute links (starting with /)
    if link.startswith('/'):
        return REPO_ROOT / link.lstrip('/')
    
    # Relative links
    if base_path.is_file():
        base_dir = base_path.parent
    else:
        base_dir = base_path
    
    # Handle parent directory references
    resolved = (base_dir / link).resolve()
    
    # Check if within repo
    try:
        resolved.relative_to(REPO_ROOT)
        return resolved
    except ValueError:
        return None

def validate_file(filepath: Path) -> List[Tuple[str, str]]:
    """Validate links in a file."""
    if not filepath.exists():
        return []
    
    content = filepath.read_text(encoding='utf-8', errors='ignore')
    links = find_markdown_links(content)
    
    broken = []
    for text, link in links:
        # Skip external links
        if link.startswith('http://') or link.startswith('https://') or link.startswith('mailto:'):
            continue
        
        resolved = resolve_link(filepath, link)
        if resolved is None or not resolved.exists():
            broken.append((link, text))
    
    return broken

def main():
    """Validate all documentation files."""
    readme_files = list(REPO_ROOT.rglob("README.md"))
    agents_files = list(REPO_ROOT.rglob("AGENTS.md"))
    
    all_files = [f for f in readme_files + agents_files 
                 if ".venv" not in str(f) and "node_modules" not in str(f)]
    
    total_broken = 0
    files_with_issues = []
    
    for filepath in all_files:
        broken = validate_file(filepath)
        if broken:
            total_broken += len(broken)
            files_with_issues.append((filepath.relative_to(REPO_ROOT), broken))
    
    if files_with_issues:
        print(f"Found {total_broken} broken links in {len(files_with_issues)} files:\n")
        for filepath, broken in files_with_issues[:20]:  # Show first 20
            print(f"{filepath}:")
            for link, text in broken:
                print(f"  - [{text}]({link})")
        if len(files_with_issues) > 20:
            print(f"\n... and {len(files_with_issues) - 20} more files")
    else:
        print("All links validated successfully!")

if __name__ == "__main__":
    main()

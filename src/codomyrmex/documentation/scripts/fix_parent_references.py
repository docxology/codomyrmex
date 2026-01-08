from pathlib import Path
from typing import Dict, Optional
import re




#!/usr/bin/env python3
"""
Fix all generic [Parent] references in AGENTS.md files with descriptive labels.
"""


def determine_parent_label(file_path: Path, repo_root: Path) -> str:
    """Determine the appropriate parent label based on file location."""
    relative_path = file_path.relative_to(repo_root)
    parts = relative_path.parts
    
    # Root level AGENTS.md has no parent
    if len(parts) == 1:
        return None
    
    # Get parent directory name
    parent_dir = parts[-2] if len(parts) > 1 else None
    
    # Special cases for top-level directories
    if len(parts) == 2:
        # Top-level directories: use "Repository Root"
        return "Repository Root"
    
    # For nested directories, use the parent directory name
    # Capitalize and format nicely
    if parent_dir:
        # Handle special cases
        if parent_dir == 'codomyrmex':
            return "Source Root"
        elif parent_dir == 'src':
            return "Source Root"
        elif parent_dir == 'docs':
            return "Documentation Root"
        elif parent_dir == 'scripts':
            return "Scripts Root"
        elif parent_dir == 'examples':
            return "Examples Root"
        elif parent_dir == 'output':
            return "Output Root"
        elif parent_dir == 'config':
            return "Configuration Root"
        elif parent_dir == 'cursorrules':
            return "Cursor Rules Root"
        elif parent_dir == 'projects':
            return "Projects Root"
        elif parent_dir == 'testing':
            return "Testing Root"
        elif parent_dir == 'plugins':
            return "Plugins Root"
        else:
            # Use parent directory name, capitalized
            return parent_dir.replace('_', ' ').title()
    
    return "Parent Directory"

def fix_parent_reference(content: str, file_path: Path, repo_root: Path) -> tuple[str, bool]:
    """Fix parent reference in content. Returns (new_content, was_changed)."""
    pattern = r'- \*\*Parent\*\*: \[Parent\]\(([^)]+)\)'
    match = re.search(pattern, content)
    
    if not match:
        return content, False
    
    parent_label = determine_parent_label(file_path, repo_root)
    if parent_label is None:
        # No parent (root level)
        return content, False
    
    new_reference = f'- **Parent**: [{parent_label}]({match.group(1)})'
    new_content = content[:match.start()] + new_reference + content[match.end():]
    return new_content, True

def main():
    """Main function to fix all parent references."""
    repo_root = Path(__file__).parent.parent.parent
    
    # Find all AGENTS.md files
    agents_files = []
    for path in repo_root.rglob("AGENTS.md"):
        if ".venv" in str(path) or "node_modules" in str(path):
            continue
        agents_files.append(path)
    
    print(f"Found {len(agents_files)} AGENTS.md files")
    
    fixed_count = 0
    for agents_file in sorted(agents_files):
        try:
            content = agents_file.read_text(encoding='utf-8')
            new_content, was_changed = fix_parent_reference(content, agents_file, repo_root)
            
            if was_changed:
                agents_file.write_text(new_content, encoding='utf-8')
                fixed_count += 1
                print(f"  Fixed: {agents_file.relative_to(repo_root)}")
        except Exception as e:
            print(f"  Error processing {agents_file.relative_to(repo_root)}: {e}")
    
    print(f"\nFixed {fixed_count} files")

if __name__ == '__main__':
    main()


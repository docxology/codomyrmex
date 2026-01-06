#!/usr/bin/env python3
"""Add missing navigation links to documentation files."""

import re
from pathlib import Path

def calculate_paths(file_path: Path, base_path: Path) -> dict:
    """Calculate all necessary relative paths."""
    rel_path = file_path.parent.relative_to(base_path)
    depth = len(rel_path.parts)
    
    paths = {
        'root': "../" * depth + "README.md" if depth > 0 else "README.md",
        'spec': "../" * depth + "SPEC.md" if depth > 0 else "SPEC.md",
        'parent': "../README.md" if depth > 0 else "README.md",
        'parent_spec': "../SPEC.md" if depth > 0 else "SPEC.md",
    }
    
    return paths

def add_navigation_links(file_path: Path, base_path: Path) -> bool:
    """Add missing navigation links to a file."""
    if not file_path.exists():
        return False
    
    try:
        content = file_path.read_text(encoding='utf-8')
        original = content
        file_name = file_path.name
        paths = calculate_paths(file_path, base_path)
        
        # Check if Navigation section exists
        has_nav_section = "## Navigation" in content or "## Navigation Links" in content
        
        # Determine what links should exist
        needs_readme = file_name != "README.md" and "README.md" not in content
        needs_agents = file_name != "AGENTS.md" and "AGENTS.md" not in content
        needs_spec = file_name != "SPEC.md" and "SPEC.md" not in content
        
        if not has_nav_section and (needs_readme or needs_agents or needs_spec):
            # Add Navigation section before end of file or before last section
            nav_section = "\n## Navigation\n\n"
            
            if file_name == "README.md":
                nav_section += "- **Technical Documentation**: [AGENTS.md](AGENTS.md)\n"
                nav_section += "- **Functional Specification**: [SPEC.md](SPEC.md)\n"
            elif file_name == "AGENTS.md":
                nav_section += "- **Human Documentation**: [README.md](README.md)\n"
                nav_section += "- **Functional Specification**: [SPEC.md](SPEC.md)\n"
            elif file_name == "SPEC.md":
                nav_section += "- **Human Documentation**: [README.md](README.md)\n"
                nav_section += "- **Technical Documentation**: [AGENTS.md](AGENTS.md)\n"
            
            # Add parent and root links
            if file_path.parent != base_path:
                parent_name = file_path.parent.name
                nav_section += f"- **Parent Directory**: [{parent_name}]({paths['parent']})\n"
                if file_path.parent / "SPEC.md" != file_path:
                    nav_section += f"- **Parent SPEC**: [{paths['parent_spec']}]({paths['parent_spec']})\n"
            
            nav_section += f"- **Repository Root**: [{paths['root']}]({paths['root']})\n"
            if depth > 0:
                nav_section += f"- **Repository SPEC**: [{paths['spec']}]({paths['spec']})\n"
            
            # Add before last line or at end
            content = content.rstrip() + "\n" + nav_section
        elif has_nav_section:
            # Enhance existing navigation section
            if file_name == "README.md":
                if "AGENTS.md" not in content and "AGENTS" not in content:
                    # Add after Navigation header
                    content = re.sub(
                        r'(## Navigation[^\n]*\n)',
                        r'\1- **Technical Documentation**: [AGENTS.md](AGENTS.md)\n- **Functional Specification**: [SPEC.md](SPEC.md)\n',
                        content,
                        count=1
                    )
            elif file_name == "AGENTS.md":
                if "README.md" not in content and "README" not in content:
                    content = re.sub(
                        r'(## Navigation[^\n]*\n)',
                        r'\1- **Human Documentation**: [README.md](README.md)\n- **Functional Specification**: [SPEC.md](SPEC.md)\n',
                        content,
                        count=1
                    )
            elif file_name == "SPEC.md":
                if "README.md" not in content and "README" not in content:
                    content = re.sub(
                        r'(## Navigation[^\n]*\n)',
                        r'\1- **Human Documentation**: [README.md](README.md)\n- **Technical Documentation**: [AGENTS.md](AGENTS.md)\n',
                        content,
                        count=1
                    )
        
        if content != original:
            file_path.write_text(content, encoding='utf-8')
            return True
        return False
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False

def main():
    """Add missing navigation links."""
    base_path = Path("/Users/mini/Documents/GitHub/codomyrmex")
    fixed_count = 0
    
    for root, dirs, files in os.walk(base_path):
        dirs[:] = [d for d in dirs if not d.startswith('.') and 
                   d not in ['__pycache__', 'node_modules', 'venv', '.venv', '.git', '@output']]
        
        for file in ['README.md', 'AGENTS.md', 'SPEC.md']:
            file_path = Path(root) / file
            if file_path.exists() and file_path.parent != base_path:
                if add_navigation_links(file_path, base_path):
                    fixed_count += 1
                    if fixed_count % 20 == 0:
                        print(f"Fixed {fixed_count} files...")
    
    print(f"\nCompleted: Fixed {fixed_count} files with navigation links")

if __name__ == "__main__":
    import os
    main()


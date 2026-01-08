from pathlib import Path
from typing import Optional
import os
import re


from codomyrmex.logging_monitoring import get_logger






























#!/usr/bin/env python3
"""Fix common documentation issues intelligently."""


"""Main entry point and utility functions

This module provides fix_common_doc_issues functionality including:
- 7 functions: calculate_correct_path, fix_broken_root_links, fix_parent_links...
- 0 classes: 

Usage:
    # Example usage here
"""
logger = get_logger(__name__)
def calculate_correct_path(from_file: Path, to_file: Path) -> str:
    """Calculate correct relative path."""
    try:
        rel_path = os.path.relpath(to_file, from_file.parent)
        return rel_path.replace('\\', '/')
    except ValueError:
        return str(to_file)

def fix_broken_root_links(content: str, file_path: Path) -> str:
    """Fix broken links to repository root."""
    base_path = Path("/Users/mini/Documents/GitHub/codomyrmex")
    
    # Calculate correct path to root
    rel_to_root = file_path.parent.relative_to(base_path)
    depth = len(rel_to_root.parts)
    correct_root = "../" * depth + "README.md" if depth > 0 else "README.md"
    correct_spec = "../" * depth + "SPEC.md" if depth > 0 else "SPEC.md"
    
    # Fix common broken patterns
    patterns = [
        (r'\[README\]\(\.\.\/\.\.\/\.\.\/README\.md\)', f'[README]({correct_root})'),
        (r'\[README\]\(\.\.\/\.\.\/README\.md\)', f'[README]({correct_root})'),
        (r'\[README\]\(\.\.\/README\.md\)', f'[README]({correct_root})'),
        (r'\[Repository Root\]\(\.\.\/\.\.\/\.\.\/README\.md\)', f'[Repository Root]({correct_root})'),
        (r'\[Repository Root\]\(\.\.\/\.\.\/README\.md\)', f'[Repository Root]({correct_root})'),
        (r'\[Repository Root\]\(\.\.\/README\.md\)', f'[Repository Root]({correct_root})'),
        (r'\[Repository SPEC\]\(\.\.\/\.\.\/\.\.\/SPEC\.md\)', f'[Repository SPEC]({correct_spec})'),
        (r'\[Repository SPEC\]\(\.\.\/\.\.\/SPEC\.md\)', f'[Repository SPEC]({correct_spec})'),
        (r'\[Repository SPEC\]\(\.\.\/SPEC\.md\)', f'[Repository SPEC]({correct_spec})'),
    ]
    
    for pattern, replacement in patterns:
        content = re.sub(pattern, replacement, content)
    
    return content

def fix_parent_links(content: str, file_path: Path) -> str:
    """Fix broken parent directory links."""
    base_path = Path("/Users/mini/Documents/GitHub/codomyrmex")
    parent_dir = file_path.parent.parent
    
    if parent_dir == base_path:
        return content
    
    parent_name = file_path.parent.name
    correct_parent = "../README.md"
    
    # Fix parent directory links
    patterns = [
        (rf'\[{re.escape(parent_name)}\]\(\.\.\/\.\.\/\.\.\/{re.escape(parent_name)}\/README\.md\)', f'[{parent_name}]({correct_parent})'),
        (rf'\[{re.escape(parent_name)}\]\(\.\.\/\.\.\/{re.escape(parent_name)}\/README\.md\)', f'[{parent_name}]({correct_parent})'),
    ]
    
    for pattern, replacement in patterns:
        content = re.sub(pattern, replacement, content)
    
    return content

def enhance_spec_content(content: str, dir_path: Path, dir_name: str) -> str:
    """Enhance SPEC.md with actual content based on directory."""
    # Check if has placeholder content
    if "[Architecture description if applicable]" not in content:
        return content  # Already has content
    
    # Get purpose from AGENTS.md or README.md
    purpose = ""
    agents = dir_path / "AGENTS.md"
    readme = dir_path / "README.md"
    
    if agents.exists():
        try:
            agents_content = agents.read_text(encoding='utf-8')
            if "## Purpose" in agents_content:
                start = agents_content.find("## Purpose")
                end = agents_content.find("##", start + 10)
                if end == -1:
                    end = min(len(agents_content), start + 300)
                purpose = agents_content[start+10:end].strip()
        except Exception:
            pass
    
    if not purpose and readme.exists():
        try:
            readme_content = readme.read_text(encoding='utf-8')
            if "## Overview" in readme_content:
                start = readme_content.find("## Overview")
                end = readme_content.find("##", start + 11)
                if end == -1:
                    end = min(len(readme_content), start + 300)
                purpose = readme_content[start+11:end].strip()
        except Exception:
            pass
    
    # Replace placeholder purpose
    if purpose and "## Purpose\n\n## Overview" in content:
        content = content.replace("## Purpose\n\n## Overview", f"## Purpose\n\n{purpose}\n\n## Overview")
    elif purpose and "## Purpose\n\n\n## Overview" in content:
        content = content.replace("## Purpose\n\n\n## Overview", f"## Purpose\n\n{purpose}\n\n## Overview")
    
    # Replace placeholder sections with generic but useful content
    replacements = {
        "[Architecture description if applicable]": "Architecture description with component relationships and data flow patterns.",
        "[Functional requirements for " + dir_name + "]": f"Functional requirements for {dir_name} including core capabilities and standards.",
        "[Testing, documentation, performance, security requirements]": "Testing requirements, documentation standards, performance expectations, and security considerations.",
        "[APIs, data structures, communication patterns]": "API interfaces, data structure definitions, and communication patterns.",
        "[How to implement within this directory]": f"Implementation guidelines for working within {dir_name} including best practices and patterns."
    }
    
    for placeholder, replacement in replacements.items():
        content = content.replace(placeholder, replacement)
    
    return content

def add_navigation_links(content: str, file_path: Path, file_type: str) -> str:
    """Add comprehensive navigation links."""
    base_path = Path("/Users/mini/Documents/GitHub/codomyrmex")
    rel_path = file_path.parent.relative_to(base_path)
    depth = len(rel_path.parts)
    
    root_path = "../" * depth + "README.md" if depth > 0 else "README.md"
    spec_path = "../" * depth + "SPEC.md" if depth > 0 else "SPEC.md"
    parent_path = "../README.md" if depth > 0 else "README.md"
    
    # Check if navigation section exists
    if "## Navigation" not in content:
        # Add navigation section before end
        nav_section = f"""
## Navigation

- **Human Documentation**: [README.md](README.md)
- **Technical Documentation**: [AGENTS.md](AGENTS.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
"""
        if depth > 0:
            parent_name = file_path.parent.parent.name if file_path.parent.parent != base_path else "Root"
            nav_section += f"- **Parent Directory**: [{parent_name}]({parent_path})\n"
        
        nav_section += f"- **Repository Root**: [{root_path}]({root_path})\n"
        if depth > 0:
            nav_section += f"- **Repository SPEC**: [{spec_path}]({spec_path})\n"
        
        content = content.rstrip() + "\n" + nav_section
    else:
        # Enhance existing navigation
        if file_type == "README.md":
            if "**Technical Documentation**: [AGENTS.md]" not in content:
                content = re.sub(
                    r'(## Navigation\n)',
                    r'\1- **Technical Documentation**: [AGENTS.md](AGENTS.md)\n- **Functional Specification**: [SPEC.md](SPEC.md)\n',
                    content
                )
        elif file_type == "AGENTS.md":
            if "**Human Documentation**: [README.md]" not in content:
                content = re.sub(
                    r'(## Navigation[^\n]*\n)',
                    r'\1- **Human Documentation**: [README.md](README.md)\n- **Functional Specification**: [SPEC.md](SPEC.md)\n',
                    content
                )
    
    return content

def process_file(file_path: Path) -> bool:
    """Process a single documentation file."""
    if not file_path.exists():
        return False
    
    try:
        content = file_path.read_text(encoding='utf-8')
        original = content
        
        # Fix broken links
        content = fix_broken_root_links(content, file_path)
        content = fix_parent_links(content, file_path)
        
        # Enhance SPEC.md content
        if file_path.name == "SPEC.md":
            dir_name = file_path.parent.name
            content = enhance_spec_content(content, file_path.parent, dir_name)
        
        # Add navigation links
        content = add_navigation_links(content, file_path, file_path.name)
        
        if content != original:
            file_path.write_text(content, encoding='utf-8')
            return True
        return False
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False

def main():
    """Fix common documentation issues."""
    base_path = Path("/Users/mini/Documents/GitHub/codomyrmex")
    fixed_count = 0
    
    for root, dirs, files in os.walk(base_path):
        dirs[:] = [d for d in dirs if not d.startswith('.') and 
                   d not in ['__pycache__', 'node_modules', 'venv', '.venv', '.git']]
        
        for file in ['README.md', 'AGENTS.md', 'SPEC.md']:
            file_path = Path(root) / file
            if file_path.exists() and file_path.parent != base_path:
                if process_file(file_path):
                    fixed_count += 1
                    if fixed_count % 20 == 0:
                        print(f"Fixed {fixed_count} files...")
    
    print(f"\nCompleted: Fixed {fixed_count} documentation files")

if __name__ == "__main__":
    main()


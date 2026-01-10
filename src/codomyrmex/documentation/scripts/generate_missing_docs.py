from pathlib import Path
from typing import Optional
import os

from codomyrmex.logging_monitoring import get_logger




















"""
def get_directory_info(dir_path: Path) -> dict:
    """



    #!/usr/bin/env python3
    """Generate missing README.md and AGENTS.md files."""

logger = get_logger(__name__)

Get directory information from existing files."""
    info = {
        'purpose': '',
        'description': '',
        'children': []
    }
    
    # Try to get info from existing README or AGENTS
    for file in [dir_path / 'README.md', dir_path / 'AGENTS.md', dir_path / 'SPEC.md']:
        if file.exists():
            try:
                content = file.read_text(encoding='utf-8')
                if '## Purpose' in content:
                    start = content.find('## Purpose')
                    end = content.find('##', start + 10)
                    if end == -1:
                        end = len(content)
                    info['purpose'] = content[start+10:end].strip()[:300]
                    break
            except Exception:
                pass
    
    # List child directories
    try:
        for item in dir_path.iterdir():
            if item.is_dir() and not item.name.startswith('.') and item.name not in ['__pycache__']:
                info['children'].append(item.name)
    except Exception:
        pass
    
    return info

def create_readme(dir_path: Path, dir_name: str, info: dict) -> str:
    """Create README.md content."""
    depth = len(dir_path.relative_to(Path('/Users/mini/Documents/GitHub/codomyrmex')).parts) - 1
    parent_path = "../" * depth
    
    content = f"""# {dir_name}

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: December 2025

## Overview

{info['purpose'] if info['purpose'] else f'Directory: {dir_name}'}

## Directory Contents
"""
    
    if info['children']:
        for child in sorted(info['children'])[:10]:
            content += f"- `{child}/` – Subdirectory\n"
        if len(info['children']) > 10:
            content += f"- ... ({len(info['children']) - 10} more)\n"
    
    content += f"""
## Navigation
- **Technical Documentation**: [AGENTS.md](AGENTS.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
- **Repository Root**: [{parent_path}README.md]({parent_path}README.md)
"""
    
    return content

def create_agents(dir_path: Path, dir_name: str, info: dict) -> str:
    """Create AGENTS.md content."""
    depth = len(dir_path.relative_to(Path('/Users/mini/Documents/GitHub/codomyrmex')).parts) - 1
    parent_path = "../" * depth
    
    content = f"""# Codomyrmex Agents — {dir_name}

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: December 2025

## Purpose

{info['purpose'] if info['purpose'] else f'Directory: {dir_name}'}

## Active Components
"""
    
    if info['children']:
        for child in sorted(info['children'])[:10]:
            content += f"- `{child}/` – Subdirectory\n"
    
    content += f"""
## Operating Contracts

[Operating contracts for {dir_name}]

## Navigation
- **Human Documentation**: [README.md](README.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
- **Repository Root**: [{parent_path}README.md]({parent_path}README.md)
"""
    
    return content

def main():
    """Generate missing documentation files."""
    base_path = Path("/Users/mini/Documents/GitHub/codomyrmex")
    readme_count = 0
    agents_count = 0
    
    for root, dirs, files in os.walk(base_path):
        dirs[:] = [d for d in dirs if not d.startswith('.') and 
                   d not in ['__pycache__', 'node_modules', 'venv', '.venv', '.git']]
        
        current_dir = Path(root)
        if current_dir == base_path:
            continue
        
        dir_name = current_dir.name
        info = get_directory_info(current_dir)
        
        # Create README.md if missing
        readme_file = current_dir / 'README.md'
        if not readme_file.exists():
            try:
                readme_content = create_readme(current_dir, dir_name, info)
                readme_file.write_text(readme_content, encoding='utf-8')
                readme_count += 1
            except Exception as e:
                print(f"Error creating README.md for {current_dir}: {e}")
        
        # Create AGENTS.md if missing
        agents_file = current_dir / 'AGENTS.md'
        if not agents_file.exists():
            try:
                agents_content = create_agents(current_dir, dir_name, info)
                agents_file.write_text(agents_content, encoding='utf-8')
                agents_count += 1
            except Exception as e:
                print(f"Error creating AGENTS.md for {current_dir}: {e}")
    
    print(f"\nCompleted: {readme_count} README.md files created, {agents_count} AGENTS.md files created")

if __name__ == "__main__":
    main()

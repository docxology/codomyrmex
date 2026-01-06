#!/usr/bin/env python3
"""Generate SPEC.md files for all directories missing them."""

import os
from pathlib import Path
from typing import Optional

def get_directory_purpose(dir_path: Path) -> str:
    """Try to infer directory purpose from README.md or AGENTS.md."""
    readme = dir_path / "README.md"
    agents = dir_path / "AGENTS.md"
    
    purpose = ""
    if readme.exists():
        try:
            content = readme.read_text(encoding='utf-8')
            # Try to extract purpose from README
            if "## Purpose" in content:
                start = content.find("## Purpose")
                end = content.find("##", start + 10)
                if end == -1:
                    end = len(content)
                purpose = content[start:end].strip()
            elif "## Overview" in content:
                start = content.find("## Overview")
                end = content.find("##", start + 11)
                if end == -1:
                    end = min(len(content), start + 500)
                purpose = content[start:end].strip()
        except Exception:
            pass
    
    if not purpose and agents.exists():
        try:
            content = agents.read_text(encoding='utf-8')
            if "## Purpose" in content:
                start = content.find("## Purpose")
                end = content.find("##", start + 10)
                if end == -1:
                    end = len(content)
                purpose = content[start:end].strip()
        except Exception:
            pass
    
    return purpose[:200] if purpose else f"Directory: {dir_path.name}"

def create_spec_content(dir_path: Path, dir_name: str, purpose: str) -> str:
    """Create SPEC.md content for a directory."""
    # Calculate relative paths from this directory to repository root
    base_path = Path("/Users/mini/Documents/GitHub/codomyrmex")
    try:
        rel_path = dir_path.relative_to(base_path)
        depth = len(rel_path.parts) - 1  # Subtract 1 because we're in the directory
        root_path = "../" * depth if depth > 0 else "./"
    except ValueError:
        # If path is not relative to base, use simple calculation
        depth = len(dir_path.parts) - len(base_path.parts) - 1
        root_path = "../" * depth if depth > 0 else "./"
    
    spec_content = f"""# {dir_name} - Functional Specification

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: December 2025

## Purpose

{purpose}

## Design Principles

### Modularity
- Self-contained components
- Clear boundaries
- Minimal dependencies

### Internal Coherence
- Logical organization
- Consistent patterns
- Unified design

### Parsimony
- Essential elements only
- No unnecessary complexity
- Minimal surface area

### Functionality
- Focus on working solutions
- Forward-looking design
- Current needs focus

### Testing
- Comprehensive coverage
- TDD practices
- Real data analysis

### Documentation
- Self-documenting code
- Clear APIs
- Complete specifications

## Architecture

[Architecture description if applicable]

## Functional Requirements

[Functional requirements for {dir_name}]

## Quality Standards

[Testing, documentation, performance, security requirements]

## Interface Contracts

[APIs, data structures, communication patterns]

## Implementation Guidelines

[How to implement within this directory]

## Navigation

- **Human Documentation**: [README.md](README.md)
- **Technical Documentation**: [AGENTS.md](AGENTS.md)
"""
    
    # Add parent navigation if not at root
    if depth > 0:
        parent_name = dir_path.parent.name if dir_path.parent != base_path else 'Root'
        spec_content += f"- **Parent Directory**: [{parent_name}](../README.md)\n"
    
    spec_content += f"- **Repository Root**: [{root_path}README.md]({root_path}README.md)\n"
    if depth > 0:  # Only add SPEC link if not at root
        spec_content += f"- **Repository SPEC**: [{root_path}SPEC.md]({root_path}SPEC.md)\n"
    
    return spec_content

def main():
    """Generate SPEC.md files for all directories missing them."""
    base_path = Path("/Users/mini/Documents/GitHub/codomyrmex")
    dirs_processed = 0
    dirs_skipped = 0
    
    for root, dirs, files in os.walk(base_path):
        # Skip hidden and system directories
        dirs[:] = [d for d in dirs if not d.startswith('.') and 
                   d not in ['__pycache__', 'node_modules', 'venv', '.venv', '.git']]
        
        current_dir = Path(root)
        if current_dir == base_path:
            continue
        
        spec_file = current_dir / 'SPEC.md'
        if spec_file.exists():
            dirs_skipped += 1
            continue
        
        # Get directory purpose
        purpose = get_directory_purpose(current_dir)
        dir_name = current_dir.name
        
        # Create SPEC.md content
        spec_content = create_spec_content(current_dir, dir_name, purpose)
        
        # Write SPEC.md file
        try:
            spec_file.write_text(spec_content, encoding='utf-8')
            dirs_processed += 1
            if dirs_processed % 10 == 0:
                print(f"Processed {dirs_processed} directories...")
        except Exception as e:
            print(f"Error creating SPEC.md for {current_dir}: {e}")
    
    print(f"\nCompleted: {dirs_processed} SPEC.md files created, {dirs_skipped} already existed")

if __name__ == "__main__":
    main()


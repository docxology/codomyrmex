import os
from pathlib import Path
from datetime import datetime

AGENTS_TEMPLATE = """# {module_name} Agents — Local Coordination

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: {date}

## Purpose

Coordination and navigation hub for agents interacting with `{module_name}`.

## Operating Contracts

- **Respect Modularity**: Changes must not break external boundaries.
- **Maintain Documentation Alignment**: Keep all documentation synced with code logic.
- **Traceability**: Leave structured tracks for upstream orchestration agents.
"""

README_TEMPLATE = """# {module_name}

Internal module for the Codomyrmex ecosystem.

## Overview

This directory provides functionality and resources for `{module_name}`. Follow the project's standard modular practices when adding or modifying code within this namespace.
"""

SPEC_TEMPLATE = """# {module_name} Specification

## 1. Description

Functional and technical requirements for the `{module_name}` module.

## 2. Core Capabilities

- Adherence to Zero-Mock implementation standards.
- Modular self-containment for reliable orchestrator interaction.
"""

def extract_module_name(path_str):
    name = os.path.basename(path_str)
    if name == 'src' or name == 'codomyrmex' or name == 'projects':
        return path_str.split('/')[-1]
    return name.replace('_', ' ').title()

def rectify_docs(start_path):
    start_dir = Path(start_path)
    if not start_dir.exists():
        return

    today = datetime.now().strftime("%B %Y")
    
    for root, dirs, files in os.walk(start_dir):
        # Prevent recursion into ignored folders
        dirs[:] = [d for d in dirs if d not in ('.git', '__pycache__', '.pytest_cache', '.venv', '.github', 'node_modules', '.mypy_cache', 'docs', 'documentation')]
        
        # Don't touch the docs_gen generated outputs
        if '/documentation/' in root:
            continue
            
        current_dir = Path(root)
        
        has_py = any(f.endswith('.py') for f in files)
        has_agents = 'AGENTS.md' in files
        has_readme = 'README.md' in files
        has_spec = 'SPEC.md' in files
        
        # We process directories possessing existing markdown files (even if stub) or code, to ensure enforcement
        if not (has_py or has_agents or has_readme or has_spec):
            # Also if it's an interior directory in `agents` we should probably document it
            if '/agents/' in root or '/daf-consulting/' in root:
                pass
            else:
                continue

        module_name = extract_module_name(root)
        
        paths = [
            (current_dir / 'AGENTS.md', AGENTS_TEMPLATE, has_agents),
            (current_dir / 'README.md', README_TEMPLATE, has_readme),
            (current_dir / 'SPEC.md', SPEC_TEMPLATE, has_spec)
        ]
        
        for file_path, template, exists in paths:
            if not exists:
                print(f"Creating missing {file_path.name} in {current_dir.relative_to(start_dir.parent)}")
                # Fill in template values
                content = template.format(module_name=module_name, date=today)
                file_path.write_text(content, encoding='utf-8')
            else:
                # Check for stub
                content = file_path.read_text(encoding='utf-8')
                if len(content.strip()) < 50:
                    print(f"Replacing stub {file_path.name} in {current_dir.relative_to(start_dir.parent)}")
                    content = template.format(module_name=module_name, date=today)
                    file_path.write_text(content, encoding='utf-8')

if __name__ == "__main__":
    repo_root = "/Users/mini/Documents/GitHub/codomyrmex"
    print("Running Doc Rectification...")
    rectify_docs(f"{repo_root}/src/codomyrmex")
    rectify_docs(f"{repo_root}/projects")
    print("Done")

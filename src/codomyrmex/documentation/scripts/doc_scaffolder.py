import os
import sys

from codomyrmex.logging_monitoring import get_logger

























"""
# """Main entry point and utility functions


"""
EXCLUDE_DIRS = {
    '__pycache__', '.git', '.github', '.idea', '.vscode', 'venv', 'env', 'node_modules', 
    '__init__.py', '.DS_Store', 'dist', 'build', 'egg-info', '.mypy_cache', '.pytest_cache',
    '@output'
}

EXCLUDE_FILES = {
    '__init__.py', '.DS_Store'
}

TEMPLATE_README =
"""
"""

"""



"""Main entry point and utility functions

logger = get_logger(__name__)

# {name}

## Signposting
- **Parent**: [Parent](../README.md)
- **Children**:
{children_links}
- **Key Artifacts**:
    - [Agent Guide](AGENTS.md)
    - [Functional Spec](SPEC.md)

## Overview
[DESCRIBE THE PURPOSE AND SCOPE OF THE {name} DIRECTORY]
"""

TEMPLATE_AGENTS = """# {name} Agents

## Signposting
- **Parent**: [Parent](../AGENTS.md)
- **Self**: [Agents](AGENTS.md)
- **Children**:
{children_links}
- **Key Artifacts**:
    - [Functional Spec](SPEC.md)
    - [Human Readme](README.md)

## Purpose
[DESCRIBE THE COORDINATION ROLE OF THIS DIRECTORY FOR AI AGENTS]
"""

TEMPLATE_SPEC = """# {name} Functional Specification

## Core Concept
[DESCRIBE THE CORE ARCHITECTURAL OR FUNCTIONAL CONCEPT OF {name}]

## Functional Requirements
- [REQUIREMENT 1: Describe a specific capability]
- [REQUIREMENT 2: Describe another specific capability]

## Modularity & Interfaces
- Inputs: [DESCRIBE INPUTS]
- Outputs: [DESCRIBE OUTPUTS]
- Dependencies: [LIST DEPENDENCIES]

## Coherence
[DESCRIBE HOW THIS COMPONENT FITS INTO THE LARGER CODOMYRMEX SYSTEM]
"""

def get_children_links(root, dirs, filename="README.md"):
    links = []
    for d in sorted(dirs):
        if d in EXCLUDE_DIRS or d.startswith('.'):
            continue
        links.append(f"    - [{d}]({d}/{filename})")
    
    if not links:
        links.append("    - None")
    
    return "\n".join(links)

def update_file_with_signposting(path, name, children_links, file_type="README.md"):
    with open(path, "r") as f:
        content = f.read()
    
    if "## Signposting" in content:
        return

    print(f"Updating {path} with Signposting")
    
    if file_type == "README.md":
        signposting = f"""
## Signposting
- **Parent**: [Parent](../README.md)
- **Children**:
{children_links}
- **Key Artifacts**:
    - [Agent Guide](AGENTS.md)
    - [Functional Spec](SPEC.md)
"""
    else: # AGENTS.md
        signposting = f"""
## Signposting
- **Parent**: [Parent](../AGENTS.md)
- **Self**: [Agents](AGENTS.md)
- **Children**:
{children_links}
- **Key Artifacts**:
    - [Functional Spec](SPEC.md)
    - [Human Readme](README.md)
"""

    lines = content.splitlines()
    # Find first header
    insert_idx = 0
    for i, line in enumerate(lines):
        if line.startswith("# "):
            insert_idx = i + 1
            break
    
    new_lines = lines[:insert_idx] + signposting.splitlines() + lines[insert_idx:]
    with open(path, "w") as f:
        f.write("\n".join(new_lines))

def process_directory(root, dirs):
    name = os.path.basename(root)
    if not name:
        name = "Root"

    # README
    readme_path = os.path.join(root, "README.md")
    children_readme = get_children_links(root, dirs, "README.md")
    if not os.path.exists(readme_path):
        print(f"Creating README.md in {root}")
        content = TEMPLATE_README.format(name=name, children_links=children_readme)
        with open(readme_path, "w") as f:
            f.write(content)
    else:
        update_file_with_signposting(readme_path, name, children_readme, "README.md")
    
    # AGENTS
    agents_path = os.path.join(root, "AGENTS.md")
    children_agents = get_children_links(root, dirs, "AGENTS.md")
    if not os.path.exists(agents_path):
        print(f"Creating AGENTS.md in {root}")
        content = TEMPLATE_AGENTS.format(name=name, children_links=children_agents)
        with open(agents_path, "w") as f:
            f.write(content)
    else:
        update_file_with_signposting(agents_path, name, children_agents, "AGENTS.md")

    # SPEC
    spec_path = os.path.join(root, "SPEC.md")
    if not os.path.exists(spec_path):
        print(f"Creating SPEC.md in {root}")
        content = TEMPLATE_SPEC.format(name=name)
        with open(spec_path, "w") as f:
            f.write(content)


def main():
    start_dir = sys.argv[1] if len(sys.argv) > 1 else "."
    start_dir = os.path.abspath(start_dir)

    for root, dirs, files in os.walk(start_dir):
        # Modify dirs in-place to exclude unwanted directories
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS and not d.startswith('.')]
        
        process_directory(root, dirs)

if __name__ == "__main__":
    main()

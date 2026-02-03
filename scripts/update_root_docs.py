#!/usr/bin/env python3
"""
scripts/update_root_docs.py

Synchronizes `src/codomyrmex` root files (__init__.py, README.md, AGENTS.md)
with the actual subdirectories present.
"""

import os
from pathlib import Path
from typing import List

ROOT_DIR = Path(__file__).parent.parent
SRC_DIR = ROOT_DIR / "src" / "codomyrmex"

# Modules to always ignore
IGNORE = ["__pycache__", ".DS_Store"]

def get_submodules() -> List[str]:
    modules = []
    for item in SRC_DIR.iterdir():
        if item.is_dir() and item.name not in IGNORE and not item.name.startswith("."):
            if (item / "__init__.py").exists():
                modules.append(item.name)
    return sorted(modules)

def update_init_py(modules: List[str]):
    init_path = SRC_DIR / "__init__.py"
    content = init_path.read_text()
    
    # Generate new _submodules list
    submodules_list = "    " + ',\n    '.join([f'"{m}"' for m in modules]) + ",\n"
    
    # Generate new __all__ list
    all_list = "    " + ',\n    '.join([f'"{m}"' for m in modules]) + ",\n"
    
    # We will do a somewhat heuristic replacement, assuming standard formatting
    # Find start and end of _submodules list
    start_marker = "_submodules = ["
    end_marker = "]"
    
    try:
        start_idx = content.find(start_marker) + len(start_marker)
        end_idx = content.find(end_marker, start_idx)
        
        if start_idx == -1 or end_idx == -1:
            print("Could not find _submodules list in __init__.py")
            return

        new_content = content[:start_idx] + "\n" + submodules_list + content[end_idx:]
        
        # Now find __all__
        start_marker_all = "__all__ = ["
        start_idx_all = new_content.find(start_marker_all) + len(start_marker_all)
        end_idx_all = new_content.find(end_marker, start_idx_all)
        
        if start_idx_all == -1 or end_idx_all == -1:
             print("Could not find __all__ list in __init__.py")
             return

        # Keep the extra exports at the end of __all__ if they exist
        # Identifying where module list ends and static exports begin is tricky.
        # Let's just assume we want to replace the module part.
        # Check if there are static exports at the end of the existing list?
        # The existing file has: "get_version", "get_module_path", "list_modules"
        
        static_exports = [
            '    "get_version",',
            '    "get_module_path",',
            '    "list_modules",'
        ]
        
        final_all_content = all_list + '\n'.join(static_exports) + "\n"
        
        final_content = new_content[:start_idx_all] + "\n" + final_all_content + new_content[end_idx_all:]
        
        init_path.write_text(final_content)
        print("Updated __init__.py")
        
    except Exception as e:
        print(f"Error updating __init__.py: {e}")

def update_readme_md(modules: List[str]):
    readme_path = SRC_DIR / "README.md"
    content = readme_path.read_text()
    
    header = "## Directory Contents\n\n"
    start_idx = content.find(header)
    if start_idx == -1:
        print("Could not find Directory Contents in README.md")
        return
    
    start_idx += len(header)
    
    # Find end of list (next section usually starts with ##)
    end_idx = content.find("## ", start_idx)
    if end_idx == -1:
        end_idx = len(content)
        
    # Generate new list
    new_list = ""
    # Add static files first
    new_list += "- `PAI.md` – Personal AI Infrastructure documentation\n"
    new_list += "- `README.md` – This file\n"
    new_list += "- `SPEC.md` – Module specification\n"
    new_list += "- `__init__.py` – Package initialization\n"
    
    for m in modules:
        # Try to get short desc from module __init__ docstring? 
        # For now just use name
        new_list += f"- `{m}/` – Module\n"
        
    final_content = content[:start_idx] + new_list + "\n" + content[end_idx:]
    readme_path.write_text(final_content)
    print("Updated README.md")

def update_agents_md(modules: List[str]):
    agents_path = SRC_DIR / "AGENTS.md"
    content = agents_path.read_text()
    
    header = "## Active Components\n\n"
    start_idx = content.find(header)
    if start_idx == -1:
        print("Could not find Active Components in AGENTS.md")
        return
        
    start_idx += len(header)
    end_idx = content.find("## ", start_idx)
    if end_idx == -1:
        end_idx = len(content)
        
    new_list = ""
    new_list += "- `PAI.md` – Project file\n"
    new_list += "- `README.md` – Project file\n"
    new_list += "- `SPEC.md` – Project file\n"
    new_list += "- `__init__.py` – Project file\n"
    
    for m in modules:
        new_list += f"- `{m}/` – Module component\n"
        
    final_content = content[:start_idx] + new_list + "\n" + content[end_idx:]
    agents_path.write_text(final_content)
    print("Updated AGENTS.md")

def main():
    modules = get_submodules()
    print(f"Found {len(modules)} submodules.")
    
    update_init_py(modules)
    update_readme_md(modules)
    update_agents_md(modules)

if __name__ == "__main__":
    main()


import sys
from pathlib import Path
try:
    import codomyrmex
except ImportError:
    # Add project root to sys.path
    project_root = Path(__file__).resolve().parent.parent.parent
    src_path = project_root / "src"
    sys.path.insert(0, str(src_path))
import os
from pathlib import Path

repo_root = Path("/Users/mini/Documents/GitHub/codomyrmex")
scripts_dir = repo_root / "scripts"

def get_dirs(path):
    return sorted([d for d in os.listdir(path) if os.path.isdir(os.path.join(path, d)) and not d.startswith('_') and d != '__pycache__'])

current_dirs = get_dirs(scripts_dir)

# Update scripts/AGENTS.md
agents_file = scripts_dir / "AGENTS.md"
if agents_file.exists():
    with open(agents_file, 'r') as f:
        lines = f.readlines()
    
    new_lines = []
    children_section = False
    active_components = False
    
    for line in lines:
        if "## Signposting" in line:
            new_lines.append(line)
            continue
        if "- **Children**:" in line:
            new_lines.append(line)
            children_section = True
            for d in current_dirs:
                new_lines.append(f"    - [{d}]({d}/AGENTS.md)\n")
            continue
        if children_section and line.startswith("    - "):
            continue
        if children_section and not line.strip():
            children_section = False
        
        if "## Active Components" in line:
            new_lines.append(line)
            active_components = True
            # Add files in root
            root_files = sorted([f for f in os.listdir(scripts_dir) if os.path.isfile(os.path.join(scripts_dir, f)) and not f.startswith('.')])
            for f in root_files:
                new_lines.append(f"- `{f}` – Project file\n")
            for d in current_dirs:
                new_lines.append(f"- `{d}/` – Directory containing {d} components\n")
            continue
        if active_components and (line.startswith("- `") or line.startswith("- [")):
            continue
        if active_components and not line.strip():
            active_components = False
            
        if not children_section and not active_components:
            new_lines.append(line)
            
    with open(agents_file, 'w') as f:
        f.writelines(new_lines)
    print("Updated scripts/AGENTS.md")

# Update scripts/README.md
readme_file = scripts_dir / "README.md"
if readme_file.exists():
    with open(readme_file, 'r') as f:
        content = f.read()
    
    # Simple replacement of common old paths
    replacements = {
        "scripts/ai_code_editing": "scripts/coding",
        "scripts/maintenance": "scripts/tools",
        "scripts/testing": "scripts/tests",
        "scripts/examples": "scripts/documentation/examples",
        "testing/": "scripts/tests/"
    }
    for old, new in replacements.items():
        content = content.replace(old, new)
    
    with open(readme_file, 'w') as f:
        f.write(content)
    print("Updated scripts/README.md")

print("Docs cleanup complete.")
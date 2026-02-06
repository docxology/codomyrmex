import os
from pathlib import Path

from codomyrmex.logging_monitoring import get_logger

"""
Fix AGENTS.md Structure

This script iterates through all AGENTS.md files and ensures they have the required sections:
- Purpose
- Active Components
- Operating Contracts

If sections are missing, it adds them with intelligent default content.


"""


logger = get_logger(__name__)

def get_default_contracts():
    return """
## Operating Contracts
- Maintain alignment between code, documentation, and configured workflows.
- Ensure Model Context Protocol interfaces remain available for sibling agents.
- Record outcomes in shared telemetry and update task queues when necessary.
"""

def get_active_components(dir_path):
    """Generate active components list based on directory contents."""
    components = []
    try:
        for item in os.listdir(dir_path):
            if item.startswith('.') or item == '__pycache__' or item == 'AGENTS.md':
                continue

            item_path = dir_path / item
            if item_path.is_dir():
                 components.append(f"- `{item}/` - Agent surface for {item} components.")
            elif item_path.is_file():
                 components.append(f"- `{item}` - Component file.")
    except Exception:
        pass

    if not components:
        return "\n## Active Components\n- No specific components listed. See README.md for details.\n"

    return "\n## Active Components\n" + "\n".join(sorted(components)) + "\n"

def fix_agents_file(file_path):
    try:
        content = file_path.read_text(encoding='utf-8')
        modified = False

        # Check for Operating Contracts
        if '## Operating Contracts' not in content and '# Operating Contracts' not in content:
            print(f"Adding Operating Contracts to {file_path}")
            content += get_default_contracts()
            modified = True

        # Check for Active Components
        if '## Active Components' not in content and '# Active Components' not in content:
            print(f"Adding Active Components to {file_path}")
            # Insert before Operating Contracts if it exists (which it might now)
            # But simpler to just append if it was missing, or insert before if we can find a good spot.
            # If we just appended Operating Contracts, we can append Components before it? No, structure usually implies components then contracts.

            # Let's try to place it before Operating Contracts if it exists
            if '## Operating Contracts' in content:
                parts = content.split('## Operating Contracts')
                content = parts[0] + get_active_components(file_path.parent) + "\n## Operating Contracts" + parts[1]
            else:
                content += get_active_components(file_path.parent)

            modified = True

        if modified:
            file_path.write_text(content, encoding='utf-8')
            return True

    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False
    return False

def main():
    root = Path(__file__).parent.parent.parent
    print(f"Scanning {root} for AGENTS.md files...")

    agents_files = []
    for path in root.rglob('AGENTS.md'):
        if any(part.startswith('.') for part in path.parts):
            continue
        if 'node_modules' in path.parts or '__pycache__' in path.parts:
            continue
        agents_files.append(path)

    count = 0
    for file_path in agents_files:
        if fix_agents_file(file_path):
            count += 1

    print(f"Fixed {count} AGENTS.md files.")

if __name__ == "__main__":
    main()

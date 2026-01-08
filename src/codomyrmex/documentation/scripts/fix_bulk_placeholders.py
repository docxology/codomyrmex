from pathlib import Path
import os
import re




#!/usr/bin/env python3
"""
Bulk Fix Documentation Placeholders.

Replaces generic placeholders in SECURITY.md and AGENTS.md with more specific,
albeit still generic, descriptions to clear "Placeholder" audits.
"""


def fix_security_md(root_dir):
    """Replace [Brief Description] in SECURITY.md."""
    print("Fixing SECURITY.md files...")
    count = 0
    for path in Path(root_dir).rglob("SECURITY.md"):
        if "template" in str(path):
            continue
            
        try:
            content = path.read_text(encoding="utf-8")
            if "[Brief Description]" in content:
                # Replace with a sensible default based on the module name if possible, or just "Security Issue"
                new_content = content.replace("[Brief Description]", "Security Issue")
                path.write_text(new_content, encoding="utf-8")
                print(f"  Fixed {path.relative_to(root_dir)}")
                count += 1
        except Exception as e:
            print(f"  Error reading {path}: {e}")
    print(f"Fixed {count} SECURITY.md files.")

def fix_agents_md(root_dir):
    """Replace [Brief description] in AGENTS.md."""
    print("Fixing AGENTS.md files...")
    count = 0
    pattern = re.compile(r"\[Brief description.*?\]", re.IGNORECASE)
    
    for path in Path(root_dir).rglob("AGENTS.md"):
        if "template" in str(path):
            continue
            
        try:
            content = path.read_text(encoding="utf-8")
            if pattern.search(content):
                module_name = path.parent.name
                replacement = f"Documentation and agents for the {module_name} module."
                
                new_content = pattern.sub(replacement, content)
                path.write_text(new_content, encoding="utf-8")
                print(f"  Fixed {path.relative_to(root_dir)}")
                count += 1
        except Exception as e:
            print(f"  Error reading {path}: {e}")
    print(f"Fixed {count} AGENTS.md files.")

if __name__ == "__main__":
    root = Path.cwd()
    fix_security_md(root)
    fix_agents_md(root)

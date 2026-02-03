#!/usr/bin/env python3
"""
scripts/update_spec_md.py

Updates SPEC.md to include any modules missing from the module lists.
Adds them to the 'Specialized Layer' section by default.
"""

from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent
SRC_DIR = ROOT_DIR / "src" / "codomyrmex"
SPEC_PATH = SRC_DIR / "SPEC.md"

# List of all modules (same logic as before)
def get_all_modules():
    modules = []
    for item in SRC_DIR.iterdir():
        if item.is_dir() and not item.name.startswith(".") and item.name != "__pycache__":
            if (item / "__init__.py").exists():
                modules.append(item.name)
    return set(modules)

def main():
    content = SPEC_PATH.read_text()
    all_modules = get_all_modules()
    
    # We look for the "Specialized Layer" definition in the mermaid chart or the text list
    # Let's target the text list: "#### Specialized Layer" ... "**Modules**:"
    
    start_marker = "#### Specialized Layer"
    modules_marker = "**Modules**:"
    
    start_idx = content.find(start_marker)
    if start_idx == -1:
        print("Could not find Specialized Layer section")
        return
        
    modules_idx = content.find(modules_marker, start_idx)
    if modules_idx == -1:
        print("Could not find Modules list in Specialized Layer section")
        return
        
    modules_idx += len(modules_marker)
    
    # Find the end of the list (next section usually starts with **Characteristics**)
    end_idx = content.find("**Characteristics**", modules_idx)
    
    if end_idx == -1:
        end_idx = len(content)
        
    current_list_block = content[modules_idx:end_idx]
    
    # Identify which modules are already mentioned in the WHOLE file to avoid dupes anywhere
    # (e.g. if they are in Core Layer)
    existing_modules = set()
    for m in all_modules:
        if f"`{m}`" in content or f"`{m}<" in content or f"[{m}]" in content:
            existing_modules.add(m)
            
    missing = all_modules - existing_modules
    
    if missing:
        print(f"Adding {len(missing)} missing modules to Specialized Layer: {missing}")
        
        new_entries = ""
        for m in sorted(missing):
            # Try to get a simple description from restore_descriptions.py map if possible, 
            # or just default.
            new_entries += f"\n- `{m}`: Specialized module"
            
        # Append to the end of the current list block
        # The current list ends with a newline usually
        new_list_block = current_list_block.rstrip() + new_entries + "\n\n"
        
        final_content = content[:modules_idx] + new_list_block + content[end_idx:]
        SPEC_PATH.write_text(final_content)
        print("Updated SPEC.md")
    else:
        print("No missing modules found in SPEC.md")

if __name__ == "__main__":
    main()

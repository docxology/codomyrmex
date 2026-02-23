import os
import shutil
import re

SRC_DIR = "src/codomyrmex"
DOCS_DIR = "docs/modules"

def get_actual_modules():
    mods = []
    for d in os.listdir(SRC_DIR):
        if d.startswith("__"): continue
        p = os.path.join(SRC_DIR, d)
        if os.path.isdir(p) and os.path.isfile(os.path.join(p, "__init__.py")):
            mods.append(d)
    return sorted(mods)

def sync_subdirectories():
    actual_mods = get_actual_modules()
    
    # Remove stale dirs in docs/modules
    if os.path.exists(DOCS_DIR):
        for d in os.listdir(DOCS_DIR):
            p = os.path.join(DOCS_DIR, d)
            if os.path.isdir(p) and d not in actual_mods:
                print(f"Removing obsolete directory: {p}")
                shutil.rmtree(p)
                
    # Copy all RASP/API/etc files from src to docs/modules
    for m in actual_mods:
        src_module = os.path.join(SRC_DIR, m)
        dest_module = os.path.join(DOCS_DIR, m)
        os.makedirs(dest_module, exist_ok=True)
        
        # Copy any markdown / relevant files
        for f in os.listdir(src_module):
            if f.endswith(".md"):
                shutil.copy2(os.path.join(src_module, f), os.path.join(dest_module, f))
                
def fix_file(filepath, count):
    if not os.path.exists(filepath): return
    with open(filepath, 'r') as f:
        content = f.read()
        
    original = content
        
    # Standardize the numbers
    content = re.sub(r'(\d+) modules?', f'{count} modules', content)
    content = re.sub(r'(\d+)/(\d+) complete', f'{count}/{count} complete', content)
    content = re.sub(r'(\d+) module subdirectories', f'{count} module subdirectories', content)
    
    # Fix the generic "XX specialized modules"
    content = re.sub(r'containing \d+ specialized modules', f'containing {count} specialized modules', content)
    
    if content != original:
        with open(filepath, 'w') as f:
            f.write(content)
            print(f"Updated numbers in {filepath}")

def main():
    actual_mods = get_actual_modules()
    count = len(actual_mods)
    
    sync_subdirectories()
    
    root_docs = ["AGENTS.md", "dependency-graph.md", "ollama.md", "overview.md", "PAI.md", "README.md", "relationships.md", "SPEC.md"]
    for f in root_docs:
        fix_file(os.path.join(DOCS_DIR, f), count)
        
if __name__ == "__main__":
    main()

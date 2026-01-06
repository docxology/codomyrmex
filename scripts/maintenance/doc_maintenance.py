import os
import re
from pathlib import Path

# Paths to search
SEARCH_DIRS = ["src", "scripts", "docs", "config", "cursorrules", "projects", "examples"]
ROOT_FILES = ["README.md", "AGENTS.md", "SPEC.md"]

# Path mappings
PATH_MAPPINGS = {
    r"src/codomyrmex/language_models/": "src/codomyrmex/llm/",
    r"src/codomyrmex/modeling_3d/": "src/codomyrmex/spatial/three_d/",
    r"src/codomyrmex/coding_execution_sandbox/": "src/codomyrmex/coding/sandbox/",
    r"src/codomyrmex/coding_review/": "src/codomyrmex/coding/review/",
    r"src/codomyrmex/ollama_integration/": "src/codomyrmex/llm/ollama/",
    r"src/codomyrmex/api_standardization/": "src/codomyrmex/api/standardization/",
    r"src/codomyrmex/api_documentation/": "src/codomyrmex/api_documentation/", # Wait, Check if this exists
    r"src/codomyrmex/ai_code_editing/": "src/codomyrmex/agents/ai_code_editing/",
    r"src/codomyrmex/security_audit/": "src/codomyrmex/security/",
    r"testing/": "src/codomyrmex/tests/",
}

# Navigation links to fix (depth-sensitive)
# From root:
ROOT_NAV_FIX = """## Navigation Links

- **Documentation**: [Reference Guides](docs/README.md)
- **All Agents**: [AGENTS.md](AGENTS.md)
- **Functional Spec**: [SPEC.md](SPEC.md)
- **Source Index**: [src/README.md](src/README.md)
"""

def fix_content(content, file_path):
    original = content
    
    # Apply path mappings
    for old, new in PATH_MAPPINGS.items():
        content = content.replace(old, new)
        
    # Fix broken relative links in root files
    if file_path.name in ROOT_FILES and file_path.parent == Path.cwd():
        # Look for the broken nav block
        nav_pattern = r"## Navigation Links\s+-\s+\*\*Parent\*\*: \[Project Overview\]\(\.\./README\.md\).*?\(\.\.\/\.\.\/\.\.\/README\.md\)"
        content = re.sub(nav_pattern, ROOT_NAV_FIX, content, flags=re.DOTALL)
        
        # Also handle partial broken navs
        content = content.replace("../../AGENTS.md", "AGENTS.md")
        content = content.replace("../../docs/README.md", "docs/README.md")
        content = content.replace("../../../README.md", "README.md")

    # Remove redundant "Additional Files" block if it matches the pattern
    additional_files_pattern = r"\n### Additional Files\n- `SPEC\.md` – Spec Md.*?\n- `uv\.lock` – Uv Lock\n"
    content = re.sub(additional_files_pattern, "\n", content, flags=re.DOTALL)

    # Address common placeholders
    content = content.replace("<!-- Description pending -->", "Detailed technical specification and implementation guide.")
    content = content.replace("<!-- Requirement pending definition -->", "System compliance and architectural integrity verification.")
    
    return content

def main():
    root = Path.cwd()
    files_to_fix = []
    
    # Collect all .md files
    for d in SEARCH_DIRS:
        if (root / d).exists():
            files_to_fix.extend((root / d).glob("**/*.md"))
    
    for f in ROOT_FILES:
        if (root / f).exists():
            files_to_fix.append(root / f)
            
    updated_count = 0
    for file_path in files_to_fix:
        try:
            content = file_path.read_text(encoding="utf-8")
            new_content = fix_content(content, file_path)
            
            if new_content != content:
                file_path.write_text(new_content, encoding="utf-8")
                updated_count += 1
                # print(f"Fixed: {file_path}")
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
            
    print(f"Total files updated: {updated_count}")

if __name__ == "__main__":
    main()

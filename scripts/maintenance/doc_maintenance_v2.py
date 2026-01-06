import os
import re
from pathlib import Path

# Paths to search
SEARCH_DIRS = ["src", "scripts", "docs", "config", "cursorrules", "projects", "examples", "output"]
ROOT_FILES = ["README.md", "AGENTS.md", "SPEC.md"]

# Module consolidation mappings
MODULE_MAPPINGS = {
    "language_models": "llm",
    "modeling_3d": "spatial/three_d",
    "code_execution_sandbox": "code/sandbox",
    "code_review": "code/review",
    "ollama_integration": "llm/ollama",
    "api_standardization": "api/standardization",
    "api_documentation": "api/documentation",
    "ai_code_editing": "agents/ai_code_editing",
    "security_audit": "security",
}

def fix_content(content, file_path, repo_root):
    # depth = len(file_path.relative_to(repo_root).parts) - 1
    
    def replace_link(match):
        text = match.group(1)
        link = match.group(2)
        
        # Skip absolute links or anchors
        if link.startswith(("http", "#", "mailto:")):
            return match.group(0)
            
        # 1. Fix module names in links
        for old, new in MODULE_MAPPINGS.items():
            if old in link:
                link = link.replace(old, new)
        
        # 2. Fix 'testing/' -> 'src/codomyrmex/tests/'
        if link.startswith("testing/") or "/testing/" in link:
            link = link.replace("testing/", "src/codomyrmex/tests/")
            
        # 3. Handle common depth errors for 'docs/', 'scripts/', 'examples/'
        # If a link starts with ../docs/ but doesn't exist, try adding more ../
        current_dir = file_path.parent
        
        # Normalize link (remove query params/anchors for check)
        clean_link = link.split("#")[0].split("?")[0]
        if not (current_dir / clean_link).exists():
            # Try to find the file from repo root
            # Strip leading ../
            stripped_link = clean_link
            while stripped_link.startswith("../"):
                stripped_link = stripped_link[3:]
            
            # Common root-level dirs
            for root_dir in ["docs", "scripts", "examples", "config", "src", "projects"]:
                if stripped_link.startswith(root_dir + "/"):
                    # Calculate correct relative path from current_dir to repo_root/stripped_link
                    try:
                        rel_to_root = Path(stripped_link)
                        abs_target = repo_root / rel_to_root
                        if abs_target.exists():
                            # Generate relative path
                            new_rel = os.path.relpath(abs_target, current_dir)
                            return f"[{text}]({new_rel})"
                    except:
                        pass
        
        return f"[{text}]({link})"

    # Apply link replacement
    content = re.sub(r"\[(.*?)\]\((.*?)\)", replace_link, content)
    
    # 4. Clean up redundant sections
    additional_files_pattern = r"\n### Additional Files\n- `SPEC\.md` – Spec Md.*?\n- `uv\.lock` – Uv Lock\n"
    content = re.sub(additional_files_pattern, "\n", content, flags=re.DOTALL)

    # 5. Fix common placeholders
    content = content.replace("<!-- Description pending -->", "Detailed technical specification and implementation guide.")
    content = content.replace("<!-- Requirement pending definition -->", "System compliance and architectural integrity verification.")
    
    return content

def main():
    repo_root = Path.cwd()
    files_to_fix = []
    
    # Collect all .md files
    for d in SEARCH_DIRS:
        if (repo_root / d).exists():
            files_to_fix.extend((repo_root / d).glob("**/*.md"))
    
    for f in ROOT_FILES:
        if (repo_root / f).exists():
            files_to_fix.append(repo_root / f)
            
    updated_count = 0
    for file_path in files_to_fix:
        try:
            content = file_path.read_text(encoding="utf-8")
            new_content = fix_content(content, file_path, repo_root)
            
            if new_content != content:
                file_path.write_text(new_content, encoding="utf-8")
                updated_count += 1
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
            
    print(f"Total files updated: {updated_count}")

if __name__ == "__main__":
    main()

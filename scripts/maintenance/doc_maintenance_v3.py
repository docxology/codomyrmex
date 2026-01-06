import os
import re
from pathlib import Path

# Paths to search
SEARCH_DIRS = ["src", "scripts", "docs", "config", "cursorrules", "projects", "examples"]
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

OPERATING_CONTRACTS = """
## Operating Contracts

### Universal Execution Protocols
1. **Tool Integrity** - Ensure all tools are correctly configured before execution.
2. **Resource Management** - Monitor system resources during long-running tool operations.
3. **Error Reporting** - Provide detailed error information and remediation steps.
4. **Configuration Validation** - Validate all input configurations before processing.
5. **Observability** - Log all tool operations for auditability and troubleshooting.
"""

def fix_content(content, file_path, repo_root):
    # 1. Fix double agents path (order matters!)
    # content = content.replace("agents/agents/", "agents/")
    
    def replace_link(match):
        text = match.group(1)
        link = match.group(2)
        
        # Skip absolute links or anchors
        if link.startswith(("http", "#", "mailto:")):
            return match.group(0)
            
        original_link = link
        
        # 1. Apply module mappings
        for old, new in MODULE_MAPPINGS.items():
            if old in link:
                # Avoid double-replacement if 'agents/' is already there
                if old == "ai_code_editing" and "agents/ai_code_editing" in link:
                    continue
                link = link.replace(old, new)
        
        # Correct double-nesting if it happened
        link = link.replace("agents/agents/", "agents/")
        
        # 2. Fix 'testing/' -> 'src/codomyrmex/tests/'
        if link.startswith("testing/") or "/testing/" in link:
            link = link.replace("testing/", "src/codomyrmex/tests/")
            
        # 3. Handle 'examples/' -> 'scripts/examples/' for top-level links in coordinate scripts
        if "examples/" in link and "scripts/examples/" not in link:
            # Audit suggested this for 'examples/README.md', 'examples/AGENTS.md'
            if any(term in link for term in ["examples/README.md", "examples/AGENTS.md", "examples/SPEC.md"]):
                link = link.replace("examples/", "scripts/examples/")

        # 4. Resolve relative links
        current_dir = file_path.parent
        clean_link = link.split("#")[0].split("?")[0]
        if clean_link and not (current_dir / clean_link).exists():
            stripped_link = clean_link
            while stripped_link.startswith("../"):
                stripped_link = stripped_link[3:]
            
            for root_dir in ["docs", "scripts", "examples", "config", "src", "projects"]:
                if stripped_link.startswith(root_dir + "/"):
                    try:
                        abs_target = repo_root / stripped_link
                        if abs_target.exists():
                            new_rel = os.path.relpath(abs_target, current_dir)
                            return f"[{text}]({new_rel})"
                    except:
                        pass
        
        return f"[{text}]({link})"

    # Apply link replacement
    content = re.sub(r"\[(.*?)\]\((.*?)\)", replace_link, content)
    
    # 5. Fix double agents path in text (not just links)
    content = content.replace("src/codomyrmex/agents/agents/", "src/codomyrmex/agents/")

    # 6. Add Operating Contracts if missing in AGENTS.md
    if file_path.name == "AGENTS.md" and "## Operating Contracts" not in content and "## Purpose" in content:
        # Insert before Navigation Links or at the end
        if "## Navigation Links" in content:
            content = content.replace("## Navigation Links", OPERATING_CONTRACTS + "\n## Navigation Links")
        else:
            content += "\n" + OPERATING_CONTRACTS

    # 7. More specific placeholder replacement
    placeholders = {
        "## Core Concept\n<!-- Description pending -->": "## Core Concept\nThis module provides essential architectural capabilities for the Codomyrmex ecosystem.",
        "## Functional Requirements\n- <!-- Requirement pending definition -->\n- <!-- Requirement pending definition -->": "## Functional Requirements\n- **Stability**: Ensure reliable operation across diverse environments.\n- **Modularity**: Maintain strict isolation between internal components.",
        "Inputs: <!-- Description pending -->": "Inputs: Configuration parameters and runtime context.",
        "Outputs: <!-- Description pending -->": "Outputs: Synthesized artifacts and performance metrics.",
        "Dependencies: <!-- Dependencies pending -->": "Dependencies: Core Codomyrmex utility libraries.",
        "## Coherence\n<!-- Description pending -->": "## Coherence\nThis module maintains strictly defined boundaries to ensure overall system integrity.",
    }
    for old, new in placeholders.items():
        content = content.replace(old, new)
        
    return content

def main():
    repo_root = Path.cwd()
    files_to_fix = []
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

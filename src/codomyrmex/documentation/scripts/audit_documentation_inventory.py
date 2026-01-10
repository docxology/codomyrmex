from pathlib import Path
from typing import Dict, List, Tuple
import json
import os
import re

from codomyrmex.logging_monitoring import get_logger





Audit all README.md and AGENTS.md files in the repository.
Creates a comprehensive inventory with current state assessment.
"""


logger = get_logger(__name__)

REPO_ROOT = Path(__file__).parent.parent.parent

def check_file_content(filepath: Path) -> Dict:
    """Check a documentation file for completeness indicators."""
    if not filepath.exists():
        return {"exists": False}
    
    content = filepath.read_text(encoding='utf-8', errors='ignore')
    
    checks = {
        "exists": True,
        "size": len(content),
        "has_version": bool(re.search(r'Version.*v?\d+\.\d+', content, re.IGNORECASE)),
        "has_status": bool(re.search(r'Status.*(Active|Inactive|Deprecated)', content, re.IGNORECASE)),
        "has_signposting": bool(re.search(r'Signposting|Parent|Children', content, re.IGNORECASE)),
        "has_mermaid": bool(re.search(r'```mermaid', content)),
        "mermaid_count": len(re.findall(r'```mermaid', content)),
        "has_function_signatures": bool(re.search(r'def\s+\w+\(|class\s+\w+\(', content)),
        "has_placeholder": bool(re.search(r'placeholder|template|TODO|FIXME|XXX', content, re.IGNORECASE)),
        "has_navigation": bool(re.search(r'Navigation|Related|Links', content, re.IGNORECASE)),
    }
    
    # For AGENTS.md, check for function signatures more specifically
    if filepath.name == "AGENTS.md":
        checks["has_class_definitions"] = bool(re.search(r'class\s+\w+.*:', content))
        checks["has_method_signatures"] = bool(re.search(r'def\s+\w+\([^)]*\)\s*->', content))
    
    return checks

def find_doc_files(root: Path) -> List[Tuple[Path, str]]:
    """Find all README.md and AGENTS.md files."""
    files = []
    for path in root.rglob("README.md"):
        if ".venv" not in str(path) and "node_modules" not in str(path):
            files.append((path, "README.md"))
    for path in root.rglob("AGENTS.md"):
        if ".venv" not in str(path) and "node_modules" not in str(path):
            files.append((path, "AGENTS.md"))
    return sorted(files)

def audit_all_files() -> Dict:
    """Audit all documentation files."""
    files = find_doc_files(REPO_ROOT)
    inventory = {
        "total_files": len(files),
        "readme_count": sum(1 for _, name in files if name == "README.md"),
        "agents_count": sum(1 for _, name in files if name == "AGENTS.md"),
        "files": {}
    }
    
    for filepath, filename in files:
        rel_path = filepath.relative_to(REPO_ROOT)
        checks = check_file_content(filepath)
        inventory["files"][str(rel_path)] = {
            "type": filename,
            "path": str(rel_path),
            **checks
        }
    
    return inventory

def generate_summary(inventory: Dict) -> str:
    """Generate a summary report."""
    summary = []
    summary.append(f"Total Documentation Files: {inventory['total_files']}")
    summary.append(f"README.md files: {inventory['readme_count']}")
    summary.append(f"AGENTS.md files: {inventory['agents_count']}")
    summary.append("")
    
    # Count files by completeness
    readme_files = [f for f in inventory['files'].values() if f['type'] == 'README.md']
    agents_files = [f for f in inventory['files'].values() if f['type'] == 'AGENTS.md']
    
    summary.append("README.md Statistics:")
    summary.append(f"  With Mermaid diagrams: {sum(1 for f in readme_files if f.get('has_mermaid', False))}")
    summary.append(f"  With signposting: {sum(1 for f in readme_files if f.get('has_signposting', False))}")
    summary.append(f"  With placeholders: {sum(1 for f in readme_files if f.get('has_placeholder', False))}")
    summary.append("")
    
    summary.append("AGENTS.md Statistics:")
    summary.append(f"  With function signatures: {sum(1 for f in agents_files if f.get('has_function_signatures', False))}")
    summary.append(f"  With class definitions: {sum(1 for f in agents_files if f.get('has_class_definitions', False))}")
    summary.append(f"  With signposting: {sum(1 for f in agents_files if f.get('has_signposting', False))}")
    summary.append(f"  With placeholders: {sum(1 for f in agents_files if f.get('has_placeholder', False))}")
    
    return "\n".join(summary)

if __name__ == "__main__":
    print("Auditing documentation files...")
    inventory = audit_all_files()
    
    # Save inventory
    output_file = REPO_ROOT / "output" / "documentation_inventory.json"
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, 'w') as f:
        json.dump(inventory, f, indent=2)
    
    # Print summary
    print(generate_summary(inventory))
    print(f"\nFull inventory saved to: {output_file}")

from pathlib import Path
from typing import List, Tuple
import os






REQUIRED_FILES = ["README.md", "AGENTS.md", "SPEC.md"]
IGNORE_DIRS = [
    ".git", ".github", ".venv", "__pycache__", ".pytest_cache", 
    ".codomyrmex", "node_modules", ".gemini"
]

def is_relevant_dir(path: Path) -> bool:
    if any(part in IGNORE_DIRS or part.startswith('.') for part in path.parts):
        return False
    # If it's a leaf node containing code or if it previously had docs
    # Or if it is a top level directory
    return True

def audit_directory(root_path: Path) -> Tuple[int, int, List[str]]:
    total_dirs = 0
    compliant_dirs = 0
    issues = []

    for root, dirs, files in os.walk(root_path):
        # Modify dirs in-place to skip ignored
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS and not d.startswith('.')]
        
        current_path = Path(root)
        
        # Heuristic: We only really care about directories that are "significant".
        # For now, let's check ALL directories that are not hidden, 
        # but maybe skip deeply nested ones if they are just code packages without implementation?
        # Actually spec says "every folder level".
        
        missing = []
        for req in REQUIRED_FILES:
            if req not in files:
                missing.append(req)
        
        if missing:
            # Check if this directory is empty or trivial
            if not any(f.endswith('.py') or f.endswith('.sh') or f.endswith('.md') for f in files):
                continue # Skip mostly empty directories
            
            issues.append(f"{current_path}: Missing {', '.join(missing)}")
        else:
            compliant_dirs += 1
            
        total_dirs += 1

    return total_dirs, compliant_dirs, issues

if __name__ == "__main__":
    root = Path(".")
    # Audit specific top level folders we care about
    targets = ["src", "scripts", "testing", "docs", "config", "projects", "cursorrules", "examples"]
    
    all_issues = []
    grand_total = 0
    grand_compliant = 0
    
    print("Starting Global Documentation Audit...\n")
    
    for target in targets:
        if not (root / target).exists():
            print(f"Warning: Target '{target}' not found.")
            continue
            
        t, c, issues = audit_directory(root / target)
        grand_total += t
        grand_compliant += c
        all_issues.extend(issues)
        
    print(f"\nAudit Complete.")
    print(f"Total Directories Checked: {grand_total}")
    print(f"Compliant Directories: {grand_compliant}")
    print(f"Compliance Rate: {grand_compliant/grand_total*100:.1f}%")
    
    if all_issues:
        print("\nIssues Found:")
        for i in sorted(all_issues)[:20]: # Show first 20
            print(f"  - {i}")
        if len(all_issues) > 20:
            print(f"  ... and {len(all_issues)-20} more.")
    else:
        print("\nNo issues found! 100% Compliant.")

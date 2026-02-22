import os
import ast

def check_package(dirpath):
    issues = []
    
    # Check for documentation files
    docs_needed = ['README.md', 'SPEC.md', 'AGENTS.md']
    for doc in docs_needed:
        if not os.path.exists(os.path.join(dirpath, doc)):
            issues.append(f"Missing {doc}")
            
    # Check __init__.py for __all__
    init_path = os.path.join(dirpath, "__init__.py")
    with open(init_path, "r") as f:
        try:
            tree = ast.parse(f.read())
            has_all = any(
                isinstance(node, ast.Assign) and 
                any(isinstance(target, ast.Name) and target.id == '__all__' for target in node.targets)
                for node in tree.body
            )
            # If __init__.py is NOT empty, we should ideally have an __all__ or at least verify it's active
            # For this strict audit, we just warn if it's missing __all__ but has code
            if not has_all and len(tree.body) > 0:
                issues.append("Missing __all__ definition in __init__.py (might be inactive or lack explicit exports)")
        except SyntaxError:
            issues.append(f"SyntaxError in {init_path}")

    return issues

def scan_repo(root_dir):
    print("Starting repo-wide audit...")
    total_packages = 0
    issues_found = 0
    
    for dirpath, dirnames, filenames in os.walk(root_dir):
        # We only care about Python packages
        if "__init__.py" in filenames:
            total_packages += 1
            issues = check_package(dirpath)
            if issues:
                issues_found += len(issues)
                print(f"[{dirpath}]")
                for issue in issues:
                    print(f"  - {issue}")
                    
    print(f"\nAudit complete. Scanned {total_packages} packages. Found {issues_found} issues.")

if __name__ == "__main__":
    scan_repo("src/codomyrmex")

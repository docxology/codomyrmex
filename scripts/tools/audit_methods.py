
import sys
from pathlib import Path
try:
    import codomyrmex
except ImportError:
    # Add project root to sys.path
    project_root = Path(__file__).resolve().parent.parent.parent
    src_path = project_root / "src"
    sys.path.insert(0, str(src_path))
import ast
import os
import sys

def is_functional(node):
    """Check if a function/method body is functional (not just pass/docstring/raise NotImplemented)."""
    if not node.body:
        return False
    
    effective_body = []
    for stmt in node.body:
        # Ignore docstrings (Expr -> Constant string)
        if isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Constant) and isinstance(stmt.value.value, str):
            continue
        # Ignore pass
        if isinstance(stmt, ast.Pass):
            continue
        # Ignore raise NotImplementedError
        if isinstance(stmt, ast.Raise):
             # Simplified check for raise NotImplementedError
             if isinstance(stmt.exc, ast.Call) and isinstance(stmt.exc.func, ast.Name) and stmt.exc.func.id == "NotImplementedError":
                 continue
             if isinstance(stmt.exc, ast.Name) and stmt.exc.id == "NotImplementedError":
                 continue
        
        effective_body.append(stmt)
        
    return len(effective_body) > 0

def has_docstring(node):
    return ast.get_docstring(node) is not None

def audit_file(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        try:
            tree = ast.parse(f.read(), filename=filepath)
        except SyntaxError:
            return {"syntax_error": True}

    issues = []
    
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            name = node.name
            # Skip private/magic methods if desired, but user said "all methods"
            # keeping it strict for now.
            
            doc = has_docstring(node)
            func = is_functional(node)
            
            missing = []
            if not doc:
                missing.append("missing_docstring")
            if not func:
                missing.append("placeholder_body")
                
            if missing:
                issues.append({
                    "name": name,
                    "lineno": node.lineno,
                    "issues": missing
                })
                
    return issues

def main():
    root_dir = "src/codomyrmex"
    report = {}
    
    for root, dirs, files in os.walk(root_dir):
        # Exclude tests/examples from strict "real functional" audit if desired? 
        # User said "repo test suite" and "confirm all methods", usually means source code.
        if "tests" in root.split(os.sep): 
            continue
            
        for file in files:
            if file.endswith(".py") and not file.startswith("__"):
                path = os.path.join(root, file)
                file_issues = audit_file(path)
                if file_issues:
                   report[path] = file_issues

    # Print Report
    total_issues = 0
    for path, issues in report.items():
        if isinstance(issues, dict) and issues.get("syntax_error"):
            print(f"SYNTAX ERROR: {path}")
            continue
            
        print(f"\nFile: {path}")
        for tissue in issues:
            total_issues += 1
            print(f"  Line {tissue['lineno']} - {tissue['name']}: {', '.join(tissue['issues'])}")
            
    print(f"\nTotal Issues Found: {total_issues}")
    if total_issues > 0:
        sys.exit(1)

if __name__ == "__main__":
    main()
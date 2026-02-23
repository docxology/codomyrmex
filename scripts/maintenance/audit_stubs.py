import os
import ast

SRC_DIR = "src/codomyrmex"

def is_stub_node(node):
    if not node.body: return True
    body = node.body
    if len(body) > 1 and isinstance(body[0], ast.Expr) and isinstance(body[0].value, ast.Constant) and isinstance(body[0].value.value, str):
        body = body[1:]
    if not body: return True
    if len(body) == 1:
        stmt = body[0]
        if isinstance(stmt, ast.Pass): return True
        if isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Constant) and stmt.value.value is Ellipsis: return True
        if isinstance(stmt, ast.Raise):
            if isinstance(stmt.exc, ast.Name) and stmt.exc.id == "NotImplementedError": return True
            if isinstance(stmt.exc, ast.Call) and getattr(stmt.exc.func, "id", "") == "NotImplementedError": return True
    return False

def audit_stubs_better():
    issues = []
    
    for root, dirs, files in os.walk(SRC_DIR):
        if "__pycache__" in root or "/tests" in root: continue
            
        for f in files:
            filepath = os.path.join(root, f)
            # Skip obvious protocol/interface files
            if "interface" in f.lower() or "protocol" in f.lower() or "base.py" == f or "abc.py" == f or "__init__.py" == f:
                continue
                
            if f.endswith(".py") and not f.startswith("test_"):
                with open(filepath, "r") as fp:
                    try:
                        content = fp.read()
                        tree = ast.parse(content)
                        
                        # Add parent pointers to identify class methods
                        for node in ast.walk(tree):
                            for child in ast.iter_child_nodes(node):
                                child.parent = node
                                
                        for node in ast.walk(tree):
                            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                                if is_stub_node(node):
                                    parent = getattr(node, "parent", None)
                                    is_abstract = False
                                    
                                    # check decorators
                                    for d in node.decorator_list:
                                        name = getattr(d, "id", "") or getattr(d, "attr", "")
                                        if name in ("abstractmethod", "overload", "property"):
                                            is_abstract = True
                                            break
                                        
                                    if isinstance(parent, ast.ClassDef):
                                        for base in parent.bases:
                                            name = getattr(base, "id", "") or getattr(base, "attr", "")
                                            if name in ("ABC", "Protocol", "Interface", "Exception", "Error", "BaseException"):
                                                is_abstract = True
                                                break
                                                
                                    if not is_abstract:
                                        # Skip some noisy false positives:
                                        if isinstance(parent, ast.ClassDef) and (parent.name.endswith("Error") or parent.name.endswith("Exception") or parent.name.endswith("Base")):
                                            continue
                                        # Just generic stuff
                                        if node.name in ("__init__", "__post_init__", "__enter__", "__exit__", "close", "shutdown", "cleanup", "update", "setup"):
                                            continue
                                            
                                        # Let us see the rest
                                        issues.append(f"- `{node.name}` in [{filepath}](../../{filepath}#L{node.lineno})")
                    except Exception as e:
                        pass
    return issues

issues = audit_stubs_better()
with open("/Users/mini/.gemini/antigravity/brain/85a85c7d-a8cc-4b5a-bf5c-94143d7aea03/stub_audit.md", "w") as f:
    f.write(f"# Stub Audit Findings\n\nFound {len(issues)} concrete stub methods requiring implementation:\n\n")
    for issue in issues:
        f.write(issue + "\n")
print(f"Written {len(issues)} stubs to artifact")

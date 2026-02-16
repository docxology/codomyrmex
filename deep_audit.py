import os
import ast
import re
from pathlib import Path

def extract_python_members(file_path):
    """Extract public classes and methods from a Python file."""
    members = {"classes": {}, "functions": []}
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            tree = ast.parse(f.read())
        
        for node in ast.iter_child_nodes(tree):
            if isinstance(node, ast.ClassDef):
                if not node.name.startswith("_"):
                    methods = []
                    for subnode in node.body:
                        if isinstance(subnode, ast.FunctionDef):
                            if not subnode.name.startswith("_"):
                                methods.append(subnode.name)
                    members["classes"][node.name] = methods
            elif isinstance(node, ast.FunctionDef):
                if not node.name.startswith("_"):
                    members["functions"].append(node.name)
    except Exception as e:
        # print(f"Error parsing {file_path}: {e}")
        pass
    return members

def extract_md_mentions(file_path):
    """Extract class and method mentions from a Markdown file."""
    if not os.path.exists(file_path):
        return set()
    
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Heuristic: look for things like **ClassName**, `method_name`, etc.
    # Also look for headings that might be class names
    tokens = set(re.findall(r"[*`]{1,2}([a-zA-Z0-9_]{3,})[*`]{1,2}", content))
    headings = set(re.findall(r"^#+ (?:.* )?([a-zA-Z0-9_]{3,})", content, re.M))
    
    return tokens.union(headings)

def run_audit(root_dir):
    src_dir = os.path.join(root_dir, "src", "codomyrmex")
    docs_dir = os.path.join(root_dir, "docs", "modules")
    
    report = []
    
    # Get all host modules (directories in src/codomyrmex)
    modules = [d for d in os.listdir(src_dir) if os.path.isdir(os.path.join(src_dir, d)) and d != "__pycache__"]
    
    for module in sorted(modules):
        mod_path = os.path.join(src_dir, module)
        
        # 1. Implementation members
        impl_members = {"classes": {}, "functions": []}
        for root, _, files in os.walk(mod_path):
            for file in files:
                if file.endswith(".py"):
                    file_members = extract_python_members(os.path.join(root, file))
                    impl_members["functions"].extend(file_members["functions"])
                    for cls, methods in file_members["classes"].items():
                        if cls not in impl_members["classes"]:
                            impl_members["classes"][cls] = []
                        impl_members["classes"][cls].extend(methods)

        # 2. Documentation mentions
        doc_files = [
            os.path.join(mod_path, "SPEC.md"),
            os.path.join(mod_path, "AGENTS.md"),
            os.path.join(docs_dir, module, "SPEC.md"),
            os.path.join(docs_dir, module, "AGENTS.md"),
            os.path.join(docs_dir, module, "README.md"),
        ]
        
        mentions = set()
        for doc_file in doc_files:
            mentions.update(extract_md_mentions(doc_file))
            
        # 3. Compare
        missing_docs = []
        for cls, methods in impl_members["classes"].items():
            if cls not in mentions:
                missing_docs.append(f"Class: {cls}")
            for method in methods:
                if method not in mentions:
                    missing_docs.append(f"Method: {cls}.{method}")
        
        for func in impl_members["functions"]:
            if func not in mentions:
                missing_docs.append(f"Function: {func}")
                
        if missing_docs:
            report.append(f"### Module: {module}")
            report.append(f"- Missing in docs: {len(missing_docs)} items")
            # Limit report size
            for item in missing_docs[:5]:
                report.append(f"  - {item}")
            if len(missing_docs) > 5:
                 report.append(f"  - ... and {len(missing_docs)-5} more")
            report.append("")

    with open("deep_audit_report.md", "w") as f:
        f.write("# Deep Audit Discrepancy Report\n\n")
        f.write("\n".join(report))
        
    print(f"Audit complete. Report written to deep_audit_report.md. Found issues in {len(report)//4} modules.")

if __name__ == "__main__":
    run_audit(os.getcwd())

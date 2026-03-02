#!/usr/bin/env python3
"""
Generate and manage project documentation.

Usage:
    python doc_generator.py [--type TYPE] [--output OUTPUT]
"""

import sys
from pathlib import Path

try:
    import codomyrmex  # noqa: F401
except ImportError:
    project_root = Path(__file__).resolve().parent.parent.parent
    sys.path.insert(0, str(project_root / "src"))

import argparse
import ast


def extract_module_info(file_path: Path) -> dict:
    """Extract info from a Python module."""
    with open(file_path) as f:
        source = f.read()
    
    info = {
        "name": file_path.stem,
        "docstring": None,
        "functions": [],
        "classes": [],
    }
    
    try:
        tree = ast.parse(source)
        info["docstring"] = ast.get_docstring(tree)
        
        for node in ast.iter_child_nodes(tree):
            if isinstance(node, ast.FunctionDef):
                info["functions"].append({
                    "name": node.name,
                    "docstring": ast.get_docstring(node),
                    "args": [a.arg for a in node.args.args],
                })
            elif isinstance(node, ast.ClassDef):
                methods = []
                for item in node.body:
                    if isinstance(item, ast.FunctionDef):
                        methods.append(item.name)
                info["classes"].append({
                    "name": node.name,
                    "docstring": ast.get_docstring(node),
                    "methods": methods,
                })
    except:
        pass
    
    return info


def generate_markdown(info: dict) -> str:
    """Generate markdown documentation."""
    lines = [f"# {info['name']}\n"]
    
    if info["docstring"]:
        lines.append(f"{info['docstring']}\n")
    
    if info["classes"]:
        lines.append("## Classes\n")
        for cls in info["classes"]:
            lines.append(f"### `{cls['name']}`\n")
            if cls["docstring"]:
                lines.append(f"{cls['docstring']}\n")
            if cls["methods"]:
                lines.append("**Methods:**\n")
                for m in cls["methods"]:
                    lines.append(f"- `{m}()`\n")
            lines.append("")
    
    if info["functions"]:
        lines.append("## Functions\n")
        for func in info["functions"]:
            args = ", ".join(func["args"])
            lines.append(f"### `{func['name']}({args})`\n")
            if func["docstring"]:
                lines.append(f"{func['docstring']}\n")
            lines.append("")
    
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Generate documentation")
    parser.add_argument("path", nargs="?", help="Python file or directory")
    parser.add_argument("--output", "-o", default=None, help="Output file")
    parser.add_argument("--format", "-f", choices=["markdown", "json"], default="markdown")
    parser.add_argument("--list", "-l", action="store_true", help="List undocumented items")
    args = parser.parse_args()
    
    if not args.path:
        print("📚 Documentation Generator\n")
        print("Usage:")
        print("  python doc_generator.py module.py")
        print("  python doc_generator.py src/ --output docs/")
        print("  python doc_generator.py module.py --list")
        return 0
    
    target = Path(args.path)
    if not target.exists():
        print(f"❌ Path not found: {args.path}")
        return 1
    
    files = [target] if target.is_file() else list(target.rglob("*.py"))
    files = [f for f in files if "__pycache__" not in str(f) and not f.name.startswith("_")]
    
    print(f"📚 Generating docs for {len(files)} file(s)\n")
    
    undocumented = []
    
    for f in files[:20]:
        info = extract_module_info(f)
        
        if args.list:
            if not info["docstring"]:
                undocumented.append(f"Module: {f.name}")
            for func in info["functions"]:
                if not func["docstring"] and not func["name"].startswith("_"):
                    undocumented.append(f"  Function: {f.name}:{func['name']}")
            for cls in info["classes"]:
                if not cls["docstring"]:
                    undocumented.append(f"  Class: {f.name}:{cls['name']}")
            continue
        
        doc = generate_markdown(info)
        
        if args.output:
            out_dir = Path(args.output)
            out_dir.mkdir(parents=True, exist_ok=True)
            out_file = out_dir / f"{f.stem}.md"
            out_file.write_text(doc)
            print(f"   ✅ {f.name} → {out_file}")
        else:
            print(f"📄 {f.name}:")
            print(f"   Functions: {len(info['functions'])}")
            print(f"   Classes: {len(info['classes'])}")
    
    if args.list:
        if undocumented:
            print(f"⚠️  Undocumented items ({len(undocumented)}):\n")
            for item in undocumented[:30]:
                print(f"   {item}")
        else:
            print("✅ All items documented")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

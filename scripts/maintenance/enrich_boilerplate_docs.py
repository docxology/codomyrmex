import os
import ast
from pathlib import Path
from datetime import datetime

BOILERPLATE_SIG = "Internal module for the Codomyrmex ecosystem."

def extract_module_name(path_str):
    name = os.path.basename(path_str)
    if name in ('src', 'codomyrmex', 'projects'):
        return path_str.split('/')[-1]
    return name.replace('_', ' ').title()

def get_ast_context(filepath):
    try:
        content = filepath.read_text(encoding='utf-8')
        tree = ast.parse(content)
        docstring = ast.get_docstring(tree)
        classes = []
        functions = []
        for node in tree.body:
            if isinstance(node, ast.ClassDef):
                c_doc = ast.get_docstring(node)
                classes.append((node.name, c_doc))
            elif isinstance(node, ast.FunctionDef):
                f_doc = ast.get_docstring(node)
                functions.append((node.name, f_doc))
        return docstring, classes, functions
    except Exception:
        return None, [], []

def get_folder_context(directory):
    py_files = []
    sh_files = []
    other_files = []
    subdirs = []
    for f in directory.iterdir():
        if f.name in ('.git', '__pycache__', '.pytest_cache', '.venv', '.github', 'node_modules', '.mypy_cache'):
            continue
        if f.is_dir():
            subdirs.append(f.name)
        elif f.is_file():
            if f.name.endswith('.py'):
                py_files.append(f)
            elif f.name.endswith('.sh'):
                sh_files.append(f)
            elif f.name not in ('README.md', 'AGENTS.md', 'SPEC.md'):
                other_files.append(f.name)
    return py_files, sh_files, other_files, subdirs

def build_readme(module_name, py_files, sh_files, other_files, subdirs):
    lines = [f"# {module_name}", ""]
    
    # Extract main docstring if __init__.py exists
    main_doc = ""
    for pyf in py_files:
        if pyf.name == '__init__.py':
            md, _, _ = get_ast_context(pyf)
            if md:
                main_doc = md
                break
    
    if main_doc:
        lines.append(main_doc)
        lines.append("")
    else:
        lines.append(f"The `{module_name}` module provides components and workflows within the Codomyrmex ecosystem.")
        lines.append("")
    
    if py_files:
        lines.append("## Core Components")
        lines.append("")
        for pyf in py_files:
            md, classes, funcs = get_ast_context(pyf)
            desc = md.split('\n')[0] if md else "Implementation file."
            lines.append(f"- **`{pyf.name}`**: {desc}")
            for c_name, c_doc in classes[:3]:
                cd = c_doc.split('\n')[0] if c_doc else "Class definition."
                lines.append(f"  - `{c_name}`: {cd}")
        lines.append("")
        
    if sh_files or other_files:
        lines.append("## Resources")
        lines.append("")
        for f in sh_files:
            lines.append(f"- Executable script: `{f.name}`")
        for f in other_files[:10]:
            lines.append(f"- Asset: `{f}`")
        if len(other_files) > 10:
            lines.append(f"- ...and {len(other_files) - 10} other assets.")
        lines.append("")
        
    if subdirs:
        lines.append("## Structure")
        lines.append("")
        for d in subdirs:
            lines.append(f"- `{d}/`")
        lines.append("")
        
    return "\n".join(lines)

def build_agents(module_name, date, classes):
    lines = [
        f"# {module_name} Agents — Local Coordination",
        "",
        f"**Version**: v1.0.0 | **Status**: Active | **Last Updated**: {date}",
        "",
        "## Purpose",
        "",
        f"Coordination hub for AI agents interacting with the `{module_name}` subsystem.",
        ""
    ]
    
    if classes:
        lines.append("## Identified Entry Points")
        lines.append("")
        for cls in classes[:5]:
            lines.append(f"- Central entity recognized: `{cls[0]}`")
        lines.append("")
        
    lines.extend([
        "## Operating Contracts",
        "",
        "- **Modularity Focus**: Modifications should strictly target localized files.",
        "- **Context Gathering**: Read adjacent component files before executing edits.",
        "- **Zero-Mock Policy**: All testing involving these components must reflect genuine execution mechanics."
    ])
    return "\n".join(lines)

def build_spec(module_name, py_files):
    lines = [
        f"# {module_name} Specification",
        "",
        "## 1. Description",
        "",
        f"This specification outlines the technical and functional requirements for `{module_name}`."
    ]
    
    if py_files:
        lines.append("")
        lines.append("## 2. Technical Boundaries")
        lines.append("")
        for pyf in py_files:
            _, _, funcs = get_ast_context(pyf)
            if funcs:
                lines.append(f"### `{pyf.name}` Exports")
                for fn_name, _ in funcs[:5]:
                    lines.append(f"- Method signature implemented: `{fn_name}()`")
                if len(funcs) > 5:
                    lines.append("- (Truncated list of methods)")
                    
    lines.extend([
        "",
        "## 3. Core Capabilities",
        "",
        "- Maintains local coherence independent of global orchestrator state.",
        f"- Inherits the Codomyrmex ecosystem's constraints when executing `{module_name}` routines."
    ])
    
    return "\n".join(lines)

def enrich_docs(start_path):
    start_dir = Path(start_path)
    if not start_dir.exists():
        return
        
    today = datetime.now().strftime("%B %Y")
    
    total_enriched = 0
    
    for root, dirs, files in os.walk(start_dir):
        # Prevent recursion into ignored folders
        dirs[:] = [d for d in dirs if d not in ('.git', '__pycache__', '.pytest_cache', '.venv', '.github', 'node_modules', '.mypy_cache', 'docs', 'documentation')]
        
        if 'README.md' not in files:
            continue
            
        current_dir = Path(root)
        readme_path = current_dir / 'README.md'
        
        try:
            content = readme_path.read_text(encoding='utf-8')
            if BOILERPLATE_SIG in content:
                module_name = extract_module_name(root)
                py_files, sh_files, other_files, subdirs = get_folder_context(current_dir)
                
                # Fetch all classes for AGENTS.md
                all_classes = []
                for pyf in py_files:
                    _, cls_list, _ = get_ast_context(pyf)
                    all_classes.extend(cls_list)
                
                # Rebuild README
                new_readme = build_readme(module_name, py_files, sh_files, other_files, subdirs)
                readme_path.write_text(new_readme, encoding='utf-8')
                
                # Rebuild AGENTS.md if it's there and generic
                agents_path = current_dir / 'AGENTS.md'
                if agents_path.exists():
                    agents_content = agents_path.read_text(encoding='utf-8')
                    if "Coordination and navigation hub for agents" in agents_content:
                        new_agents = build_agents(module_name, today, all_classes)
                        agents_path.write_text(new_agents, encoding='utf-8')
                        
                # Rebuild SPEC.md if it's there and generic
                spec_path = current_dir / 'SPEC.md'
                if spec_path.exists():
                    spec_content = spec_path.read_text(encoding='utf-8')
                    if "Functional and technical requirements for the" in spec_content:
                        new_spec = build_spec(module_name, py_files)
                        spec_path.write_text(new_spec, encoding='utf-8')
                
                print(f"Enriched: {current_dir.relative_to(start_dir.parent)}")
                total_enriched += 1
        except Exception as e:
            print(f"Error processing {current_dir}: {e}")
            
    print(f"Total Enriched: {total_enriched}")

if __name__ == "__main__":
    repo_root = "/Users/mini/Documents/GitHub/codomyrmex"
    print("Running Doc Enrichment...")
    enrich_docs(f"{repo_root}/src/codomyrmex")
    enrich_docs(f"{repo_root}/projects")
    print("Done")

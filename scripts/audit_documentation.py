#!/usr/bin/env python3
"""
scripts/audit_documentation.py

Audits the documentation completeness of the codomyrmex repository.
Checks for the presence and quality of RASP files (README, AGENTS, SPEC, PAI)
and Python specific requirements (py.typed, docstrings).
"""

import os
import ast
import argparse
import sys
from pathlib import Path
from typing import List

REQUIRED_DOCS = ["README.md", "AGENTS.md", "SPEC.md", "PAI.md"]
PLACEHOLDER_TEXTS = ["Placeholder", "TODO: Add documentation", "# New Module"]

class ModuleAudit:
    def __init__(self, path: Path, src_root: Path):
        self.path = path
        self.name = path.name
        self.relative_path = path.relative_to(src_root)
        self.missing_docs: List[str] = []
        self.placeholder_docs: List[str] = []
        self.has_py_typed = False
        self.init_has_docstring = False
        self.files_count = 0

    def audit(self):
        # Check RASP files
        for doc in REQUIRED_DOCS:
            doc_path = self.path / doc
            if not doc_path.exists():
                self.missing_docs.append(doc)
            else:
                try:
                    content = doc_path.read_text()
                    if len(content) < 50 or any(p in content for p in PLACEHOLDER_TEXTS):
                        self.placeholder_docs.append(doc)
                except Exception:
                    self.missing_docs.append(doc) # Treat unreadable as missing

        # Check py.typed
        if (self.path / "py.typed").exists():
            self.has_py_typed = True

        # Check __init__.py
        init_path = self.path / "__init__.py"
        if init_path.exists():
            try:
                tree = ast.parse(init_path.read_text())
                if ast.get_docstring(tree):
                    self.init_has_docstring = True
            except Exception:
                pass

        # Count python files
        self.files_count = len(list(self.path.glob("*.py")))

def is_package(path: Path) -> bool:
    return path.is_dir() and (path / "__init__.py").exists()

def generate_report(audits: List[ModuleAudit], report_file: Path):
    total_modules = len(audits)
    perfect_modules = 0
    modules_missing_rasp = 0
    modules_with_placeholders = 0
    modules_missing_typed = 0
    
    report_lines = [
        "# Documentation Audit Report",
        "",
        f"**Date**: {os.popen('date').read().strip()}",
        f"**Total Modules Scanned**: {total_modules}",
        "",
        "## Summary",
        "",
    ]

    for audit in audits:
        is_perfect = (
            not audit.missing_docs and 
            not audit.placeholder_docs and 
            audit.has_py_typed and 
            audit.init_has_docstring
        )
        if is_perfect:
            perfect_modules += 1
        
        if audit.missing_docs:
            modules_missing_rasp += 1
        if audit.placeholder_docs:
            modules_with_placeholders += 1
        if not audit.has_py_typed:
            modules_missing_typed += 1

    report_lines.append(f"- **Perfect Compliance**: {perfect_modules} / {total_modules} ({perfect_modules/total_modules:.1%})")
    report_lines.append(f"- **Missing Any RASP**: {modules_missing_rasp}")
    report_lines.append(f"- **Placeholder RASP**: {modules_with_placeholders}")
    report_lines.append(f"- **Missing py.typed**: {modules_missing_typed}")
    report_lines.append("")
    report_lines.append("## Detailed Compliance Matrix")
    report_lines.append("")
    report_lines.append("| Module | Missing | Placeholders | py.typed | init doc |")
    report_lines.append("| :--- | :--- | :--- | :---: | :---: |")

    # Sort by number of issues (most issues first)
    audits.sort(key=lambda x: len(x.missing_docs) + len(x.placeholder_docs) + (0 if x.has_py_typed else 1), reverse=True)

    for audit in audits:
        missing_str = ", ".join(audit.missing_docs) if audit.missing_docs else "✅"
        placeholder_str = ", ".join(audit.placeholder_docs) if audit.placeholder_docs else "✅"
        typed_str = "✅" if audit.has_py_typed else "❌"
        init_doc_str = "✅" if audit.init_has_docstring else "❌"
        
        # Highlight checking row if it has issues
        if missing_str != "✅" or placeholder_str != "✅" or typed_str == "❌" or init_doc_str == "❌":
            report_lines.append(f"| `{audit.relative_path}` | {missing_str} | {placeholder_str} | {typed_str} | {init_doc_str} |")

    try:
        report_file.write_text("\n".join(report_lines))
        print(f"Report generated at: {report_file}")
    except Exception as e:
        print(f"Error writing report to {report_file}: {e}", file=sys.stderr)

def main():
    parser = argparse.ArgumentParser(description="Audit documentation completeness.")
    parser.add_argument("--root", type=Path, default=Path(__file__).parent.parent, help="Project root directory")
    parser.add_argument("--report", type=Path, default=None, help="Output path for the report file")
    
    args = parser.parse_args()
    
    root_dir = args.root
    src_dir = root_dir / "src" / "codomyrmex"
    report_file = args.report or (root_dir / "docs_audit_report.md")

    if not src_dir.exists():
        print(f"Error: Source directory {src_dir} does not exist.")
        return

    audits = []
    
    for root, dirs, files in os.walk(src_dir):
        root_path = Path(root)
        if is_package(root_path):
            # Skip hidden directories
            if any(part.startswith('.') for part in root_path.relative_to(src_dir).parts):
                continue
                
            audit = ModuleAudit(root_path, src_dir)
            audit.audit()
            audits.append(audit)

    if not audits:
        print("No modules found to audit.")
        return

    generate_report(audits, report_file)

if __name__ == "__main__":
    main()

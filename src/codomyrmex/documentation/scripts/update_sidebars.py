from pathlib import Path
import json















#!/usr/bin/env python3
"""Generate sidebar entries for Docusaurus based on aggregated docs in docs/modules.

This script scans src/codomyrmex/documentation/docs/modules and emits a JSON-like
structure fragment that can be manually merged into sidebars.js or used to
automate sidebar updates.
"""

ROOT = Path(__file__).resolve().parents[1] / "docs" / "modules"


def scan_modules(root: Path):
    """Scan Modules.

        Args:        root: Parameter for the operation.

        Returns:        The result of the operation.
        """
    modules = {}
    for module_dir in sorted([p for p in root.iterdir() if p.is_dir()]):
        docs = []
        for md in sorted(module_dir.rglob("*.md")):
            rel = md.relative_to(root)
            docs.append(str(rel).replace("\\", "/"))
        modules[module_dir.name] = docs
    return modules


def main():
    modules = scan_modules(ROOT)
    print(json.dumps(modules, indent=2))


if __name__ == "__main__":
    main()

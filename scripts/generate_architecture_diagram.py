#!/usr/bin/env python3
"""
scripts/generate_architecture_diagram.py

Auto-generates a Mermaid architecture diagram from static import analysis
using codomyrmex.static_analysis.imports. Outputs to docs/ARCHITECTURE.md.
"""

import argparse
import sys
from pathlib import Path

# Ensure src is in path
PROJ_ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = PROJ_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

try:
    from codomyrmex.static_analysis.imports import scan_imports, get_layer
except ImportError as e:
    print(f"Error importing codomyrmex module: {e}")
    sys.exit(1)


def generate_mermaid(src_dir: Path) -> str:
    edges = scan_imports(src_dir)
    
    # Extract all unique modules
    modules = set()
    # Extract unique edges between modules (ignore file-level granularity)
    unique_links = set()
    
    for edge in edges:
        src = edge["src"]
        dst = edge["dst"]
        modules.add(src)
        modules.add(dst)
        unique_links.add((src, dst))
        
    # Group modules by layer
    layers = {
        "foundation": [],
        "core": [],
        "service": [],
        "specialized": [],
        "other": []
    }
    
    for mod in modules:
        layers[get_layer(mod)].append(mod)
        
    for k in layers:
        layers[k] = sorted(layers[k])
        
    # Build mermaid diagram
    lines = [
        "# Codomyrmex System Architecture",
        "",
        "This diagram is auto-generated from static import analysis.",
        "",
        "```mermaid",
        "graph TD",
    ]
    
    # Subgraphs
    for layer_name in ["foundation", "core", "service", "specialized", "other"]:
        mods = layers[layer_name]
        if not mods:
            continue
        lines.append(f"  subgraph {layer_name.capitalize()}")
        for m in mods:
            lines.append(f"    {m}")
        lines.append("  end")
        
    # Edges
    lines.append("")
    for src, dst in sorted(unique_links):
        lines.append(f"  {src} --> {dst}")
        
    lines.append("```")
    lines.append("")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Auto-generate Mermaid architecture diagram")
    parser.add_argument("--root", type=Path, default=PROJ_ROOT, help="Project root directory")
    args = parser.parse_args()

    src_dir = args.root / "src" / "codomyrmex"
    if not src_dir.exists():
        print(f"Error: Source directory {src_dir} does not exist.")
        sys.exit(1)

    mermaid_content = generate_mermaid(src_dir)
    
    docs_dir = args.root / "docs"
    docs_dir.mkdir(exist_ok=True)
    out_file = docs_dir / "ARCHITECTURE.md"
    
    out_file.write_text(mermaid_content, encoding="utf-8")
    print(f"✅ Architecture diagram written to {out_file.relative_to(PROJ_ROOT)}")


if __name__ == "__main__":
    main()

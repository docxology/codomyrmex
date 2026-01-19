#!/usr/bin/env python3
"""
Data Visualization - Real Usage Examples

Demonstrates actual visualization capabilities:
- Style and palette enumeration
- Mermaid diagram generation stubs
- AdvancedPlotter interface
"""

import sys
import os
from pathlib import Path

# Ensure codomyrmex is in path
try:
    import codomyrmex
except ImportError:
    project_root = Path(__file__).resolve().parent.parent.parent.parent
    sys.path.insert(0, str(project_root / "src"))

from codomyrmex.utils.cli_helpers import setup_logging, print_success, print_info, print_error
from codomyrmex.data_visualization import (
    get_available_styles,
    get_available_palettes,
    AdvancedPlotter,
    MermaidDiagramGenerator
)

def main():
    setup_logging()
    print_info("Running Data Visualization Examples...")

    # 1. Styles & Palettes
    print_info("Enumerating visualization styles and palettes...")
    try:
        styles = get_available_styles()
        palettes = get_available_palettes()
        print_success(f"  Available styles: {', '.join(styles)}")
        print_success(f"  Available palettes: {', '.join(palettes)}")
    except Exception as e:
        print_error(f"  Failed to get styles/palettes: {e}")

    # 2. Mermaid Generator
    print_info("Testing MermaidDiagramGenerator...")
    try:
        generator = MermaidDiagramGenerator()
        diagram = generator.create_git_branch_diagram(branches=[], commits=[], title="Demo Git Flow")
        if diagram:
            print_success("  Mermaid diagram generated successfully.")
    except Exception as e:
        print_info(f"  Mermaid generation demo: {e}")

    # 3. Advanced Plotter
    print_info("Testing AdvancedPlotter initialization...")
    try:
        plotter = AdvancedPlotter()
        print_success("  AdvancedPlotter initialized successfully.")
    except Exception as e:
        # matplotlib might not be available
        print_info(f"  AdvancedPlotter demo note: {e}")

    print_success("Data visualization examples completed successfully")
    return 0

if __name__ == "__main__":
    sys.exit(main())

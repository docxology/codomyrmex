#!/usr/bin/env python3
"""
Data Visualization - Advanced Workflow

Demonstrates advanced visualization workflows:
- Mermaid diagram generation
- Git repository visualization  
- Multi-panel dashboards
"""

import sys
from pathlib import Path

# Ensure codomyrmex is in path
try:
    import codomyrmex
except ImportError:
    project_root = Path(__file__).resolve().parent.parent.parent.parent
    sys.path.insert(0, str(project_root / "src"))

from codomyrmex.utils.cli_helpers import setup_logging, print_success, print_info, print_error


def main():
    setup_logging()
    print_info("Running Advanced Data Visualization Workflow...")

    try:
        from codomyrmex.data_visualization import (
            MermaidDiagramGenerator,
            create_git_branch_diagram,
            create_repository_structure_diagram,
            GitVisualizer,
            AdvancedPlotter,
            PlotConfig,
            ChartStyle,
            ColorPalette,
        )
        print_info("Successfully imported advanced visualization components")
    except ImportError as e:
        print_error(f"Could not import data_visualization: {e}")
        return 1

    # Example 1: Mermaid diagram generation
    print_info("Mermaid Diagram Generation:")
    print("  MermaidDiagramGenerator capabilities:")
    print("    - create_git_branch_diagram(): Git branch flow")
    print("    - create_git_workflow_diagram(): CI/CD workflow")
    print("    - create_repository_structure_diagram(): Folder tree")
    print("    - create_commit_timeline_diagram(): Commit history")

    # Example 2: Git visualization
    print_info("Git Visualization:")
    print("  GitVisualizer capabilities:")
    print("    - visualize_git_repository(): Full repo viz")
    print("    - create_git_tree_png(): PNG export")
    print("    - create_git_tree_mermaid(): Mermaid export")

    # Example 3: AdvancedPlotter configuration
    print_info("AdvancedPlotter configuration options:")
    print("  Chart Styles:")
    for style in list(ChartStyle)[:4]:
        print(f"    - {style.name}: {style.value}")
    
    print("  Color Palettes:")
    for palette in list(ColorPalette)[:4]:
        print(f"    - {palette.name}: {palette.value}")

    # Example 4: Dashboard creation workflow
    print_info("Multi-panel Dashboard workflow:")
    print("  1. Define data sources")
    print("  2. Configure PlotConfig for each panel")
    print("  3. Set layout grid (rows, cols)")
    print("  4. Call create_dashboard()")
    print("  5. Export to PNG/SVG/HTML")

    # Example 5: Integration with other modules
    print_info("Cross-module integration:")
    print("  - metrics → data_visualization: Performance charts")
    print("  - git_operations → data_visualization: Commit graphs")
    print("  - static_analysis → data_visualization: Code metrics")
    print("  - database_management → data_visualization: Query stats")

    print_success("Advanced Data Visualization workflow completed successfully")
    return 0


if __name__ == "__main__":
    sys.exit(main())

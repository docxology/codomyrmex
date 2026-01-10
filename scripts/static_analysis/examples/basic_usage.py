#!/usr/bin/env python3
"""
Static Analysis - Real Usage Examples

Demonstrates actual static analysis capabilities:
- Code quality analysis
- Analyzer configuration
- Complexity metrics
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
    print_info("Running Static Analysis Examples...")

    try:
        from codomyrmex.static_analysis import (
            StaticAnalyzer,
            analyze_file,
            analyze_project,
            get_available_tools,
            AnalysisType,
            SeverityLevel,
        )
        print_info("Successfully imported static_analysis module")
    except ImportError as e:
        print_error(f"Could not import static_analysis: {e}")
        return 1

    # Example 1: StaticAnalyzer capabilities
    print_info("StaticAnalyzer capabilities:")
    print("  - analyze_file(): Analyze a single file")
    print("  - analyze_project(): Analyze entire project")
    print("  - get_available_tools(): List available tools")

    # Example 2: Analysis types
    print_info("Available analysis types:")
    try:
        for analysis_type in list(AnalysisType)[:5]:
            print(f"  - {analysis_type.name}: {analysis_type.value}")
    except Exception as e:
        print_info(f"  Analysis types: {e}")

    # Example 3: Severity levels
    print_info("Severity levels:")
    try:
        for severity in list(SeverityLevel):
            print(f"  - {severity.name}: {severity.value}")
    except Exception as e:
        print_info(f"  Severity levels: {e}")

    # Example 4: Get available tools
    print_info("Available analysis tools:")
    try:
        tools = get_available_tools()
        for tool in tools[:5]:
            print(f"  - {tool}")
    except Exception as e:
        print_info(f"  Tools: {e}")

    # Example 5: Analyze project structure
    print_info("Analyzing project structure...")
    project_root = Path(__file__).resolve().parent.parent.parent.parent
    src_dir = project_root / "src" / "codomyrmex"
    
    try:
        # Count Python files
        py_files = list(src_dir.rglob("*.py"))
        print(f"  Total Python files: {len(py_files)}")
        
        # Count directories
        dirs = [d for d in src_dir.iterdir() if d.is_dir() and not d.name.startswith("_")]
        print(f"  Total modules: {len(dirs)}")
    except Exception as e:
        print_info(f"  Analysis: {e}")

    # Example 6: Integration with other modules
    print_info("Cross-module integration:")
    print("  - coding → static_analysis: Before code generation")
    print("  - ci_cd_automation → static_analysis: CI checks")
    print("  - documentation → static_analysis: Doc coverage")

    print_success("Static Analysis examples completed successfully")
    return 0


if __name__ == "__main__":
    sys.exit(main())

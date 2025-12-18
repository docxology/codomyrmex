#!/usr/bin/env python3
"""
Comprehensive Project Analysis Tool

Analyzes the Codomyrmex project structure, dependencies, and code quality.
Provides insights for maintenance and development.
"""

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Any


def analyze_project_structure() -> Dict[str, Any]:
    """Analyze the overall project structure."""
    project_root = Path(__file__).parent.parent.parent.parent

    structure = {
        "directories": {},
        "files": {},
        "total_size": 0,
        "file_types": {}
    }

    for root, dirs, files in os.walk(project_root):
        # Skip common directories
        skip_dirs = {'.git', '__pycache__', '.pytest_cache', '.mypy_cache', '.venv', 'node_modules'}
        dirs[:] = [d for d in dirs if d not in skip_dirs]

        rel_root = os.path.relpath(root, project_root)

        if rel_root == '.':
            rel_root = 'root'

        structure["directories"][rel_root] = {
            "subdirs": len(dirs),
            "files": len(files),
            "files_list": [f for f in files if not f.startswith('.')]
        }

        for file in files:
            if file.startswith('.'):
                continue

            file_path = os.path.join(root, file)
            file_size = os.path.getsize(file_path)
            structure["total_size"] += file_size

            # Track file types
            ext = Path(file).suffix.lower()
            if ext not in structure["file_types"]:
                structure["file_types"][ext] = []
            structure["file_types"][ext].append(file)

    return structure


def analyze_dependencies() -> Dict[str, Any]:
    """Analyze project dependencies."""
    deps = {
        "python_requires": ">=3.10",
        "main_dependencies": [],
        "dev_dependencies": [],
        "total_count": 0
    }

    # Read pyproject.toml if available
    pyproject_path = Path(__file__).parent.parent.parent.parent / "pyproject.toml"
    if pyproject_path.exists():
        try:
            import tomllib
            with open(pyproject_path, "rb") as f:
                data = tomllib.load(f)

            if "project" in data and "dependencies" in data["project"]:
                deps["main_dependencies"] = data["project"]["dependencies"]

            if "tool" in data and "uv" in data["tool"] and "dev-dependencies" in data["tool"]["uv"]:
                deps["dev_dependencies"] = data["tool"]["uv"]["dev-dependencies"]

        except ImportError:
            print("tomllib not available, skipping pyproject.toml analysis")
        except Exception as e:
            print(f"Error reading pyproject.toml: {e}")

    deps["total_count"] = len(deps["main_dependencies"]) + len(deps["dev_dependencies"])
    return deps


def analyze_code_quality() -> Dict[str, Any]:
    """Analyze code quality metrics."""
    quality = {
        "total_python_files": 0,
        "test_files": 0,
        "documentation_files": 0,
        "has_tests": False,
        "has_docs": False,
        "has_ci": False,
        "has_linting": False
    }

    project_root = Path(__file__).parent.parent.parent.parent

    # Count Python files
    for py_file in project_root.rglob("*.py"):
        quality["total_python_files"] += 1
        if py_file.name.startswith("test_") or "test" in py_file.parts:
            quality["test_files"] += 1

    # Count documentation files
    for md_file in project_root.rglob("*.md"):
        quality["documentation_files"] += 1

    # Check for testing setup
    quality["has_tests"] = (project_root / "testing").exists() or (project_root / "tests").exists()

    # Check for CI configuration
    quality["has_ci"] = (project_root / ".github" / "workflows").exists()

    # Check for linting configuration
    quality["has_linting"] = (
        (project_root / "pyproject.toml").exists() or
        (project_root / ".flake8").exists() or
        (project_root / "setup.cfg").exists()
    )

    return quality


def generate_report(structure: Dict, deps: Dict, quality: Dict) -> str:
    """Generate a comprehensive analysis report."""
    report = []
    report.append("# Codomyrmex Project Analysis Report")
    report.append("=" * 50)
    report.append("")

    # Project Structure
    report.append("## Project Structure")
    report.append(f"- **Total Size**: {structure['total_size'] / 1024 / 1024:.2f} MB")
    report.append(f"- **Directories**: {len(structure['directories'])}")
    report.append(f"- **Python Files**: {quality['total_python_files']}")
    report.append(f"- **Documentation Files**: {quality['documentation_files']}")
    report.append("")

    # File Types
    report.append("## File Types")
    for ext, files in sorted(structure['file_types'].items()):
        report.append(f"- **{ext}**: {len(files)} files")
    report.append("")

    # Dependencies
    report.append("## Dependencies")
    report.append(f"- **Main Dependencies**: {len(deps['main_dependencies'])}")
    report.append(f"- **Dev Dependencies**: {len(deps['dev_dependencies'])}")
    report.append(f"- **Total Dependencies**: {deps['total_count']}")
    report.append("")

    # Code Quality
    report.append("## Code Quality")
    report.append(f"- **Has Tests**: {'✅' if quality['has_tests'] else '❌'}")
    report.append(f"- **Has CI**: {'✅' if quality['has_ci'] else '❌'}")
    report.append(f"- **Has Linting**: {'✅' if quality['has_linting'] else '❌'}")
    report.append(f"- **Test Coverage**: {quality['test_files']}/{quality['total_python_files']} files")
    report.append("")

    # Recommendations
    report.append("## Recommendations")
    if not quality['has_tests']:
        report.append("- ⚠️  Consider adding tests for better code reliability")
    if not quality['has_ci']:
        report.append("- ⚠️  Consider adding GitHub Actions for continuous integration")
    if not quality['has_linting']:
        report.append("- ⚠️  Consider adding code linting configuration")
    if quality['total_python_files'] > 100 and quality['test_files'] < quality['total_python_files'] * 0.5:
        report.append("- ⚠️  Consider increasing test coverage")
    report.append("")

    return "\n".join(report)


def main():
    """Main function to run the analysis."""
    parser = argparse.ArgumentParser(description="Analyze Codomyrmex project structure")
    parser.add_argument("--output", "-o", help="Output file for the report")
    parser.add_argument("--json", action="store_true", help="Output JSON format")

    args = parser.parse_args()

    print("🔍 Analyzing Codomyrmex project...")

    # Run analyses
    structure = analyze_project_structure()
    deps = analyze_dependencies()
    quality = analyze_code_quality()

    if args.json:
        # Output JSON
        result = {
            "structure": structure,
            "dependencies": deps,
            "quality": quality
        }

        if args.output:
            with open(args.output, 'w') as f:
                json.dump(result, f, indent=2)
        else:
            print(json.dumps(result, indent=2))
    else:
        # Output human-readable report
        report = generate_report(structure, deps, quality)

        if args.output:
            with open(args.output, 'w') as f:
                f.write(report)
        else:
            print(report)

    print("✅ Analysis complete!")


if __name__ == "__main__":
    main()

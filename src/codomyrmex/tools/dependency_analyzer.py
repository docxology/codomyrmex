#!/usr/bin/env python3
"""
Dependency Analyzer for Codomyrmex Modules.

This tool analyzes module dependencies to:
- Detect circular import dependencies
- Validate dependency hierarchy
- Generate dependency graph visualizations
- Enforce module boundaries
"""

import ast
import sys
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Set, Tuple

try:
    from codomyrmex.logging_monitoring.logger_config import get_logger, setup_logging

    setup_logging()
    logger = get_logger(__name__)
except ImportError:
    import logging

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)


class DependencyAnalyzer:
    """Analyzes module dependencies for circular imports and hierarchy violations."""

    def __init__(self, repo_root: Path):
        """Initialize analyzer with repository root."""
        self.repo_root = repo_root.resolve()
        self.src_path = self.repo_root / "src" / "codomyrmex"
        self.imports: Dict[str, Set[str]] = defaultdict(set)
        self.modules: Set[str] = set()
        self.circular_deps: List[Tuple[str, str]] = []
        self.violations: List[Dict[str, str]] = []

        # Define allowed dependency layers (from relationships.md)
        self.allowed_dependencies = {
            # Foundation layer (can import from nothing)
            "environment_setup": set(),
            "logging_monitoring": set(),
            "model_context_protocol": set(),
            # AI & Intelligence layer
            "ai_code_editing": {"logging_monitoring", "environment_setup", "model_context_protocol"},
            "pattern_matching": {"logging_monitoring", "environment_setup"},
            # Analysis & Quality layer
            "static_analysis": {"logging_monitoring"},
            "code_execution_sandbox": {"logging_monitoring"},
            "security_audit": {"logging_monitoring", "static_analysis"},
            # Visualization layer
            "data_visualization": {"logging_monitoring"},
            # Build & Deploy layer
            "build_synthesis": {"logging_monitoring", "static_analysis"},
            "git_operations": {"logging_monitoring"},
            "containerization": {"logging_monitoring"},
            "ci_cd_automation": {"logging_monitoring", "build_synthesis", "containerization"},
            # Application layer
            "project_orchestration": {"logging_monitoring"},  # Can import from all, but validate
            "terminal_interface": set(),
            "system_discovery": {"logging_monitoring"},
            # Other modules
            "config_management": {"logging_monitoring"},
            "database_management": {"logging_monitoring"},
            "documentation": set(),  # Can import from all
            "api_documentation": {"logging_monitoring", "static_analysis"},
            "code_review": {"logging_monitoring", "ai_code_editing", "static_analysis"},
            "language_models": {"logging_monitoring", "model_context_protocol"},
            "ollama_integration": {"logging_monitoring", "model_context_protocol"},
            "performance": {"logging_monitoring"},
            "modeling_3d": {"logging_monitoring"},
            "physical_management": {"logging_monitoring"},
            "module_template": set(),
        }

    def extract_imports(self, file_path: Path) -> Set[str]:
        """Extract all codomyrmex imports from a Python file."""
        imports = set()
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            tree = ast.parse(content, filename=str(file_path))

            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        if alias.name.startswith("codomyrmex."):
                            module_name = alias.name.split(".")[1]  # Get module name
                            imports.add(module_name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module and node.module.startswith("codomyrmex."):
                        module_name = node.module.split(".")[1]  # Get module name
                        imports.add(module_name)

        except SyntaxError as e:
            logger.warning(f"Syntax error in {file_path}: {e}")
        except Exception as e:
            logger.error(f"Error parsing {file_path}: {e}")

        return imports

    def scan_module(self, module_name: str) -> None:
        """Scan a module for imports."""
        module_path = self.src_path / module_name
        if not module_path.exists():
            return

        self.modules.add(module_name)
        module_imports = set()

        # Scan all Python files in the module
        for py_file in module_path.rglob("*.py"):
            if py_file.name.startswith("test_") or py_file.name == "__init__.py":
                continue  # Skip test files and __init__.py for now

            file_imports = self.extract_imports(py_file)
            module_imports.update(file_imports)

        self.imports[module_name] = module_imports

    def scan_all_modules(self) -> None:
        """Scan all modules in the repository."""
        if not self.src_path.exists():
            logger.error(f"Source path not found: {self.src_path}")
            return

        for item in self.src_path.iterdir():
            if item.is_dir() and not item.name.startswith("_") and item.name != "output":
                self.scan_module(item.name)

    def detect_circular_dependencies(self) -> List[Tuple[str, str]]:
        """Detect circular import dependencies."""
        circular = []

        # Build dependency graph
        graph: Dict[str, Set[str]] = {module: set(self.imports[module]) for module in self.modules}

        def has_cycle(start: str, current: str, visited: Set[str], path: List[str]) -> bool:
            """Check if there's a cycle from start to current."""
            if current in visited:
                if current == start:
                    return True
                return False

            visited.add(current)
            path.append(current)

            for neighbor in graph.get(current, set()):
                if has_cycle(start, neighbor, visited.copy(), path.copy()):
                    return True

            return False

        # Check each module for cycles
        for module in self.modules:
            if has_cycle(module, module, set(), []):
                # Find the actual cycle path
                for dep in self.imports[module]:
                    if dep in self.modules and module in self.imports.get(dep, set()):
                        circular.append((module, dep))

        self.circular_deps = circular
        return circular

    def validate_dependency_hierarchy(self) -> List[Dict[str, str]]:
        """Validate that modules follow the allowed dependency hierarchy."""
        violations = []

        for module, imports in self.imports.items():
            if module not in self.allowed_dependencies:
                # Unknown module - allow all imports for now
                continue

            allowed = self.allowed_dependencies[module]

            for imported_module in imports:
                if imported_module not in self.modules:
                    continue  # External import, skip

                # Special case: project_orchestration can import from all modules
                if module == "project_orchestration":
                    continue

                # Special case: documentation can import from all modules
                if module == "documentation":
                    continue

                if imported_module not in allowed:
                    violations.append(
                        {
                            "module": module,
                            "imported": imported_module,
                            "allowed": ", ".join(sorted(allowed)) if allowed else "none",
                            "severity": "error",
                        }
                    )

        self.violations = violations
        return violations

    def generate_report(self) -> str:
        """Generate a human-readable dependency analysis report."""
        lines = [
            "# Dependency Analysis Report",
            "",
            f"*Analyzed {len(self.modules)} modules*",
            "",
            "## Circular Dependencies",
            "",
        ]

        if self.circular_deps:
            lines.append("❌ **Circular dependencies detected:**")
            lines.append("")
            for mod1, mod2 in self.circular_deps:
                lines.append(f"- `{mod1}` ↔ `{mod2}` (circular dependency)")
            lines.append("")
        else:
            lines.append("✅ **No circular dependencies detected**")
            lines.append("")

        lines.extend(
            [
                "## Hierarchy Violations",
                "",
            ]
        )

        if self.violations:
            lines.append("❌ **Dependency hierarchy violations:**")
            lines.append("")
            lines.append("| Module | Imported Module | Allowed Dependencies | Severity |")
            lines.append("|--------|----------------|---------------------|----------|")

            for violation in self.violations:
                lines.append(
                    f"| {violation['module']} | {violation['imported']} | "
                    f"{violation['allowed']} | {violation['severity']} |"
                )
            lines.append("")
        else:
            lines.append("✅ **No hierarchy violations detected**")
            lines.append("")

        # Module dependency summary
        lines.extend(
            [
                "## Module Dependency Summary",
                "",
                "| Module | Number of Dependencies | Dependencies |",
                "|--------|----------------------|---------------|",
            ]
        )

        for module in sorted(self.modules):
            deps = sorted(self.imports.get(module, set()))
            deps_str = ", ".join(deps) if deps else "none"
            lines.append(f"| {module} | {len(deps)} | {deps_str} |")

        return "\n".join(lines)

    def generate_mermaid_graph(self) -> str:
        """Generate Mermaid diagram of module dependencies."""
        lines = [
            "```mermaid",
            "graph TD",
        ]

        # Add nodes
        for module in sorted(self.modules):
            lines.append(f"    {module.replace('_', '')}[{module}]")

        # Add edges (only show violations for clarity)
        for violation in self.violations:
            mod1 = violation["module"].replace("_", "")
            mod2 = violation["imported"].replace("_", "")
            lines.append(f"    {mod1} -->|violation| {mod2}")

        # Add circular dependency edges
        for mod1, mod2 in self.circular_deps:
            m1 = mod1.replace("_", "")
            m2 = mod2.replace("_", "")
            lines.append(f"    {m1} -.->|circular| {m2}")

        lines.append("```")

        return "\n".join(lines)

    def analyze(self) -> Dict[str, any]:
        """Run complete dependency analysis."""
        logger.info("Scanning modules for dependencies...")
        self.scan_all_modules()

        logger.info("Detecting circular dependencies...")
        circular = self.detect_circular_dependencies()

        logger.info("Validating dependency hierarchy...")
        violations = self.validate_dependency_hierarchy()

        return {
            "modules": sorted(self.modules),
            "imports": {k: sorted(v) for k, v in self.imports.items()},
            "circular_dependencies": circular,
            "violations": violations,
            "summary": {
                "total_modules": len(self.modules),
                "modules_with_imports": len([m for m in self.modules if self.imports.get(m)]),
                "circular_count": len(circular),
                "violation_count": len(violations),
            },
        }


def main() -> int:
    """Main entry point."""
    repo_root = Path(__file__).parent.parent.parent.parent
    analyzer = DependencyAnalyzer(repo_root)

    logger.info("Starting dependency analysis...")
    results = analyzer.analyze()

    # Print summary
    print("\n" + "=" * 60)
    print("Dependency Analysis Results")
    print("=" * 60)
    print(f"\nModules analyzed: {results['summary']['total_modules']}")
    print(f"Circular dependencies: {results['summary']['circular_count']}")
    print(f"Hierarchy violations: {results['summary']['violation_count']}")

    if results["circular_dependencies"]:
        print("\n❌ Circular dependencies found:")
        for mod1, mod2 in results["circular_dependencies"]:
            print(f"  - {mod1} ↔ {mod2}")

    if results["violations"]:
        print("\n❌ Hierarchy violations found:")
        for violation in results["violations"][:10]:  # Show first 10
            print(
                f"  - {violation['module']} imports {violation['imported']} "
                f"(allowed: {violation['allowed']})"
            )
        if len(results["violations"]) > 10:
            print(f"  ... and {len(results['violations']) - 10} more")

    # Generate report file
    report_file = repo_root / "docs" / "modules" / "dependency-analysis.md"
    report_content = analyzer.generate_report()
    report_content += "\n\n" + analyzer.generate_mermaid_graph()

    report_file.parent.mkdir(parents=True, exist_ok=True)
    with open(report_file, "w", encoding="utf-8") as f:
        f.write(report_content)

    print(f"\n✅ Analysis report written to: {report_file}")

    # Return exit code based on issues
    if results["circular_dependencies"] or results["violations"]:
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())


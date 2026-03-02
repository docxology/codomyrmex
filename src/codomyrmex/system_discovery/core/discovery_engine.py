"""System Discovery Engine for Codomyrmex

This module provides comprehensive system discovery capabilities, scanning all
modules, methods, classes, and functions to create a complete map of the
Codomyrmex ecosystem capabilities.
"""

import importlib
import inspect
import json
import logging
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from codomyrmex.logging_monitoring import get_logger

try:
    from codomyrmex.logging_monitoring.core.logger_config import (
        get_logger,
        setup_logging,
    )

    setup_logging()
    logger = get_logger(__name__)
except ImportError:
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

from .dependency_analyzer import DependencyAnalyzer
from .health_checker import SystemHealthChecker


@dataclass
class ModuleCapability:
    """A single discovered capability (function, class, method, or constant) within a module."""

    name: str
    module_path: str
    type: str  # 'function', 'class', 'method', 'constant'
    signature: str
    docstring: str
    file_path: str
    line_number: int
    is_public: bool
    dependencies: list[str]


@dataclass
class ModuleInfo:
    """Aggregated metadata and capabilities for a single discovered Codomyrmex module."""

    name: str
    path: str
    description: str
    version: str
    capabilities: list[ModuleCapability]
    dependencies: list[str]
    is_importable: bool
    has_tests: bool
    has_docs: bool
    last_modified: str


class SystemDiscovery:
    """
    Comprehensive system discovery and orchestration for Codomyrmex.

    This class provides the main interface for discovering all modules,
    their capabilities, system status, and interactive exploration.

    Uses DependencyAnalyzer for module metadata extraction and
    SystemHealthChecker for health/status/git operations.
    """

    def __init__(self, project_root: Path | None = None):
        """Initialize the system discovery engine.

        Args:
            project_root: Filesystem path to the project root directory.
                Defaults to the current working directory if not provided.
        """
        self.project_root = project_root or Path.cwd()
        self.src_path = self.project_root / "src"
        self.codomyrmex_path = self.src_path / "codomyrmex"
        self.testing_path = self.project_root / "testing"

        self.modules: dict[str, ModuleInfo] = {}
        self.system_status: dict[str, Any] = {}

        # Collaborators
        self._analyzer = DependencyAnalyzer(self.project_root, self.testing_path)
        self._health = SystemHealthChecker(
            self.project_root, self.src_path, self.testing_path
        )

        # Ensure src is in Python path
        if str(self.src_path) not in sys.path:
            pass

    def run_full_discovery(self) -> None:
        """Run complete system discovery, scanning all modules and printing results."""
        print("\n" + "=" * 60)
        print("   CODOMYRMEX SYSTEM DISCOVERY")
        print("=" * 60)

        print(f"\nProject Root: {self.project_root}")
        print(f"Source Path: {self.src_path}")
        print(f"Testing Path: {self.testing_path}")

        self.scan_system()
        self._display_discovery_results()
        self._display_capability_summary()

    def scan_system(self) -> dict[str, Any]:
        """Programmatically scan the system and return the inventory."""
        self._discover_modules()

        system_inventory = {
            "project_root": str(self.project_root),
            "status": {
                "python_version": sys.version.split()[0],
                "src_exists": self.src_path.exists(),
                "tests_exist": self.testing_path.exists(),
            },
            "modules": {
                name: asdict(info) for name, info in self.modules.items()
            },
            "stats": {
                "total_modules": len(self.modules),
                "importable": sum(1 for m in self.modules.values() if m.is_importable),
                "documented": sum(1 for m in self.modules.values() if m.has_docs),
                "tested": sum(1 for m in self.modules.values() if m.has_tests),
            }
        }
        return system_inventory

    def export_inventory(self, output_path: Path) -> bool:
        """Export system inventory to a JSON file.

        Args:
            output_path: Path to save the JSON file.

        Returns:
            True if successful, False otherwise.
        """
        try:
            inventory = self.scan_system()

            def default_serializer(obj):
                if isinstance(obj, (Path, set)):
                    return str(list(obj) if isinstance(obj, set) else obj)
                return str(obj)

            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(inventory, f, indent=2, default=default_serializer)

            logger.info(f"System inventory exported to {output_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to export inventory: {e}")
            return False

    def export_full_inventory(self) -> None:
        """Export complete system inventory to JSON file."""
        if not self.modules:
            self._discover_modules()
        self._health.export_full_inventory(self.modules)

    def check_git_repositories(self) -> None:
        """Check status of git repositories."""
        self._health.check_git_repositories()

    def show_status_dashboard(self) -> None:
        """Display a comprehensive system status dashboard to stdout."""
        self._health.show_status_dashboard()

    def run_demo_workflows(self) -> None:
        """Execute demonstration workflows for available modules."""
        self._health.run_demo_workflows(self.modules)

    def _discover_modules(self) -> None:
        """Find all Python modules under the codomyrmex package directory and analyze each one."""
        print(f"\nScanning modules in {self.codomyrmex_path}...")

        if not self.codomyrmex_path.exists():
            logger.error(f"Codomyrmex path does not exist: {self.codomyrmex_path}")
            return

        for module_dir in self.codomyrmex_path.iterdir():
            if module_dir.is_dir() and not module_dir.name.startswith("."):
                if (module_dir / "__init__.py").exists():
                    module_name = module_dir.name
                    print(f"  Discovering {module_name}...")

                    module_info = self._analyze_module(module_name, module_dir)
                    if module_info:
                        self.modules[module_name] = module_info

    def _analyze_module(
        self, module_name: str, module_path: Path
    ) -> ModuleInfo | None:
        """Analyze a single module directory, extracting metadata, dependencies, and capabilities."""
        try:
            module_import_path = f"codomyrmex.{module_name}"

            try:
                module = importlib.import_module(module_import_path)
                is_importable = True
                logger.info(f"Successfully imported {module_import_path}")
            except Exception as e:
                logger.warning(f"Could not import {module_import_path}: {e}")
                module = None
                is_importable = False

            description = self._analyzer.get_module_description(module_path)
            version = self._analyzer.get_module_version(module_path)
            dependencies = self._analyzer.get_module_dependencies(module_path)
            has_tests = self._analyzer.has_tests(module_name)
            has_docs = self._analyzer.has_docs(module_path)
            last_modified = self._analyzer.get_last_modified(module_path)

            capabilities = []
            if is_importable and module:
                capabilities = self._discover_module_capabilities(module, module_path)
            else:
                capabilities = self._analyzer.static_analysis_capabilities(module_path)

            return ModuleInfo(
                name=module_name,
                path=str(module_path),
                description=description,
                version=version,
                capabilities=capabilities,
                dependencies=dependencies,
                is_importable=is_importable,
                has_tests=has_tests,
                has_docs=has_docs,
                last_modified=last_modified,
            )

        except Exception as e:
            logger.error(f"Error analyzing module {module_name}: {e}")
            return None

    def _discover_module_capabilities(
        self, module: Any, module_path: Path
    ) -> list[ModuleCapability]:
        """Discover capabilities via runtime inspection of an imported module's public members."""
        capabilities = []

        try:
            for name, obj in inspect.getmembers(module):
                if name.startswith("_"):
                    continue

                capability = self._analyzer.analyze_object(name, obj, module_path)
                if capability:
                    capabilities.append(capability)

        except Exception as e:
            logger.error(f"Error discovering capabilities for {module}: {e}")

        return capabilities

    def _display_discovery_results(self) -> None:
        """Print a formatted summary of all discovered modules with status icons to stdout."""
        print("\nDiscovery Results:")
        print(f"   Found {len(self.modules)} modules")

        importable_count = sum(1 for m in self.modules.values() if m.is_importable)
        tested_count = sum(1 for m in self.modules.values() if m.has_tests)
        documented_count = sum(1 for m in self.modules.values() if m.has_docs)

        print(f"   {importable_count} importable")
        print(f"   {tested_count} have tests")
        print(f"   {documented_count} have documentation")

        print("\nModule Summary:")
        for name, info in self.modules.items():
            status_icons = []
            if info.is_importable:
                status_icons.append("OK")
            else:
                status_icons.append("FAIL")

            if info.has_tests:
                status_icons.append("T")
            if info.has_docs:
                status_icons.append("D")

            capability_count = len(info.capabilities)

            print(
                f"   {'|'.join(status_icons)} {name:<25} "
                f"({capability_count:2d} capabilities) - {info.description[:150]}"
            )

    def _display_capability_summary(self) -> None:
        """Print an aggregated breakdown of all capabilities grouped by type."""
        print("\nCapability Summary:")

        all_capabilities = []
        for module_info in self.modules.values():
            all_capabilities.extend(module_info.capabilities)

        by_type = {}
        for cap in all_capabilities:
            if cap.type not in by_type:
                by_type[cap.type] = []
            by_type[cap.type].append(cap)

        for cap_type, caps in by_type.items():
            print(f"   {cap_type:<12}: {len(caps)} items")

        print(f"\nTotal Capabilities Discovered: {len(all_capabilities)}")

    # ---- Delegate methods (preserve original private API for test compatibility) ----

    def _get_module_description(self, module_path: Path) -> str:
        """Delegate to DependencyAnalyzer."""
        return self._analyzer.get_module_description(module_path)

    def _get_module_version(self, module_path: Path) -> str:
        """Delegate to DependencyAnalyzer."""
        return self._analyzer.get_module_version(module_path)

    def _get_module_dependencies(self, module_path: Path) -> list[str]:
        """Delegate to DependencyAnalyzer."""
        return self._analyzer.get_module_dependencies(module_path)

    def _has_tests(self, module_name: str) -> bool:
        """Delegate to DependencyAnalyzer."""
        return self._analyzer.has_tests(module_name)

    def _has_docs(self, module_path: Path) -> bool:
        """Delegate to DependencyAnalyzer."""
        return self._analyzer.has_docs(module_path)

    def _get_last_modified(self, module_path: Path) -> str:
        """Delegate to DependencyAnalyzer."""
        return self._analyzer.get_last_modified(module_path)

    def _static_analysis_capabilities(self, module_path: Path) -> list[ModuleCapability]:
        """Delegate to DependencyAnalyzer."""
        return self._analyzer.static_analysis_capabilities(module_path)

    def _get_function_signature_from_ast(self, node) -> str:
        """Delegate to DependencyAnalyzer."""
        return self._analyzer.get_function_signature_from_ast(node)

    def _analyze_object(self, name: str, obj: Any, module_path: Path) -> ModuleCapability | None:
        """Delegate to DependencyAnalyzer."""
        return self._analyzer.analyze_object(name, obj, module_path)

    def _check_core_dependencies(self) -> None:
        """Delegate to SystemHealthChecker."""
        self._health.check_core_dependencies()

    def _check_git_status(self) -> None:
        """Delegate to SystemHealthChecker."""
        self._health.check_git_status()

    def _get_system_status_dict(self) -> dict[str, Any]:
        """Delegate to SystemHealthChecker."""
        return self._health.get_system_status_dict()


if __name__ == "__main__":
    discovery = SystemDiscovery()
    discovery.run_full_discovery()

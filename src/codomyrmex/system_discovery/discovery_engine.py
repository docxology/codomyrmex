"""System Discovery Engine for Codomyrmex

This module provides comprehensive system discovery capabilities, scanning all
modules, methods, classes, and functions to create a complete map of the
Codomyrmex ecosystem capabilities.
"""
import ast
import datetime
import importlib
import inspect
import json
import logging
import subprocess
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import numpy as np

from codomyrmex.coding import execute_code
from codomyrmex.data_visualization import create_line_plot
from codomyrmex.logging_monitoring import get_logger
from codomyrmex.logging_monitoring.logger_config import get_logger, setup_logging

try:

    setup_logging()
    logger = get_logger(__name__)
except ImportError:

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)


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

        # Ensure src is in Python path
        if str(self.src_path) not in sys.path:
            pass
#             sys.path.insert(0, str(self.src_path))  # Removed sys.path manipulation

    def run_full_discovery(self) -> None:
        """Run complete system discovery, scanning all modules and printing results.

        Orchestrates the full discovery pipeline: scans the codomyrmex package
        for modules, then displays the discovery results and capability summary
        to stdout.
        """
        print("\n🔍 " + "=" * 60)
        print("   CODOMYRMEX SYSTEM DISCOVERY")
        print("=" * 60)

        print(f"\n📂 Project Root: {self.project_root}")
        print(f"📦 Source Path: {self.src_path}")
        print(f"🧪 Testing Path: {self.testing_path}")

        # Scan system
        self.scan_system()

        # Show discovery results
        self._display_discovery_results()

        # Show capability summary
        self._display_capability_summary()

    def scan_system(self) -> dict[str, Any]:
        """
        Programmatically scan the system and return the inventory.

        Returns:
            Dictionary containing system status and module inventory.
        """
        # Discover all modules
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
        """
        Export system inventory to a JSON file.

        Args:
            output_path: Path to save the JSON file.

        Returns:
            True if successful, False otherwise.
        """
        try:
            inventory = self.scan_system()

            # Simple recursive helper to handle non-serializable objects if any slip through
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

    def export_full_inventory(self) -> bool:
        """Export full inventory to default location (compatibility method)."""
        return self.export_inventory(self.project_root / "codomyrmex_inventory.json")

    def check_git_repositories(self) -> None:
        """Check status of git repositories."""
        self._check_git_status()

    def _discover_modules(self) -> None:
        """Find all Python modules under the codomyrmex package directory and analyze each one."""
        print(f"\n🔎 Scanning modules in {self.codomyrmex_path}...")

        if not self.codomyrmex_path.exists():
            logger.error(f"Codomyrmex path does not exist: {self.codomyrmex_path}")
            return

        # Find all Python modules
        for module_dir in self.codomyrmex_path.iterdir():
            if module_dir.is_dir() and not module_dir.name.startswith("."):
                if (module_dir / "__init__.py").exists():
                    module_name = module_dir.name
                    print(f"  📦 Discovering {module_name}...")

                    module_info = self._analyze_module(module_name, module_dir)
                    if module_info:
                        self.modules[module_name] = module_info

    def _analyze_module(
        self, module_name: str, module_path: Path
    ) -> ModuleInfo | None:
        """Analyze a single module directory, extracting metadata, dependencies, and capabilities."""
        try:
            # Try to import the module
            module_import_path = f"codomyrmex.{module_name}"

            try:
                module = importlib.import_module(module_import_path)
                is_importable = True
                logger.info(f"Successfully imported {module_import_path}")
            except Exception as e:
                logger.warning(f"Could not import {module_import_path}: {e}")
                module = None
                is_importable = False

            # Get module metadata
            description = self._get_module_description(module_path)
            version = self._get_module_version(module_path)
            dependencies = self._get_module_dependencies(module_path)

            # Check for tests and docs
            has_tests = self._has_tests(module_name)
            has_docs = self._has_docs(module_path)

            # Get last modified time
            last_modified = self._get_last_modified(module_path)

            # Discover capabilities
            capabilities = []
            if is_importable and module:
                capabilities = self._discover_module_capabilities(module, module_path)
            else:
                # Try static analysis if import fails
                capabilities = self._static_analysis_capabilities(module_path)

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

                capability = self._analyze_object(name, obj, module_path)
                if capability:
                    capabilities.append(capability)

        except Exception as e:
            logger.error(f"Error discovering capabilities for {module}: {e}")

        return capabilities

    def _static_analysis_capabilities(
        self, module_path: Path
    ) -> list[ModuleCapability]:
        """Discover capabilities via AST parsing of Python files when runtime import fails."""
        capabilities = []

        try:
            # Analyze Python files in the module directory
            for py_file in module_path.glob("**/*.py"):
                if py_file.name.startswith("test_"):
                    continue

                try:
                    with open(py_file, encoding="utf-8") as f:
                        content = f.read()

                    tree = ast.parse(content)

                    for node in ast.walk(tree):
                        if isinstance(node, ast.FunctionDef):
                            if not node.name.startswith("_"):
                                capability = ModuleCapability(
                                    name=node.name,
                                    module_path=str(module_path),
                                    type="function",
                                    signature=self._get_function_signature_from_ast(
                                        node
                                    ),
                                    docstring=ast.get_docstring(node) or "No docstring",
                                    file_path=str(py_file),
                                    line_number=node.lineno,
                                    is_public=not node.name.startswith("_"),
                                    dependencies=[],
                                )
                                capabilities.append(capability)

                        elif isinstance(node, ast.ClassDef):
                            if not node.name.startswith("_"):
                                capability = ModuleCapability(
                                    name=node.name,
                                    module_path=str(module_path),
                                    type="class",
                                    signature=f"class {node.name}",
                                    docstring=ast.get_docstring(node) or "No docstring",
                                    file_path=str(py_file),
                                    line_number=node.lineno,
                                    is_public=not node.name.startswith("_"),
                                    dependencies=[],
                                )
                                capabilities.append(capability)

                except Exception as e:
                    logger.warning(f"Could not analyze {py_file}: {e}")
                    continue

        except Exception as e:
            logger.error(f"Error in static analysis of {module_path}: {e}")

        return capabilities

    def _analyze_object(
        self, name: str, obj: Any, module_path: Path
    ) -> ModuleCapability | None:
        """Inspect a runtime object (function, class, method, or constant) and build a ModuleCapability."""
        try:
            obj_type = "unknown"
            signature = str(obj)
            docstring = "No docstring"
            file_path = str(module_path)
            line_number = 0

            if inspect.isfunction(obj):
                obj_type = "function"
                try:
                    signature = str(inspect.signature(obj))
                    docstring = inspect.getdoc(obj) or "No docstring"
                    source_file = inspect.getfile(obj)
                    file_path = source_file
                    line_number = inspect.getsourcelines(obj)[1]
                except Exception as e:
                    logger.debug(f"Could not get details for function {name}: {e}")

            elif inspect.isclass(obj):
                obj_type = "class"
                signature = f"class {name}"
                docstring = inspect.getdoc(obj) or "No docstring"
                try:
                    source_file = inspect.getfile(obj)
                    file_path = source_file
                    line_number = inspect.getsourcelines(obj)[1]
                except Exception as e:
                    logger.debug(f"Could not get details for class {name}: {e}")

            elif inspect.ismethod(obj):
                obj_type = "method"
                try:
                    signature = str(inspect.signature(obj))
                    docstring = inspect.getdoc(obj) or "No docstring"
                except Exception as e:
                    logger.debug(f"Could not get details for method {name}: {e}")

            elif isinstance(obj, (str, int, float, bool, list, dict)):
                obj_type = "constant"
                signature = f"{name} = {repr(obj)[:100]}"

            else:
                obj_type = "other"

            return ModuleCapability(
                name=name,
                module_path=str(module_path),
                type=obj_type,
                signature=signature,
                docstring=docstring[:500],  # Truncate very long docstrings
                file_path=file_path,
                line_number=line_number,
                is_public=not name.startswith("_"),
                dependencies=[],
            )

        except Exception as e:
            logger.debug(f"Error analyzing object {name}: {e}")
            return None

    def _get_function_signature_from_ast(self, node: ast.FunctionDef) -> str:
        """Reconstruct a human-readable function signature string from an AST FunctionDef node."""
        args = []

        # Regular arguments
        for arg in node.args.args:
            args.append(arg.arg)

        # Default arguments
        if node.args.defaults:
            num_defaults = len(node.args.defaults)
            for i, default in enumerate(node.args.defaults):
                arg_index = len(node.args.args) - num_defaults + i
                args[arg_index] = f"{args[arg_index]}={ast.unparse(default)}"

        # *args
        if node.args.vararg:
            args.append(f"*{node.args.vararg.arg}")

        # **kwargs
        if node.args.kwarg:
            args.append(f"**{node.args.kwarg.arg}")

        return f"{node.name}({', '.join(args)})"

    def _get_module_description(self, module_path: Path) -> str:
        """Extract a short description from the module's README.md or __init__.py docstring."""
        # Try README first
        readme_path = module_path / "README.md"
        if readme_path.exists():
            try:
                with open(readme_path, encoding="utf-8") as f:
                    lines = f.readlines()
                    for line in lines:
                        if line.strip() and not line.startswith("#"):
                            return line.strip()
            except Exception as e:
                logger.debug(f"Could not read README for {module_path}: {e}")

        # Try __init__.py docstring
        init_path = module_path / "__init__.py"
        if init_path.exists():
            try:
                with open(init_path, encoding="utf-8") as f:
                    tree = ast.parse(f.read())
                    docstring = ast.get_docstring(tree)
                    if docstring:
                        return docstring
            except Exception as e:
                logger.debug(f"Could not get docstring from {init_path}: {e}")

        return "No description available"

    def _get_module_version(self, module_path: Path) -> str:
        """Detect the module version by parsing __version__ from __init__.py via AST."""
        # Try __init__.py
        init_path = module_path / "__init__.py"
        if init_path.exists():
            try:
                with open(init_path, encoding="utf-8") as f:
                    content = f.read()
                    if "__version__" in content:
                        tree = ast.parse(content)
                        for node in ast.walk(tree):
                            if isinstance(node, ast.Assign):
                                for target in node.targets:
                                    if (
                                        isinstance(target, ast.Name)
                                        and target.id == "__version__"
                                    ):
                                        if isinstance(node.value, ast.Constant):
                                            return node.value.value
            except Exception as e:
                logger.debug(f"Could not get version from {init_path}: {e}")

        return "unknown"

    def _get_module_dependencies(self, module_path: Path) -> list[str]:
        """Scan the module's requirements.txt for dependency package names."""
        dependencies = []

        # Check for module-specific requirements.txt
        req_path = module_path / "requirements.txt"
        if req_path.exists():
            try:
                with open(req_path, encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#"):
                            # Extract package name (before == or >= etc)
                            pkg_name = (
                                line.split("==")[0]
                                .split(">=")[0]
                                .split("<=")[0]
                                .split("~=")[0]
                            )
                            dependencies.append(pkg_name.strip())
            except Exception as e:
                logger.debug(f"Could not read requirements from {req_path}: {e}")

        return dependencies

    def _has_tests(self, module_name: str) -> bool:
        """Check whether a corresponding unit test file exists in the testing directory."""
        test_file = self.testing_path / "unit" / f"test_{module_name}.py"
        return test_file.exists()

    def _has_docs(self, module_path: Path) -> bool:
        """Check whether the module has documentation (README, docs dir, or API spec)."""
        doc_indicators = [
            module_path / "README.md",
            module_path / "docs",
            module_path / "API_SPECIFICATION.md",
            module_path / "USAGE_EXAMPLES.md",
        ]
        return any(path.exists() for path in doc_indicators)

    def _get_last_modified(self, module_path: Path) -> str:
        """Return the most recent modification timestamp across all Python files in the module."""
        try:
            latest_time = 0
            for py_file in module_path.glob("**/*.py"):
                mtime = py_file.stat().st_mtime
                if mtime > latest_time:
                    latest_time = mtime

            if latest_time > 0:

                return datetime.datetime.fromtimestamp(latest_time).strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
        except Exception as e:
            logger.debug(f"Could not get last modified time for {module_path}: {e}")

        return "unknown"

    def _display_discovery_results(self) -> None:
        """Print a formatted summary of all discovered modules with status icons to stdout."""
        print("\n📊 Discovery Results:")
        print(f"   Found {len(self.modules)} modules")

        importable_count = sum(1 for m in self.modules.values() if m.is_importable)
        tested_count = sum(1 for m in self.modules.values() if m.has_tests)
        documented_count = sum(1 for m in self.modules.values() if m.has_docs)

        print(f"   ✅ {importable_count} importable")
        print(f"   🧪 {tested_count} have tests")
        print(f"   📚 {documented_count} have documentation")

        print("\n📦 Module Summary:")
        for name, info in self.modules.items():
            status_icons = []
            if info.is_importable:
                status_icons.append("✅")
            else:
                status_icons.append("❌")

            if info.has_tests:
                status_icons.append("🧪")
            if info.has_docs:
                status_icons.append("📚")

            capability_count = len(info.capabilities)

            print(
                f"   {''.join(status_icons)} {name:<25} "
                f"({capability_count:2d} capabilities) - {info.description[:150]}"
            )

    def _display_capability_summary(self) -> None:
        """Print an aggregated breakdown of all capabilities grouped by type (function, class, etc.)."""
        print("\n🔧 Capability Summary:")

        all_capabilities = []
        for module_info in self.modules.values():
            all_capabilities.extend(module_info.capabilities)

        # Group by type
        by_type = {}
        for cap in all_capabilities:
            if cap.type not in by_type:
                by_type[cap.type] = []
            by_type[cap.type].append(cap)

        for cap_type, caps in by_type.items():
            print(f"   {cap_type:<12}: {len(caps)} items")

        print(f"\n🎯 Total Capabilities Discovered: {len(all_capabilities)}")

    def show_status_dashboard(self) -> None:
        """Display a comprehensive system status dashboard to stdout.

        Reports Python environment details, project structure health,
        core dependency availability, and git repository status.
        """
        print("\n📊 " + "=" * 60)
        print("   CODOMYRMEX STATUS DASHBOARD")
        print("=" * 60)

        # Python environment
        print("\n🐍 Python Environment:")
        print(f"   Version: {sys.version.split()[0]}")
        print(f"   Executable: {sys.executable}")
        print(
            f"   Virtual Environment: {'Yes' if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix) else 'No'}"
        )

        # Project structure
        print("\n📂 Project Structure:")
        print(f"   Root: {self.project_root}")
        print(f"   Source exists: {'✅' if self.src_path.exists() else '❌'}")
        print(f"   Tests exist: {'✅' if self.testing_path.exists() else '❌'}")
        print(
            f"   Virtual env: {'✅' if (self.project_root / '.venv').exists() or (self.project_root / 'venv').exists() else '❌'}"
        )

        # Dependencies
        self._check_core_dependencies()

        # Git status
        self._check_git_status()

    def _check_core_dependencies(self) -> None:
        """Attempt to import each core dependency and print pass/fail status."""
        print("\n📦 Core Dependencies:")

        # Map package names to their actual import names
        dep_mapping = {
            "python-dotenv": "dotenv",
            "cased-kit": "kit",
            "openai": "openai",
            "anthropic": "anthropic",
            "matplotlib": "matplotlib",
            "numpy": "numpy",
            "pytest": "pytest",
            "fastapi": "fastapi",
        }

        core_deps = list(dep_mapping.keys())

        for dep in core_deps:
            try:
                import_name = dep_mapping[dep]
                importlib.import_module(import_name)
                print(f"   ✅ {dep}")
            except ImportError:
                print(f"   ❌ {dep}")

    def _check_git_status(self) -> None:
        """Run git commands to report repo initialization, current branch, and uncommitted changes."""
        print("\n🌐 Git Repository:")

        try:
            # Check if we're in a git repo
            result = subprocess.run(
                ["git", "status"], capture_output=True, text=True, cwd=self.project_root
            )
            if result.returncode == 0:
                print("   ✅ Git repository initialized")

                # Get current branch
                branch_result = subprocess.run(
                    ["git", "branch", "--show-current"],
                    capture_output=True,
                    text=True,
                    cwd=self.project_root,
                )
                if branch_result.returncode == 0:
                    branch = branch_result.stdout.strip()
                    print(f"   🌿 Current branch: {branch}")

                # Check for uncommitted changes
                status_result = subprocess.run(
                    ["git", "status", "--porcelain"],
                    capture_output=True,
                    text=True,
                    cwd=self.project_root,
                )
                if status_result.returncode == 0:
                    changes = status_result.stdout.strip()
                    if changes:
                        change_count = len(changes.split("\n"))
                        print(f"   ⚠️  {change_count} uncommitted changes")
                    else:
                        print("   ✅ Working tree clean")
            else:
                print("   ❌ Not a git repository")

        except FileNotFoundError:
            print("   ❌ Git not found")
        except Exception as e:
            print(f"   ❌ Git error: {e}")

    def run_demo_workflows(self) -> None:
        """Execute demonstration workflows for available modules to validate system functionality.

        Runs sample operations (data visualization, logging, code execution) using
        discovered modules and reports success/failure for each demo.
        """
        print("\n🚀 " + "=" * 60)
        print("   CODOMYRMEX DEMO WORKFLOWS")
        print("=" * 60)

        successful_demos = 0

        # Data visualization demo
        if (
            "data_visualization" in self.modules
            and self.modules["data_visualization"].is_importable
        ):
            print("\n📊 Testing Data Visualization...")
            try:


                x = np.linspace(0, 4 * np.pi, 100)
                y = np.sin(x)

                create_line_plot(
                    x_data=x,
                    y_data=y,
                    title="Demo: Sine Wave",
                    x_label="X",
                    y_label="sin(x)",
                    output_path="demo_plot.png",
                    show_plot=False,
                )
                print("   ✅ Created demo plot: demo_plot.png")
                successful_demos += 1
            except Exception as e:
                print(f"   ❌ Data visualization demo failed: {e}")

        # Logging demo
        if (
            "logging_monitoring" in self.modules
            and self.modules["logging_monitoring"].is_importable
        ):
            print("\n📋 Testing Logging System...")
            try:

                demo_logger = get_logger("demo")
                demo_logger.info("Demo logging message - system working!")
                print("   ✅ Logging system functional")
                successful_demos += 1
            except Exception as e:
                print(f"   ❌ Logging demo failed: {e}")

        # Code execution demo
        if (
            "code" in self.modules
            and self.modules["code"].is_importable
        ):
            print("\n🏃 Testing Code Execution...")
            try:

                result = execute_code(
                    language="python", code="print('Hello from Codomyrmex sandbox!')"
                )
                if result.get("exit_code") == 0:
                    print(
                        f"   ✅ Code execution successful: {result.get('stdout', '').strip()}"
                    )
                    successful_demos += 1
                else:
                    print("   ⚠️  Code execution returned non-zero exit code")
            except Exception as e:
                print(f"   ❌ Code execution demo failed: {e}")

        print(f"\n🎯 Demo Summary: {successful_demos} workflows completed successfully")

    def export_full_inventory(self) -> None:
        """Export complete system inventory to JSON file."""
        print("\n📋 Generating Complete System Inventory...")

        # Run discovery if not done yet
        if not self.modules:
            self._discover_modules()

        # Create comprehensive inventory
        inventory = {
            "project_info": {
                "name": "Codomyrmex",
                "version": "0.1.0",
                "root_path": str(self.project_root),
                "python_version": sys.version,
                "timestamp": __import__("datetime").datetime.now().isoformat(),
            },
            "modules": {},
            "system_status": self._get_system_status_dict(),
        }

        # Add module details
        for name, info in self.modules.items():
            inventory["modules"][name] = asdict(info)

        # Save to file
        output_file = self.project_root / "codomyrmex_inventory.json"
        try:
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(inventory, f, indent=2, default=str)

            print(f"   ✅ Inventory exported to: {output_file}")
            print(f"   📊 {len(self.modules)} modules documented")

            total_capabilities = sum(
                len(info.capabilities) for info in self.modules.values()
            )
            print(f"   🔧 {total_capabilities} capabilities cataloged")

        except Exception as e:
            print(f"   ❌ Failed to export inventory: {e}")

    def _get_system_status_dict(self) -> dict[str, Any]:
        """Get system status as a dictionary."""
        status = {
            "python": {
                "version": sys.version.split()[0],
                "executable": sys.executable,
                "virtual_env": hasattr(sys, "real_prefix")
                or (hasattr(sys, "base_prefix") and sys.base_prefix != sys.prefix),
            },
            "project": {
                "src_exists": self.src_path.exists(),
                "tests_exist": self.testing_path.exists(),
                "venv_exists": (self.project_root / ".venv").exists()
                or (self.project_root / "venv").exists(),
            },
            "dependencies": {},
            "git": {},
        }

        # Check dependencies
        dep_mapping = {
            "python-dotenv": "dotenv",
            "cased-kit": "kit",
            "openai": "openai",
            "anthropic": "anthropic",
            "matplotlib": "matplotlib",
            "numpy": "numpy",
            "pytest": "pytest",
        }

        for dep, import_name in dep_mapping.items():
            try:
                importlib.import_module(import_name)
                status["dependencies"][dep] = True
            except ImportError:
                status["dependencies"][dep] = False

        # Check git status
        try:
            result = subprocess.run(
                ["git", "status"], capture_output=True, text=True, cwd=self.project_root
            )
            status["git"]["is_repo"] = result.returncode == 0

            if status["git"]["is_repo"]:
                # Get branch
                branch_result = subprocess.run(
                    ["git", "branch", "--show-current"],
                    capture_output=True,
                    text=True,
                    cwd=self.project_root,
                )
                if branch_result.returncode == 0:
                    status["git"]["branch"] = branch_result.stdout.strip()

                # Check for changes
                status_result = subprocess.run(
                    ["git", "status", "--porcelain"],
                    capture_output=True,
                    text=True,
                    cwd=self.project_root,
                )
                if status_result.returncode == 0:
                    status["git"]["clean"] = not status_result.stdout.strip()

        except Exception:
            status["git"]["is_repo"] = False

        return status

    def check_git_repositories(self) -> None:
        """Check git repository status and related repos."""
        print("\n🌐 " + "=" * 60)
        print("   GIT REPOSITORY STATUS")
        print("=" * 60)

        # Main repository
        print("\n📂 Main Repository:")
        self._check_git_status()

        # Check for submodules or related repositories
        print("\n📦 Dependencies & Related Repositories:")

        # Look for any git submodules
        gitmodules_path = self.project_root / ".gitmodules"
        if gitmodules_path.exists():
            print("   📁 Git submodules found:")
            try:
                with open(gitmodules_path) as f:
                    content = f.read()
                    print(f"      {content}")
            except Exception as e:
                print(f"   ❌ Could not read .gitmodules: {e}")
        else:
            print("   ℹ️  No git submodules detected")

        # Check remote repositories
        try:
            result = subprocess.run(
                ["git", "remote", "-v"],
                capture_output=True,
                text=True,
                cwd=self.project_root,
            )
            if result.returncode == 0 and result.stdout.strip():
                print("\n🌍 Remote Repositories:")
                for line in result.stdout.strip().split("\n"):
                    print(f"   {line}")
            else:
                print("\n   ℹ️  No remote repositories configured")

        except Exception as e:
            print(f"\n   ❌ Could not check remotes: {e}")


if __name__ == "__main__":
    # Allow running this module directly for testing
    discovery = SystemDiscovery()
    discovery.run_full_discovery()

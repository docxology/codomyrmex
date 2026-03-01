"""Dependency and module metadata analysis for Codomyrmex system discovery.

Provides utilities for analyzing module dependencies, versions, descriptions,
documentation presence, and capabilities via both runtime inspection and
static AST analysis.
"""

import ast
import datetime
import inspect
import logging
from pathlib import Path
from typing import Any

try:
    from codomyrmex.logging_monitoring.core.logger_config import get_logger

    logger = get_logger(__name__)
except ImportError:
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)


class DependencyAnalyzer:
    """Analyzes module metadata, dependencies, and capabilities.

    Extracts information about modules including their descriptions,
    versions, dependencies, test coverage, documentation, and
    capabilities (via both runtime inspection and AST-based static analysis).
    """

    def __init__(self, project_root: Path, testing_path: Path):
        """Initialize the dependency analyzer.

        Args:
            project_root: Filesystem path to the project root directory.
            testing_path: Filesystem path to the testing directory.
        """
        self.project_root = project_root
        self.testing_path = testing_path

    def get_module_description(self, module_path: Path) -> str:
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

    def get_module_version(self, module_path: Path) -> str:
        """Detect the module version by parsing __version__ from __init__.py via AST."""
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

    def get_module_dependencies(self, module_path: Path) -> list[str]:
        """Scan the module's requirements.txt for dependency package names."""
        dependencies = []

        req_path = module_path / "requirements.txt"
        if req_path.exists():
            try:
                with open(req_path, encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#"):
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

    def has_tests(self, module_name: str) -> bool:
        """Check whether a corresponding unit test file exists in the testing directory."""
        test_file = self.testing_path / "unit" / f"test_{module_name}.py"
        return test_file.exists()

    def has_docs(self, module_path: Path) -> bool:
        """Check whether the module has documentation (README, docs dir, or API spec)."""
        doc_indicators = [
            module_path / "README.md",
            module_path / "docs",
            module_path / "API_SPECIFICATION.md",
            module_path / "USAGE_EXAMPLES.md",
        ]
        return any(path.exists() for path in doc_indicators)

    def get_last_modified(self, module_path: Path) -> str:
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

    def static_analysis_capabilities(self, module_path: Path) -> list:
        """Discover capabilities via AST parsing of Python files when runtime import fails.

        Returns a list of ModuleCapability dataclass instances (imported at call time
        to avoid circular imports).
        """
        from .discovery_engine import ModuleCapability

        capabilities = []

        try:
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
                                    signature=self.get_function_signature_from_ast(node),
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

    def get_function_signature_from_ast(self, node: ast.FunctionDef) -> str:
        """Reconstruct a human-readable function signature string from an AST FunctionDef node."""
        args = []

        for arg in node.args.args:
            args.append(arg.arg)

        if node.args.defaults:
            num_defaults = len(node.args.defaults)
            for i, default in enumerate(node.args.defaults):
                arg_index = len(node.args.args) - num_defaults + i
                args[arg_index] = f"{args[arg_index]}={ast.unparse(default)}"

        if node.args.vararg:
            args.append(f"*{node.args.vararg.arg}")

        if node.args.kwarg:
            args.append(f"**{node.args.kwarg.arg}")

        return f"{node.name}({', '.join(args)})"

    def analyze_object(self, name: str, obj: Any, module_path: Path):
        """Inspect a runtime object and build a ModuleCapability.

        Returns a ModuleCapability dataclass instance or None.
        """
        from .discovery_engine import ModuleCapability

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
                docstring=docstring[:500],
                file_path=file_path,
                line_number=line_number,
                is_public=not name.startswith("_"),
                dependencies=[],
            )

        except Exception as e:
            logger.debug(f"Error analyzing object {name}: {e}")
            return None

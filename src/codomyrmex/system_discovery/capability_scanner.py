#!/usr/bin/env python3
"""
Capability Scanner for Codomyrmex System Discovery

Scans and analyzes capabilities across the Codomyrmex ecosystem, providing
detailed information about functions, classes, methods, and other exportable
functionality.
"""

import ast
import inspect
import importlib
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional, Set, Tuple, Union
from dataclasses import dataclass
import json
from codomyrmex.exceptions import CodomyrmexError

try:
    from codomyrmex.logging_monitoring.logger_config import get_logger

    logger = get_logger(__name__)
except ImportError:
    import logging

    logger = logging.getLogger(__name__)


@dataclass
class FunctionCapability:
    """Detailed information about a function capability."""

    name: str
    signature: str
    docstring: str
    parameters: List[Dict[str, Any]]
    return_annotation: str
    file_path: str
    line_number: int
    is_async: bool
    is_generator: bool
    decorators: List[str]
    complexity_score: int


@dataclass
class ClassCapability:
    """Detailed information about a class capability."""

    name: str
    docstring: str
    methods: List[FunctionCapability]
    properties: List[str]
    class_variables: List[str]
    inheritance: List[str]
    file_path: str
    line_number: int
    is_abstract: bool
    decorators: List[str]


@dataclass
class ModuleCapability:
    """Detailed information about a module's capabilities."""

    name: str
    path: str
    docstring: str
    functions: List[FunctionCapability]
    classes: List[ClassCapability]
    constants: Dict[str, Any]
    imports: List[str]
    exports: List[str]
    file_count: int
    line_count: int
    last_modified: str


class CapabilityScanner:
    """
    Advanced capability scanner for the Codomyrmex ecosystem.

    Provides deep analysis of code capabilities including functions, classes,
    methods, and their relationships.
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize the capability scanner."""
        self.project_root = project_root or Path.cwd()
        self.src_path = self.project_root / "src"
        self.codomyrmex_path = self.src_path / "codomyrmex"

        # Ensure src is in Python path
        if str(self.src_path) not in sys.path:
            pass
#             sys.path.insert(0, str(self.src_path))  # Removed sys.path manipulation

    def scan_all_modules(self) -> Dict[str, ModuleCapability]:
        """Scan all modules and return detailed capability information."""
        capabilities = {}

        if not self.codomyrmex_path.exists():
            logger.error(f"Codomyrmex path does not exist: {self.codomyrmex_path}")
            return capabilities

        # Find all modules
        for module_dir in self.codomyrmex_path.iterdir():
            if module_dir.is_dir() and not module_dir.name.startswith("."):
                if (module_dir / "__init__.py").exists():
                    module_name = module_dir.name
                    logger.info(f"Scanning capabilities for {module_name}...")

                    try:
                        module_capability = self.scan_module(module_name, module_dir)
                        if module_capability:
                            capabilities[module_name] = module_capability
                    except Exception as e:
                        logger.error(f"Error scanning {module_name}: {e}")

        return capabilities

    def scan_module(
        self, module_name: str, module_path: Path
    ) -> Optional[ModuleCapability]:
        """Scan a specific module for capabilities."""
        try:
            # Try to import the module for runtime analysis
            module_import_path = f"codomyrmex.{module_name}"
            try:
                module = importlib.import_module(module_import_path)
                use_runtime_analysis = True
            except Exception as e:
                logger.warning(f"Could not import {module_import_path}: {e}")
                module = None
                use_runtime_analysis = False

            # Static analysis of all Python files in the module
            functions = []
            classes = []
            constants = {}
            imports = set()
            exports = []
            total_lines = 0
            file_count = 0

            for py_file in module_path.rglob("*.py"):
                if py_file.name.startswith("test_"):
                    continue

                try:
                    with open(py_file, "r", encoding="utf-8") as f:
                        content = f.read()

                    # Count lines
                    lines = len(content.split("\n"))
                    total_lines += lines
                    file_count += 1

                    # Parse AST
                    tree = ast.parse(content, filename=str(py_file))

                    # Extract capabilities from AST
                    file_functions, file_classes, file_constants, file_imports = (
                        self._analyze_ast(tree, py_file)
                    )

                    functions.extend(file_functions)
                    classes.extend(file_classes)
                    constants.update(file_constants)
                    imports.update(file_imports)

                except Exception as e:
                    logger.warning(f"Could not analyze {py_file}: {e}")
                    continue

            # Get module docstring and exports
            module_docstring = self._get_module_docstring(module_path)

            if use_runtime_analysis and module:
                # Get exports from __all__ if available
                if hasattr(module, "__all__"):
                    exports = list(module.__all__)
                else:
                    # Get public attributes
                    exports = [
                        name
                        for name, obj in inspect.getmembers(module)
                        if not name.startswith("_")
                    ]

            # Get last modified time
            last_modified = self._get_last_modified_time(module_path)

            return ModuleCapability(
                name=module_name,
                path=str(module_path),
                docstring=module_docstring,
                functions=functions,
                classes=classes,
                constants=constants,
                imports=list(imports),
                exports=exports,
                file_count=file_count,
                line_count=total_lines,
                last_modified=last_modified,
            )

        except Exception as e:
            logger.error(f"Error scanning module {module_name}: {e}")
            return None

    def _analyze_ast(
        self, tree: ast.AST, file_path: Path
    ) -> Tuple[
        List[FunctionCapability], List[ClassCapability], Dict[str, Any], Set[str]
    ]:
        """Analyze AST and extract capabilities."""
        functions = []
        classes = []
        constants = {}
        imports = set()

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                if not node.name.startswith("_"):
                    func = self._analyze_function(node, file_path)
                    if func:
                        functions.append(func)

            elif isinstance(node, ast.AsyncFunctionDef):
                if not node.name.startswith("_"):
                    func = self._analyze_function(node, file_path, is_async=True)
                    if func:
                        functions.append(func)

            elif isinstance(node, ast.ClassDef):
                if not node.name.startswith("_"):
                    cls = self._analyze_class(node, file_path)
                    if cls:
                        classes.append(cls)

            elif isinstance(node, ast.Assign):
                # Look for module-level constants
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id.isupper():
                        try:
                            if isinstance(node.value, ast.Constant):
                                constants[target.id] = node.value.value
                            elif isinstance(node.value, ast.Str):  # Python < 3.8
                                constants[target.id] = node.value.s
                            elif isinstance(node.value, ast.Num):  # Python < 3.8
                                constants[target.id] = node.value.n
                        except Exception:
                            constants[target.id] = "complex_value"

            elif isinstance(node, (ast.Import, ast.ImportFrom)):
                try:
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            imports.add(alias.name)
                    elif isinstance(node, ast.ImportFrom) and node.module:
                        imports.add(node.module)
                except Exception:
                    pass

        return functions, classes, constants, imports

    def _analyze_function(
        self,
        node: Union[ast.FunctionDef, ast.AsyncFunctionDef],
        file_path: Path,
        is_async: bool = False,
    ) -> Optional[FunctionCapability]:
        """Analyze a function node and extract detailed information."""
        try:
            # Get basic information
            name = node.name
            docstring = ast.get_docstring(node) or "No docstring"
            line_number = node.lineno

            # Analyze parameters
            parameters = []
            for arg in node.args.args:
                param_info = {
                    "name": arg.arg,
                    "annotation": (
                        ast.unparse(arg.annotation) if arg.annotation else None
                    ),
                    "default": None,
                }
                parameters.append(param_info)

            # Add defaults
            if node.args.defaults:
                num_defaults = len(node.args.defaults)
                for i, default in enumerate(node.args.defaults):
                    param_index = len(parameters) - num_defaults + i
                    if param_index >= 0:
                        try:
                            parameters[param_index]["default"] = ast.unparse(default)
                        except Exception:
                            parameters[param_index]["default"] = "complex_default"

            # Handle *args and **kwargs
            if node.args.vararg:
                parameters.append(
                    {
                        "name": f"*{node.args.vararg.arg}",
                        "annotation": (
                            ast.unparse(node.args.vararg.annotation)
                            if node.args.vararg.annotation
                            else None
                        ),
                        "default": None,
                    }
                )

            if node.args.kwarg:
                parameters.append(
                    {
                        "name": f"**{node.args.kwarg.arg}",
                        "annotation": (
                            ast.unparse(node.args.kwarg.annotation)
                            if node.args.kwarg.annotation
                            else None
                        ),
                        "default": None,
                    }
                )

            # Get return annotation
            return_annotation = ""
            if node.returns:
                try:
                    return_annotation = ast.unparse(node.returns)
                except Exception:
                    return_annotation = "complex_annotation"

            # Build signature
            param_strs = []
            for param in parameters:
                param_str = param["name"]
                if param["annotation"]:
                    param_str += f": {param['annotation']}"
                if param["default"]:
                    param_str += f" = {param['default']}"
                param_strs.append(param_str)

            signature = f"{name}({', '.join(param_strs)})"
            if return_annotation:
                signature += f" -> {return_annotation}"

            # Check for decorators
            decorators = []
            for decorator in node.decorator_list:
                try:
                    decorators.append(ast.unparse(decorator))
                except Exception:
                    decorators.append("complex_decorator")

            # Calculate complexity (simple heuristic)
            complexity_score = self._calculate_complexity(node)

            # Check if it's a generator
            is_generator = any(
                isinstance(n, ast.Yield) or isinstance(n, ast.YieldFrom)
                for n in ast.walk(node)
            )

            return FunctionCapability(
                name=name,
                signature=signature,
                docstring=docstring[:500],  # Limit docstring length
                parameters=parameters,
                return_annotation=return_annotation,
                file_path=str(file_path),
                line_number=line_number,
                is_async=is_async or isinstance(node, ast.AsyncFunctionDef),
                is_generator=is_generator,
                decorators=decorators,
                complexity_score=complexity_score,
            )

        except Exception as e:
            logger.debug(
                f"Error analyzing function {getattr(node, 'name', 'unknown')}: {e}"
            )
            return None

    def _analyze_class(
        self, node: ast.ClassDef, file_path: Path
    ) -> Optional[ClassCapability]:
        """Analyze a class node and extract detailed information."""
        try:
            name = node.name
            docstring = ast.get_docstring(node) or "No docstring"
            line_number = node.lineno

            # Analyze methods
            methods = []
            properties = []
            class_variables = []

            for item in node.body:
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    method = self._analyze_function(item, file_path)
                    if method:
                        # Check if it's a property
                        is_property = any(
                            isinstance(dec, ast.Name) and dec.id == "property"
                            for dec in item.decorator_list
                        )

                        if is_property:
                            properties.append(method.name)
                        else:
                            methods.append(method)

                elif isinstance(item, ast.Assign):
                    # Look for class variables
                    for target in item.targets:
                        if isinstance(target, ast.Name):
                            class_variables.append(target.id)

            # Get inheritance information
            inheritance = []
            for base in node.bases:
                try:
                    inheritance.append(ast.unparse(base))
                except Exception:
                    inheritance.append("complex_base")

            # Check for decorators
            decorators = []
            for decorator in node.decorator_list:
                try:
                    decorators.append(ast.unparse(decorator))
                except Exception:
                    decorators.append("complex_decorator")

            # Check if abstract
            is_abstract = any(
                "abc" in dec.lower() or "abstract" in dec.lower() for dec in decorators
            )

            return ClassCapability(
                name=name,
                docstring=docstring[:500],  # Limit docstring length
                methods=methods,
                properties=properties,
                class_variables=class_variables,
                inheritance=inheritance,
                file_path=str(file_path),
                line_number=line_number,
                is_abstract=is_abstract,
                decorators=decorators,
            )

        except Exception as e:
            logger.debug(
                f"Error analyzing class {getattr(node, 'name', 'unknown')}: {e}"
            )
            return None

    def _calculate_complexity(self, node: ast.AST) -> int:
        """Calculate a simple complexity score for a function."""
        complexity = 1  # Base complexity

        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.For, ast.While, ast.With)):
                complexity += 1
            elif isinstance(child, ast.ExceptHandler):
                complexity += 1
            elif isinstance(
                child, (ast.ListComp, ast.DictComp, ast.SetComp, ast.GeneratorExp)
            ):
                complexity += 1

        return complexity

    def _get_module_docstring(self, module_path: Path) -> str:
        """Get module docstring from __init__.py."""
        init_path = module_path / "__init__.py"
        if init_path.exists():
            try:
                with open(init_path, "r", encoding="utf-8") as f:
                    tree = ast.parse(f.read())
                    docstring = ast.get_docstring(tree)
                    return docstring or "No docstring"
            except Exception as e:
                logger.debug(f"Could not get docstring from {init_path}: {e}")

        return "No docstring"

    def _get_last_modified_time(self, module_path: Path) -> str:
        """Get the last modified time of the module."""
        try:
            latest_time = 0
            for py_file in module_path.rglob("*.py"):
                mtime = py_file.stat().st_mtime
                if mtime > latest_time:
                    latest_time = mtime

            if latest_time > 0:
                import datetime

                return datetime.datetime.fromtimestamp(latest_time).strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
        except Exception as e:
            logger.debug(f"Could not get last modified time for {module_path}: {e}")

        return "unknown"

    def analyze_capability_relationships(
        self, capabilities: Dict[str, ModuleCapability]
    ) -> Dict[str, Any]:
        """Analyze relationships between capabilities."""
        relationships = {
            "function_calls": {},  # Which functions call which
            "class_inheritance": {},  # Class inheritance relationships
            "import_dependencies": {},  # Import relationships
            "shared_functions": [],  # Functions with same names across modules
            "complexity_analysis": {},  # Complexity statistics
        }

        # Analyze function calls (simplified - would need more sophisticated analysis)
        all_function_names = set()
        for module_cap in capabilities.values():
            for func in module_cap.functions:
                all_function_names.add(func.name)

        # Find shared function names
        function_counts = {}
        for module_name, module_cap in capabilities.items():
            for func in module_cap.functions:
                if func.name not in function_counts:
                    function_counts[func.name] = []
                function_counts[func.name].append(module_name)

        relationships["shared_functions"] = [
            {"name": name, "modules": modules}
            for name, modules in function_counts.items()
            if len(modules) > 1
        ]

        # Analyze complexity
        all_complexities = []
        for module_cap in capabilities.values():
            for func in module_cap.functions:
                all_complexities.append(func.complexity_score)

        if all_complexities:
            relationships["complexity_analysis"] = {
                "average": sum(all_complexities) / len(all_complexities),
                "max": max(all_complexities),
                "min": min(all_complexities),
                "high_complexity_functions": [
                    {
                        "module": module_name,
                        "function": func.name,
                        "complexity": func.complexity_score,
                    }
                    for module_name, module_cap in capabilities.items()
                    for func in module_cap.functions
                    if func.complexity_score > 10
                ],
            }

        return relationships

    def export_capabilities_report(
        self, capabilities: Dict[str, ModuleCapability], filename: Optional[str] = None
    ) -> str:
        """Export detailed capabilities report to JSON."""
        if filename is None:
            import datetime

            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"codomyrmex_capabilities_{timestamp}.json"

        output_path = self.project_root / filename

        # Convert to serializable format
        serializable_data = {}
        for module_name, module_cap in capabilities.items():
            serializable_data[module_name] = {
                "name": module_cap.name,
                "path": module_cap.path,
                "docstring": module_cap.docstring,
                "file_count": module_cap.file_count,
                "line_count": module_cap.line_count,
                "last_modified": module_cap.last_modified,
                "constants": module_cap.constants,
                "imports": module_cap.imports,
                "exports": module_cap.exports,
                "functions": [
                    {
                        "name": func.name,
                        "signature": func.signature,
                        "docstring": func.docstring,
                        "parameters": func.parameters,
                        "return_annotation": func.return_annotation,
                        "file_path": func.file_path,
                        "line_number": func.line_number,
                        "is_async": func.is_async,
                        "is_generator": func.is_generator,
                        "decorators": func.decorators,
                        "complexity_score": func.complexity_score,
                    }
                    for func in module_cap.functions
                ],
                "classes": [
                    {
                        "name": cls.name,
                        "docstring": cls.docstring,
                        "properties": cls.properties,
                        "class_variables": cls.class_variables,
                        "inheritance": cls.inheritance,
                        "file_path": cls.file_path,
                        "line_number": cls.line_number,
                        "is_abstract": cls.is_abstract,
                        "decorators": cls.decorators,
                        "methods": [
                            {
                                "name": method.name,
                                "signature": method.signature,
                                "docstring": method.docstring,
                                "parameters": method.parameters,
                                "complexity_score": method.complexity_score,
                            }
                            for method in cls.methods
                        ],
                    }
                    for cls in module_cap.classes
                ],
            }

        try:
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(serializable_data, f, indent=2, ensure_ascii=False)

            logger.info(f"Capabilities report exported to: {output_path}")
            return str(output_path)

        except Exception as e:
            logger.error(f"Failed to export capabilities report: {e}")
            return ""


if __name__ == "__main__":
    # Demo the capability scanner
    scanner = CapabilityScanner()
    capabilities = scanner.scan_all_modules()

    print(f"Scanned {len(capabilities)} modules")
    for module_name, module_cap in capabilities.items():
        print(
            f"  {module_name}: {len(module_cap.functions)} functions, {len(module_cap.classes)} classes"
        )

    if capabilities:
        relationships = scanner.analyze_capability_relationships(capabilities)
        print(f"Found {len(relationships['shared_functions'])} shared function names")

        if relationships["complexity_analysis"]:
            avg_complexity = relationships["complexity_analysis"]["average"]
            print(f"Average complexity: {avg_complexity:.2f}")

        # Export report
        report_path = scanner.export_capabilities_report(capabilities)
        if report_path:
            print(f"Report exported to: {report_path}")

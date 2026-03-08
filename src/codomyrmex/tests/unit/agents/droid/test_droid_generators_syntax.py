"""Tests verifying that droid generator functions produce syntactically valid Python.

Each generator in agents/droid/generators/documentation.py returns a Python
source string (a code template).  These tests use ast.parse() to confirm the
output is valid Python and importlib.util.find_spec() to confirm that import
paths referenced inside the generated code resolve against the installed package.
"""

import ast
import importlib.util
import importlib.util as _importlib_util
import re
from pathlib import Path as _Path

import pytest

# Import the generators module directly to avoid the droid __init__.py chain,
# which pulls in controller.py → codomyrmex.performance → psutil (optional dep).
_GENERATORS_PATH = (
    _Path(__file__).parent.parent.parent.parent.parent
    / "agents"
    / "droid"
    / "generators"
    / "documentation.py"
)
_spec = _importlib_util.spec_from_file_location(
    "codomyrmex.agents.droid.generators.documentation", _GENERATORS_PATH
)
_mod = _importlib_util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)

generate_quality_tests = _mod.generate_quality_tests
generate_documentation_quality_module = _mod.generate_documentation_quality_module
generate_consistency_checker_module = _mod.generate_consistency_checker_module


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _extract_import_module_names(source: str) -> list[str]:
    """Return top-level module names from 'import X' and 'from X import ...' lines."""
    tree = ast.parse(source)
    names: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                names.append(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom) and node.module:
            names.append(node.module.split(".")[0])
    return names


def _extract_codomyrmex_import_paths(source: str) -> list[str]:
    """Return full module paths of 'from codomyrmex.X import ...' statements."""
    tree = ast.parse(source)
    paths: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module:
            if node.module.startswith("codomyrmex"):
                paths.append(node.module)
    return paths


# ---------------------------------------------------------------------------
# generate_quality_tests
# ---------------------------------------------------------------------------

class TestGenerateQualityTests:
    """Tests for generate_quality_tests() generator."""

    def test_returns_string(self):
        result = generate_quality_tests()
        assert isinstance(result, str)
        assert len(result) > 0

    def test_output_is_valid_python(self):
        source = generate_quality_tests()
        # ast.parse raises SyntaxError on invalid syntax
        tree = ast.parse(source)
        assert tree is not None

    def test_codomyrmex_import_paths_resolve(self):
        source = generate_quality_tests()
        for module_path in _extract_codomyrmex_import_paths(source):
            spec = importlib.util.find_spec(module_path)
            assert spec is not None, (
                f"Generated code references import path '{module_path}' "
                f"but importlib.util.find_spec() returned None — module does not exist."
            )

    def test_contains_test_class(self):
        source = generate_quality_tests()
        tree = ast.parse(source)
        class_names = [
            node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)
        ]
        assert any("Test" in name for name in class_names), (
            "Generated test module should contain at least one class whose name starts with 'Test'"
        )

    def test_contains_test_functions(self):
        source = generate_quality_tests()
        tree = ast.parse(source)
        func_names = [
            node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)
        ]
        assert any(name.startswith("test_") for name in func_names), (
            "Generated test module should contain at least one function starting with 'test_'"
        )


# ---------------------------------------------------------------------------
# generate_documentation_quality_module
# ---------------------------------------------------------------------------

class TestGenerateDocumentationQualityModule:
    """Tests for generate_documentation_quality_module() generator."""

    def test_returns_string(self):
        result = generate_documentation_quality_module()
        assert isinstance(result, str)
        assert len(result) > 0

    def test_output_is_valid_python(self):
        source = generate_documentation_quality_module()
        tree = ast.parse(source)
        assert tree is not None

    def test_codomyrmex_import_paths_resolve(self):
        source = generate_documentation_quality_module()
        for module_path in _extract_codomyrmex_import_paths(source):
            spec = importlib.util.find_spec(module_path)
            assert spec is not None, (
                f"Generated code references import path '{module_path}' "
                f"but importlib.util.find_spec() returned None."
            )

    def test_contains_quality_analyzer_class(self):
        source = generate_documentation_quality_module()
        tree = ast.parse(source)
        class_names = [
            node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)
        ]
        assert "DocumentationQualityAnalyzer" in class_names

    def test_analyzer_has_analyze_file_method(self):
        source = generate_documentation_quality_module()
        tree = ast.parse(source)
        # Find the class node and check its methods
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name == "DocumentationQualityAnalyzer":
                method_names = [
                    n.name for n in ast.walk(node) if isinstance(n, ast.FunctionDef)
                ]
                assert "analyze_file" in method_names
                return
        pytest.fail("DocumentationQualityAnalyzer class not found in generated source")

    def test_no_deprecated_typing_imports_in_output(self):
        """Generated module should use built-in generics, not typing.Dict/List/Optional."""
        source = generate_documentation_quality_module()
        # Check that the deprecated typing imports are not present
        deprecated_pattern = re.compile(
            r"from\s+typing\s+import\s+[^\n]*\b(Dict|List|Optional|Tuple)\b"
        )
        match = deprecated_pattern.search(source)
        assert match is None, (
            f"Generated code contains deprecated typing import: {match.group(0)!r}. "
            f"Use built-in generics (dict, list, X | None, tuple) instead."
        )


# ---------------------------------------------------------------------------
# generate_consistency_checker_module
# ---------------------------------------------------------------------------

class TestGenerateConsistencyCheckerModule:
    """Tests for generate_consistency_checker_module() generator."""

    def test_returns_string(self):
        result = generate_consistency_checker_module()
        assert isinstance(result, str)
        assert len(result) > 0

    def test_output_is_valid_python(self):
        source = generate_consistency_checker_module()
        tree = ast.parse(source)
        assert tree is not None

    def test_codomyrmex_import_paths_resolve(self):
        source = generate_consistency_checker_module()
        for module_path in _extract_codomyrmex_import_paths(source):
            spec = importlib.util.find_spec(module_path)
            assert spec is not None, (
                f"Generated code references import path '{module_path}' "
                f"but importlib.util.find_spec() returned None."
            )

    def test_contains_consistency_checker_class(self):
        source = generate_consistency_checker_module()
        tree = ast.parse(source)
        class_names = [
            node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)
        ]
        assert "DocumentationConsistencyChecker" in class_names

    def test_checker_has_check_project_consistency_method(self):
        source = generate_consistency_checker_module()
        tree = ast.parse(source)
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name == "DocumentationConsistencyChecker":
                method_names = [
                    n.name for n in ast.walk(node) if isinstance(n, ast.FunctionDef)
                ]
                assert "check_project_consistency" in method_names
                return
        pytest.fail("DocumentationConsistencyChecker class not found in generated source")

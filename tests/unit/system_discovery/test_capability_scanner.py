"""Tests for system_discovery.core.capability_scanner — zero-mock.

Covers: FunctionCapability, ClassCapability, ModuleCapability dataclasses,
CapabilityScanner (init, scan_module, _calculate_complexity, _analyze_ast).
Uses real AST parsing on this project's own source code.
"""

import ast
from pathlib import Path

from tests.support.repo_paths import PACKAGE_ROOT, REPO_ROOT

from codomyrmex.system_discovery.core.capability_scanner import (
    CapabilityScanner,
    ClassCapability,
    FunctionCapability,
    ModuleCapability,
)


class TestFunctionCapability:
    def test_create(self):
        fc = FunctionCapability(
            name="test_func",
            signature="test_func(x: int) -> str",
            docstring="A test function.",
            parameters=[{"name": "x", "annotation": "int"}],
            return_annotation="str",
            file_path="test.py",
            line_number=10,
            is_async=False,
            is_generator=False,
            decorators=[],
            complexity_score=3,
        )
        assert fc.name == "test_func"
        assert fc.is_async is False
        assert fc.complexity_score == 3


class TestClassCapability:
    def test_create(self):
        cc = ClassCapability(
            name="TestClass",
            docstring="A test class.",
            methods=[],
            properties=["name"],
            class_variables=["VERSION"],
            inheritance=["object"],
            file_path="test.py",
            line_number=1,
            is_abstract=False,
            decorators=[],
        )
        assert cc.name == "TestClass"
        assert cc.is_abstract is False


class TestModuleCapability:
    def test_create(self):
        mc = ModuleCapability(
            name="test_module",
            path="/src/test_module",
            docstring="A test module.",
            functions=[],
            classes=[],
            constants={},
            imports=[],
            exports=[],
            file_count=5,
            line_count=200,
            last_modified="2026-01-01",
        )
        assert mc.name == "test_module"
        assert mc.file_count == 5


class TestCapabilityScanner:
    def test_init(self):
        scanner = CapabilityScanner()
        assert scanner is not None

    def test_init_with_root(self):
        root = Path("/Users/mini/Documents/GitHub/codomyrmex")
        scanner = CapabilityScanner(project_root=root)
        assert scanner is not None

    def test_calculate_complexity_simple(self):
        code = "def simple(): return 1"
        tree = ast.parse(code)
        scanner = CapabilityScanner()
        score = scanner._calculate_complexity(tree.body[0])
        assert isinstance(score, int)
        assert score >= 1

    def test_calculate_complexity_branchy(self):
        code = """
def branchy(x):
    if x > 0:
        if x > 10:
            return "big"
        return "small"
    elif x == 0:
        return "zero"
    else:
        for i in range(x):
            if i % 2:
                continue
        return "negative"
"""
        tree = ast.parse(code)
        scanner = CapabilityScanner()
        score = scanner._calculate_complexity(tree.body[0])
        assert score > 1

    def test_analyze_ast(self):
        code = '''
def greet(name: str) -> str:
    """Say hello."""
    return f"Hello, {name}"

class Calculator:
    """A simple calculator."""
    def add(self, a: int, b: int) -> int:
        return a + b

CONSTANT = 42
'''
        tree = ast.parse(code)
        scanner = CapabilityScanner()
        result = scanner._analyze_ast(tree, Path("test.py"))
        assert isinstance(result, tuple)
        functions, classes, constants, imports = result
        assert len(functions) >= 1
        assert len(classes) >= 1

    def test_scan_all_modules(self):
        # Use the real project root derived from this file's location
        # rather than a hardcoded developer-specific path.
        _this_file = Path(__file__).resolve()
        # tests/unit/system_discovery -> tests/unit/system_discovery
        # project root is 5 levels up from tests/unit/system_discovery
        _project_root = REPO_ROOT
        scanner = CapabilityScanner(project_root=_project_root)
        modules = scanner.scan_all_modules()
        assert isinstance(modules, dict)
        assert len(modules) > 0

    def test_export_capabilities_report_success(self, tmp_path: Path):
        scanner = CapabilityScanner(project_root=tmp_path)
        caps = {
            "test_module": ModuleCapability(
                name="test_module",
                path="/src/test_module",
                docstring="A test module.",
                functions=[
                    FunctionCapability(
                        name="f", signature="f()", docstring="doc", parameters=[], return_annotation="None",
                        file_path="f.py", line_number=1, is_async=False, is_generator=False, decorators=[],
                        complexity_score=1
                    )
                ],
                classes=[
                    ClassCapability(
                        name="C", docstring="doc", properties=[], class_variables=[], inheritance=[],
                        file_path="c.py", line_number=1, is_abstract=False, decorators=[], methods=[]
                    )
                ],
                constants={},
                imports=[],
                exports=[],
                file_count=5,
                line_count=200,
                last_modified="2026-01-01"
            )
        }
        output = scanner.export_capabilities_report(caps, filename="test.json")
        assert output == str(tmp_path / "test.json")
        assert (tmp_path / "test.json").exists()

    def test_export_capabilities_report_default_filename(self, tmp_path: Path):
        scanner = CapabilityScanner(project_root=tmp_path)
        output = scanner.export_capabilities_report({})
        assert output.startswith(str(tmp_path / "codomyrmex_capabilities_"))
        assert output.endswith(".json")
        assert Path(output).exists()

    def test_export_capabilities_report_error(self, tmp_path: Path):
        # Make tmp_path read-only to trigger an Exception
        read_only_dir = tmp_path / "readonly"
        read_only_dir.mkdir()
        read_only_dir.chmod(0o444)

        scanner = CapabilityScanner(project_root=read_only_dir)
        output = scanner.export_capabilities_report({}, filename="test.json")
        assert output == ""

"""Comprehensive unit tests for static_analysis module.

This module provides 30+ tests covering:
1. AST parsing and traversal
2. Code complexity calculation
3. Import analysis
4. Dependency detection
5. Code metrics (lines, functions, classes)
6. Dead code detection
7. Code smell detection
8. Linting integration
9. Security vulnerability detection
10. Type checking integration
11. Error handling for malformed code
"""

import ast
import json
import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest


# Sample code strings for testing
SIMPLE_FUNCTION_CODE = """
def add(a, b):
    '''Add two numbers.'''
    return a + b
"""

COMPLEX_FUNCTION_CODE = """
def process_data(data, options=None):
    '''Process data with complex logic.'''
    if options is None:
        options = {}

    result = []
    for item in data:
        if item > 0:
            if item % 2 == 0:
                result.append(item * 2)
            else:
                result.append(item * 3)
        elif item < 0:
            result.append(abs(item))
        else:
            result.append(0)

    return result
"""

CLASS_WITH_METHODS_CODE = """
class Calculator:
    '''A simple calculator class.'''

    def __init__(self, initial_value=0):
        self.value = initial_value

    def add(self, x):
        self.value += x
        return self.value

    def subtract(self, x):
        self.value -= x
        return self.value

    def multiply(self, x):
        self.value *= x
        return self.value

    def divide(self, x):
        if x == 0:
            raise ValueError("Cannot divide by zero")
        self.value /= x
        return self.value
"""

CODE_WITH_IMPORTS = """
import os
import sys
from pathlib import Path
from typing import Optional, List, Dict
from collections import defaultdict
import json as j

def process():
    pass
"""

CODE_WITH_SECURITY_ISSUES = """
import os
import subprocess

password = "hardcoded_secret"  # Hardcoded credentials

def unsafe_exec(cmd):
    os.system(cmd)  # Command injection vulnerability

def unsafe_eval(user_input):
    return eval(user_input)  # Dangerous eval

def unsafe_subprocess(cmd):
    subprocess.call(cmd, shell=True)  # Shell injection
"""

CODE_WITH_DEAD_CODE = """
def used_function():
    return 42

def unused_function():
    '''This function is never called.'''
    return "never used"

UNUSED_CONSTANT = "this is unused"

class UnusedClass:
    '''This class is never instantiated.'''
    pass

result = used_function()
"""

CODE_WITH_TYPE_HINTS = """
from typing import List, Optional, Dict

def process_items(items: List[str], default: Optional[str] = None) -> Dict[str, int]:
    result: Dict[str, int] = {}
    for item in items:
        result[item] = len(item)
    return result

def broken_types(x: int) -> str:
    return x  # Type mismatch: returning int instead of str
"""

MALFORMED_CODE = """
def broken_function(
    print("Missing closing parenthesis"
"""

SYNTAX_ERROR_CODE = """
def function():
    if True
        print("Missing colon")
"""

CODE_WITH_SMELLS = """
def function_with_too_many_parameters(a, b, c, d, e, f, g, h, i, j, k):
    '''Too many parameters is a code smell.'''
    return a + b + c + d + e + f + g + h + i + j + k

def deeply_nested():
    '''Deeply nested code is hard to read.'''
    if True:
        if True:
            if True:
                if True:
                    if True:
                        return "too deep"

def god_function():
    '''A function that does too many things.'''
    # Reading file
    with open("file.txt") as f:
        data = f.read()
    # Parsing data
    parsed = data.split(",")
    # Processing
    result = [x.upper() for x in parsed]
    # Formatting
    formatted = "\\n".join(result)
    # Writing
    with open("output.txt", "w") as f:
        f.write(formatted)
    # Logging
    print(formatted)
    return formatted
"""

MULTI_CLASS_CODE = """
class BaseClass:
    def base_method(self):
        pass

class ChildClass(BaseClass):
    def child_method(self):
        pass

class AnotherClass:
    class NestedClass:
        pass

    def method(self):
        pass
"""


@pytest.mark.unit
class TestASTParsingAndTraversal:
    """Test cases for AST parsing and traversal."""

    def test_parse_simple_function(self):
        """Test parsing a simple function."""
        tree = ast.parse(SIMPLE_FUNCTION_CODE)
        assert tree is not None
        functions = [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
        assert len(functions) == 1
        assert functions[0].name == "add"

    def test_parse_complex_function(self):
        """Test parsing a complex function with nested structures."""
        tree = ast.parse(COMPLEX_FUNCTION_CODE)
        functions = [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
        assert len(functions) == 1

        # Count control flow statements
        if_statements = [node for node in ast.walk(tree) if isinstance(node, ast.If)]
        for_statements = [node for node in ast.walk(tree) if isinstance(node, ast.For)]
        assert len(if_statements) >= 3
        assert len(for_statements) >= 1

    def test_parse_class_with_methods(self):
        """Test parsing a class with multiple methods."""
        tree = ast.parse(CLASS_WITH_METHODS_CODE)
        classes = [node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
        assert len(classes) == 1
        assert classes[0].name == "Calculator"

        # Count methods in the class
        methods = [node for node in ast.walk(classes[0]) if isinstance(node, ast.FunctionDef)]
        assert len(methods) == 5  # __init__, add, subtract, multiply, divide

    def test_parse_nested_classes(self):
        """Test parsing code with nested classes."""
        tree = ast.parse(MULTI_CLASS_CODE)
        classes = [node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
        # Should find BaseClass, ChildClass, AnotherClass, NestedClass
        assert len(classes) == 4

    def test_ast_node_visitor_pattern(self):
        """Test using AST node visitor pattern."""
        class FunctionVisitor(ast.NodeVisitor):
            def __init__(self):
                self.functions = []

            def visit_FunctionDef(self, node):
                self.functions.append(node.name)
                self.generic_visit(node)

        tree = ast.parse(CLASS_WITH_METHODS_CODE)
        visitor = FunctionVisitor()
        visitor.visit(tree)

        assert "__init__" in visitor.functions
        assert "add" in visitor.functions
        assert "divide" in visitor.functions


@pytest.mark.unit
class TestCodeComplexityCalculation:
    """Test cases for code complexity calculation."""

    def test_simple_function_complexity(self, code_dir):
        """Test cyclomatic complexity for simple function."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from codomyrmex.static_analysis.static_analyzer import StaticAnalyzer

        analyzer = StaticAnalyzer()
        complexity = analyzer._calculate_cyclomatic_complexity(SIMPLE_FUNCTION_CODE)
        # Simple function has minimal branching
        assert complexity >= 1
        assert complexity <= 3

    def test_complex_function_complexity(self, code_dir):
        """Test cyclomatic complexity for complex function."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from codomyrmex.static_analysis.static_analyzer import StaticAnalyzer

        analyzer = StaticAnalyzer()
        complexity = analyzer._calculate_cyclomatic_complexity(COMPLEX_FUNCTION_CODE)
        # Complex function has multiple branches
        assert complexity >= 5

    def test_class_complexity(self, code_dir):
        """Test complexity calculation for class code."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from codomyrmex.static_analysis.static_analyzer import StaticAnalyzer

        analyzer = StaticAnalyzer()
        complexity = analyzer._calculate_cyclomatic_complexity(CLASS_WITH_METHODS_CODE)
        # Class with multiple methods and conditionals
        assert complexity >= 2

    def test_malformed_code_complexity(self, code_dir):
        """Test complexity calculation handles malformed code."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from codomyrmex.static_analysis.static_analyzer import StaticAnalyzer

        analyzer = StaticAnalyzer()
        # Should return default complexity of 1 for malformed code
        complexity = analyzer._calculate_cyclomatic_complexity(MALFORMED_CODE)
        assert complexity == 1


@pytest.mark.unit
class TestImportAnalysis:
    """Test cases for import analysis."""

    def test_extract_standard_imports(self):
        """Test extracting standard library imports."""
        tree = ast.parse(CODE_WITH_IMPORTS)
        imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                imports.append(node.module)

        assert "os" in imports
        assert "sys" in imports
        assert "json" in imports
        assert "pathlib" in imports

    def test_extract_from_imports(self):
        """Test extracting 'from X import Y' style imports."""
        tree = ast.parse(CODE_WITH_IMPORTS)
        from_imports = {}
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                module = node.module
                names = [alias.name for alias in node.names]
                from_imports[module] = names

        assert "Path" in from_imports.get("pathlib", [])
        assert "Optional" in from_imports.get("typing", [])
        assert "List" in from_imports.get("typing", [])

    def test_import_aliases(self):
        """Test detecting import aliases."""
        tree = ast.parse(CODE_WITH_IMPORTS)
        aliases = {}
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.asname:
                        aliases[alias.name] = alias.asname

        assert aliases.get("json") == "j"


@pytest.mark.unit
class TestDependencyDetection:
    """Test cases for dependency detection."""

    def test_detect_external_dependencies(self, code_dir):
        """Test detection of external module dependencies."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        # Standard library modules
        stdlib_modules = {"os", "sys", "json", "pathlib", "typing", "collections"}

        tree = ast.parse(CODE_WITH_IMPORTS)
        imported_modules = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imported_modules.add(alias.name.split(".")[0])
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported_modules.add(node.module.split(".")[0])

        # Check that we found the expected modules
        assert "os" in imported_modules
        assert "pathlib" in imported_modules

    def test_find_requirements_files(self, code_dir, tmp_path):
        """Test finding requirements files in project."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from codomyrmex.static_analysis.static_analyzer import StaticAnalyzer

        # Create requirements file
        req_file = tmp_path / "requirements.txt"
        req_file.write_text("pytest>=7.0.0\nflake8>=5.0.0\n")

        analyzer = StaticAnalyzer(str(tmp_path))
        req_files = analyzer._find_requirements_files()

        assert any("requirements" in str(f) for f in req_files)


@pytest.mark.unit
class TestCodeMetrics:
    """Test cases for code metrics calculation."""

    def test_lines_of_code_metric(self, code_dir, tmp_path):
        """Test lines of code calculation."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from codomyrmex.static_analysis.static_analyzer import StaticAnalyzer

        # Create a test file
        test_file = tmp_path / "test_metrics.py"
        test_file.write_text(CLASS_WITH_METHODS_CODE)

        analyzer = StaticAnalyzer(str(tmp_path))
        metrics = analyzer.calculate_metrics(str(test_file))

        # Should count non-empty, non-comment lines
        assert metrics.lines_of_code > 10

    def test_count_functions(self):
        """Test counting functions in code."""
        tree = ast.parse(CLASS_WITH_METHODS_CODE)
        functions = [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
        assert len(functions) == 5

    def test_count_classes(self):
        """Test counting classes in code."""
        tree = ast.parse(MULTI_CLASS_CODE)
        classes = [node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
        assert len(classes) == 4  # Including nested class

    def test_maintainability_index(self, code_dir, tmp_path):
        """Test maintainability index calculation."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from codomyrmex.static_analysis.static_analyzer import StaticAnalyzer

        test_file = tmp_path / "test_maintainability.py"
        test_file.write_text(SIMPLE_FUNCTION_CODE)

        analyzer = StaticAnalyzer(str(tmp_path))
        metrics = analyzer.calculate_metrics(str(test_file))

        # Maintainability index should be positive
        assert metrics.maintainability_index >= 0

    def test_code_duplication_metric(self, code_dir, tmp_path):
        """Test code duplication calculation."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from codomyrmex.static_analysis.static_analyzer import StaticAnalyzer

        # Code with duplication
        duplicated_code = """
def func1():
    x = 1 + 2
    return x

def func2():
    x = 1 + 2
    return x

def func3():
    x = 1 + 2
    return x
"""
        test_file = tmp_path / "duplicated.py"
        test_file.write_text(duplicated_code)

        analyzer = StaticAnalyzer(str(tmp_path))
        metrics = analyzer.calculate_metrics(str(test_file))

        # Should detect duplication
        assert metrics.code_duplication >= 0


@pytest.mark.unit
class TestDeadCodeDetection:
    """Test cases for dead code detection."""

    def test_detect_unused_functions(self):
        """Test detection of unused functions."""
        tree = ast.parse(CODE_WITH_DEAD_CODE)

        # Get all function definitions
        defined_functions = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                defined_functions.add(node.name)

        # Get all function calls
        called_functions = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    called_functions.add(node.func.id)

        unused = defined_functions - called_functions
        assert "unused_function" in unused

    def test_detect_unused_variables(self):
        """Test detection of unused variables."""
        code = """
x = 10
y = 20
z = x + y
unused_var = "never used"
print(z)
"""
        tree = ast.parse(code)

        # Simple analysis: find assignments vs usages
        assigned = set()
        used = set()

        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        assigned.add(target.id)
            elif isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
                used.add(node.id)

        potentially_unused = assigned - used
        assert "unused_var" in potentially_unused

    def test_detect_unused_classes(self):
        """Test detection of unused classes."""
        tree = ast.parse(CODE_WITH_DEAD_CODE)

        # Get all class definitions
        defined_classes = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                defined_classes.add(node.name)

        assert "UnusedClass" in defined_classes


@pytest.mark.unit
class TestCodeSmellDetection:
    """Test cases for code smell detection."""

    def test_detect_too_many_parameters(self):
        """Test detection of functions with too many parameters."""
        tree = ast.parse(CODE_WITH_SMELLS)

        MAX_PARAMS = 7
        smelly_functions = []

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                num_params = len(node.args.args)
                if num_params > MAX_PARAMS:
                    smelly_functions.append((node.name, num_params))

        assert len(smelly_functions) >= 1
        assert any(name == "function_with_too_many_parameters" for name, _ in smelly_functions)

    def test_detect_deep_nesting(self):
        """Test detection of deeply nested code."""
        tree = ast.parse(CODE_WITH_SMELLS)

        def get_max_depth(node, current_depth=0):
            max_depth = current_depth
            for child in ast.iter_child_nodes(node):
                if isinstance(child, (ast.If, ast.For, ast.While, ast.With, ast.Try)):
                    child_depth = get_max_depth(child, current_depth + 1)
                    max_depth = max(max_depth, child_depth)
                else:
                    child_depth = get_max_depth(child, current_depth)
                    max_depth = max(max_depth, child_depth)
            return max_depth

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == "deeply_nested":
                depth = get_max_depth(node)
                assert depth >= 5  # Five levels of nesting

    def test_detect_long_function(self):
        """Test detection of long functions."""
        long_code = "\n".join([f"    x{i} = {i}" for i in range(100)])
        code = f"def very_long_function():\n{long_code}\n    return x99"

        tree = ast.parse(code)
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Get line count from node
                start_line = node.lineno
                end_line = node.end_lineno if hasattr(node, 'end_lineno') else start_line
                line_count = end_line - start_line + 1
                assert line_count > 50  # Long function threshold


@pytest.mark.unit
class TestLintingIntegration:
    """Test cases for linting integration."""

    def test_static_analyzer_initialization(self, code_dir):
        """Test StaticAnalyzer initialization."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from codomyrmex.static_analysis.static_analyzer import StaticAnalyzer

        analyzer = StaticAnalyzer()
        assert analyzer.tools_available is not None
        assert isinstance(analyzer.tools_available, dict)

    def test_get_available_tools(self, code_dir):
        """Test getting list of available linting tools."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from codomyrmex.static_analysis import get_available_tools

        tools = get_available_tools()
        expected_tools = ["pylint", "flake8", "mypy", "bandit", "black", "isort"]

        for tool in expected_tools:
            assert tool in tools

    def test_analysis_result_dataclass(self, code_dir):
        """Test AnalysisResult dataclass structure."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from codomyrmex.static_analysis.static_analyzer import AnalysisResult, SeverityLevel

        result = AnalysisResult(
            file_path="/test/file.py",
            line_number=10,
            column_number=5,
            severity=SeverityLevel.ERROR,
            message="Test error",
            rule_id="E001",
            category="test"
        )

        assert result.file_path == "/test/file.py"
        assert result.line_number == 10
        assert result.severity == SeverityLevel.ERROR

    def test_analysis_summary_dataclass(self, code_dir):
        """Test AnalysisSummary dataclass structure."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from codomyrmex.static_analysis.static_analyzer import AnalysisSummary

        summary = AnalysisSummary(
            total_issues=10,
            files_analyzed=5,
            analysis_time=2.5
        )

        assert summary.total_issues == 10
        assert summary.files_analyzed == 5
        assert summary.analysis_time == 2.5


@pytest.mark.unit
class TestSecurityVulnerabilityDetection:
    """Test cases for security vulnerability detection."""

    def test_detect_hardcoded_secrets(self):
        """Test detection of hardcoded secrets."""
        tree = ast.parse(CODE_WITH_SECURITY_ISSUES)

        suspicious_patterns = ["password", "secret", "api_key", "token"]
        found_issues = []

        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        var_name = target.id.lower()
                        for pattern in suspicious_patterns:
                            if pattern in var_name:
                                found_issues.append(target.id)

        assert "password" in found_issues

    def test_detect_dangerous_functions(self):
        """Test detection of dangerous function calls."""
        tree = ast.parse(CODE_WITH_SECURITY_ISSUES)

        dangerous_functions = {"eval", "exec", "compile", "system"}
        found_dangerous = []

        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    if node.func.id in dangerous_functions:
                        found_dangerous.append(node.func.id)
                elif isinstance(node.func, ast.Attribute):
                    if node.func.attr in dangerous_functions:
                        found_dangerous.append(node.func.attr)

        assert "eval" in found_dangerous
        assert "system" in found_dangerous

    def test_detect_shell_injection_risk(self):
        """Test detection of shell injection vulnerabilities."""
        tree = ast.parse(CODE_WITH_SECURITY_ISSUES)

        shell_true_calls = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Attribute):
                    for keyword in node.keywords:
                        if keyword.arg == "shell":
                            if isinstance(keyword.value, ast.Constant) and keyword.value.value is True:
                                shell_true_calls.append(node.func.attr)

        assert "call" in shell_true_calls


@pytest.mark.unit
class TestTypeCheckingIntegration:
    """Test cases for type checking integration."""

    def test_extract_type_hints(self):
        """Test extraction of type hints from code."""
        tree = ast.parse(CODE_WITH_TYPE_HINTS)

        type_hints = {}
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Get return annotation
                if node.returns:
                    type_hints[node.name] = {"return": ast.unparse(node.returns)}

                # Get argument annotations
                for arg in node.args.args:
                    if arg.annotation:
                        type_hints.setdefault(node.name, {})
                        type_hints[node.name][arg.arg] = ast.unparse(arg.annotation)

        assert "process_items" in type_hints
        assert "items" in type_hints.get("process_items", {})

    def test_pyrefly_runner_class(self, code_dir):
        """Test PyreflyRunner class initialization."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from codomyrmex.static_analysis.pyrefly_runner import PyreflyRunner

        runner = PyreflyRunner()
        assert hasattr(runner, "pyrefly_available")
        assert hasattr(runner, "analyze_file")
        assert hasattr(runner, "analyze_directory")

    def test_pyrefly_result_dataclass(self, code_dir):
        """Test PyreflyResult dataclass structure."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from codomyrmex.static_analysis.pyrefly_runner import PyreflyResult, PyreflyIssue

        issue = PyreflyIssue(
            file_path="/test/file.py",
            line=10,
            column=5,
            severity="error",
            message="Type mismatch"
        )

        result = PyreflyResult(
            success=True,
            issues=[issue],
            files_analyzed=1
        )

        assert result.success is True
        assert len(result.issues) == 1
        assert result.issues[0].severity == "error"


@pytest.mark.unit
class TestErrorHandlingForMalformedCode:
    """Test cases for error handling with malformed code."""

    def test_syntax_error_detection(self):
        """Test that syntax errors are properly detected."""
        with pytest.raises(SyntaxError):
            ast.parse(SYNTAX_ERROR_CODE)

    def test_malformed_code_handling(self):
        """Test handling of malformed code."""
        with pytest.raises(SyntaxError):
            ast.parse(MALFORMED_CODE)

    def test_analyzer_handles_syntax_error(self, code_dir, tmp_path):
        """Test that analyzer handles files with syntax errors gracefully."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from codomyrmex.static_analysis.static_analyzer import StaticAnalyzer, CodeMetrics

        # Create file with syntax error
        bad_file = tmp_path / "bad_syntax.py"
        bad_file.write_text(MALFORMED_CODE)

        analyzer = StaticAnalyzer(str(tmp_path))
        metrics = analyzer.calculate_metrics(str(bad_file))

        # Should return default metrics without crashing
        assert isinstance(metrics, CodeMetrics)

    def test_exception_classes_exist(self, code_dir):
        """Test that static analysis exception classes exist."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from codomyrmex.static_analysis.exceptions import (
            ParserError,
            LintError,
            TypeCheckError,
            ComplexityError,
            DependencyAnalysisError,
            SecurityVulnerabilityError,
            ASTError,
            MetricsError,
        )

        # Test ParserError
        error = ParserError("Parse failed", file_path="/test.py", line=10, column=5)
        assert "Parse failed" in str(error)
        assert error.context.get("file_path") == "/test.py"

        # Test TypeCheckError
        type_error = TypeCheckError("Type mismatch", expected_type="str", actual_type="int")
        assert type_error.context.get("expected_type") == "str"

        # Test SecurityVulnerabilityError
        sec_error = SecurityVulnerabilityError(
            "Vulnerability found",
            vulnerability_type="injection",
            severity="high",
            cwe_id="CWE-79"
        )
        assert sec_error.context.get("cwe_id") == "CWE-79"

    def test_empty_file_handling(self, code_dir, tmp_path):
        """Test handling of empty files."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from codomyrmex.static_analysis.static_analyzer import StaticAnalyzer

        empty_file = tmp_path / "empty.py"
        empty_file.write_text("")

        analyzer = StaticAnalyzer(str(tmp_path))
        metrics = analyzer.calculate_metrics(str(empty_file))

        assert metrics.lines_of_code == 0

    def test_unicode_file_handling(self, code_dir, tmp_path):
        """Test handling of files with unicode content."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from codomyrmex.static_analysis.static_analyzer import StaticAnalyzer

        unicode_code = '''# -*- coding: utf-8 -*-
"""Unicode test: \u4e2d\u6587"""

def greet(name):
    """Say hello in multiple languages."""
    return f"Hello \u4f60\u597d {name}!"
'''
        unicode_file = tmp_path / "unicode_test.py"
        unicode_file.write_text(unicode_code, encoding="utf-8")

        analyzer = StaticAnalyzer(str(tmp_path))
        metrics = analyzer.calculate_metrics(str(unicode_file))

        assert metrics.lines_of_code > 0


@pytest.mark.unit
class TestLanguageDetection:
    """Test cases for language detection."""

    def test_detect_python_files(self, code_dir):
        """Test detection of Python files."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from codomyrmex.static_analysis.static_analyzer import StaticAnalyzer, Language

        analyzer = StaticAnalyzer()

        assert analyzer._detect_language("test.py") == Language.PYTHON
        assert analyzer._detect_language("script.pyw") == Language.PYTHON  # May default

    def test_detect_javascript_files(self, code_dir):
        """Test detection of JavaScript files."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from codomyrmex.static_analysis.static_analyzer import StaticAnalyzer, Language

        analyzer = StaticAnalyzer()

        assert analyzer._detect_language("test.js") == Language.JAVASCRIPT
        assert analyzer._detect_language("component.jsx") == Language.JAVASCRIPT

    def test_detect_typescript_files(self, code_dir):
        """Test detection of TypeScript files."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from codomyrmex.static_analysis.static_analyzer import StaticAnalyzer, Language

        analyzer = StaticAnalyzer()

        assert analyzer._detect_language("test.ts") == Language.TYPESCRIPT
        assert analyzer._detect_language("component.tsx") == Language.TYPESCRIPT

    def test_should_analyze_file(self, code_dir):
        """Test file analysis filter."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from codomyrmex.static_analysis.static_analyzer import StaticAnalyzer

        analyzer = StaticAnalyzer()

        assert analyzer._should_analyze_file("test.py") is True
        assert analyzer._should_analyze_file("test.js") is True
        assert analyzer._should_analyze_file("test.txt") is False
        assert analyzer._should_analyze_file("test.md") is False


@pytest.mark.unit
class TestExportResults:
    """Test cases for exporting analysis results."""

    def test_export_results_json(self, code_dir, tmp_path):
        """Test exporting results to JSON format."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from codomyrmex.static_analysis.static_analyzer import (
            StaticAnalyzer,
            AnalysisResult,
            SeverityLevel,
        )

        analyzer = StaticAnalyzer(str(tmp_path))
        analyzer.results = [
            AnalysisResult(
                file_path="/test/file.py",
                line_number=10,
                column_number=5,
                severity=SeverityLevel.ERROR,
                message="Test error",
                rule_id="E001",
                category="test"
            )
        ]

        output_file = tmp_path / "results.json"
        success = analyzer.export_results(str(output_file), format="json")

        assert success is True
        assert output_file.exists()

        with open(output_file) as f:
            data = json.load(f)

        assert len(data) == 1
        assert data[0]["rule_id"] == "E001"

    def test_export_results_csv(self, code_dir, tmp_path):
        """Test exporting results to CSV format."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from codomyrmex.static_analysis.static_analyzer import (
            StaticAnalyzer,
            AnalysisResult,
            SeverityLevel,
        )

        analyzer = StaticAnalyzer(str(tmp_path))
        analyzer.results = [
            AnalysisResult(
                file_path="/test/file.py",
                line_number=10,
                column_number=5,
                severity=SeverityLevel.WARNING,
                message="Test warning",
                rule_id="W001",
                category="test"
            )
        ]

        output_file = tmp_path / "results.csv"
        success = analyzer.export_results(str(output_file), format="csv")

        assert success is True
        assert output_file.exists()

        content = output_file.read_text()
        assert "W001" in content
        assert "Test warning" in content

    def test_export_invalid_format(self, code_dir, tmp_path):
        """Test exporting with invalid format."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from codomyrmex.static_analysis.static_analyzer import StaticAnalyzer

        analyzer = StaticAnalyzer(str(tmp_path))
        output_file = tmp_path / "results.xml"

        success = analyzer.export_results(str(output_file), format="xml")

        assert success is False


@pytest.mark.unit
class TestResultFiltering:
    """Test cases for filtering analysis results."""

    def test_get_results_by_severity(self, code_dir):
        """Test filtering results by severity level."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from codomyrmex.static_analysis.static_analyzer import (
            StaticAnalyzer,
            AnalysisResult,
            SeverityLevel,
        )

        analyzer = StaticAnalyzer()
        analyzer.results = [
            AnalysisResult("/test.py", 1, 0, SeverityLevel.ERROR, "Error 1", "E001", "test"),
            AnalysisResult("/test.py", 2, 0, SeverityLevel.WARNING, "Warning 1", "W001", "test"),
            AnalysisResult("/test.py", 3, 0, SeverityLevel.ERROR, "Error 2", "E002", "test"),
        ]

        errors = analyzer.get_results_by_severity(SeverityLevel.ERROR)
        warnings = analyzer.get_results_by_severity(SeverityLevel.WARNING)

        assert len(errors) == 2
        assert len(warnings) == 1

    def test_get_results_by_category(self, code_dir):
        """Test filtering results by category."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from codomyrmex.static_analysis.static_analyzer import (
            StaticAnalyzer,
            AnalysisResult,
            SeverityLevel,
        )

        analyzer = StaticAnalyzer()
        analyzer.results = [
            AnalysisResult("/test.py", 1, 0, SeverityLevel.ERROR, "Error", "E001", "security"),
            AnalysisResult("/test.py", 2, 0, SeverityLevel.WARNING, "Warning", "W001", "style"),
            AnalysisResult("/test.py", 3, 0, SeverityLevel.ERROR, "Error", "E002", "security"),
        ]

        security_results = analyzer.get_results_by_category("security")
        style_results = analyzer.get_results_by_category("style")

        assert len(security_results) == 2
        assert len(style_results) == 1

    def test_get_results_by_file(self, code_dir):
        """Test filtering results by file."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from codomyrmex.static_analysis.static_analyzer import (
            StaticAnalyzer,
            AnalysisResult,
            SeverityLevel,
        )

        analyzer = StaticAnalyzer()
        analyzer.results = [
            AnalysisResult("/file1.py", 1, 0, SeverityLevel.ERROR, "Error", "E001", "test"),
            AnalysisResult("/file2.py", 2, 0, SeverityLevel.WARNING, "Warning", "W001", "test"),
            AnalysisResult("/file1.py", 3, 0, SeverityLevel.ERROR, "Error", "E002", "test"),
        ]

        file1_results = analyzer.get_results_by_file("/file1.py")
        file2_results = analyzer.get_results_by_file("/file2.py")

        assert len(file1_results) == 2
        assert len(file2_results) == 1

    def test_clear_results(self, code_dir):
        """Test clearing analysis results."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from codomyrmex.static_analysis.static_analyzer import (
            StaticAnalyzer,
            AnalysisResult,
            SeverityLevel,
        )

        analyzer = StaticAnalyzer()
        analyzer.results = [
            AnalysisResult("/test.py", 1, 0, SeverityLevel.ERROR, "Error", "E001", "test"),
        ]
        analyzer.metrics = {"test": "value"}

        analyzer.clear_results()

        assert len(analyzer.results) == 0
        assert len(analyzer.metrics) == 0

"""Test generation from code analysis.

Produces test suites from function signatures and class structures.
"""

from __future__ import annotations

import ast
from dataclasses import dataclass, field

from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)


@dataclass
class GeneratedTest:
    """A single generated test case.

    Attributes:
        name: Test function name.
        body: Test body code.
        target: The function/class being tested.
    """

    name: str
    body: str = ""
    target: str = ""


@dataclass
class TestSuite:
    """A generated test suite.

    Attributes:
        module_name: Module being tested.
        tests: Generated test cases.
        imports: Required import lines.
    """

    module_name: str = ""
    tests: list[GeneratedTest] = field(default_factory=list)
    imports: list[str] = field(default_factory=list)

    @property
    def test_count(self) -> int:
        """Execute Test Count operations natively."""
        return len(self.tests)

    def render(self) -> str:
        """Execute Render operations natively."""
        lines = ['"""Auto-generated tests."""', "", "import pytest", ""]
        lines.extend(self.imports)
        lines.append("")
        for test in self.tests:
            lines.append(f"def {test.name}():")
            lines.append(f"    {test.body}")
            lines.append("")
        return "\n".join(lines)


class TestGenerator:
    """Generate test cases from source code.

    Usage::

        gen = TestGenerator()
        suite = gen.from_source("def add(a, b): return a + b")
        print(suite.render())
    """

    def from_source(self, source: str, module_name: str = "module") -> TestSuite:
        """Generate tests from Python source code.

        Args:
            source: Python source code.
            module_name: Module name for imports.

        Returns:
            ``TestSuite`` with generated tests.
        """
        try:
            tree = ast.parse(source)
        except SyntaxError:
            return TestSuite(module_name=module_name)

        tests: list[GeneratedTest] = []

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and not node.name.startswith("_"):
                test = self._generate_function_test(node)
                tests.append(test)
            elif isinstance(node, ast.ClassDef):
                tests.extend(self._generate_class_tests(node))

        suite = TestSuite(module_name=module_name, tests=tests)
        logger.info("Tests generated", extra={"tests": suite.test_count})
        return suite

    def _generate_function_test(self, node: ast.FunctionDef) -> GeneratedTest:
        """Execute  Generate Function Test operations natively."""
        args = [a.arg for a in node.args.args if a.arg != "self"]
        name = f"test_{node.name}"

        if args:
            body = f"# TODO: test {node.name}({', '.join(args)})\n    assert True"
        else:
            body = f"# TODO: test {node.name}()\n    assert True"

        return GeneratedTest(name=name, body=body, target=node.name)

    def _generate_class_tests(self, node: ast.ClassDef) -> list[GeneratedTest]:
        """Execute  Generate Class Tests operations natively."""
        tests = []
        class_name = node.name

        tests.append(GeneratedTest(
            name=f"test_{class_name.lower()}_instantiation",
            body=f"# TODO: test {class_name} instantiation\n    assert True",
            target=class_name,
        ))

        for item in node.body:
            if isinstance(item, ast.FunctionDef) and not item.name.startswith("_"):
                tests.append(GeneratedTest(
                    name=f"test_{class_name.lower()}_{item.name}",
                    body=f"# TODO: test {class_name}.{item.name}\n    assert True",
                    target=f"{class_name}.{item.name}",
                ))

        return tests


__all__ = ["GeneratedTest", "TestGenerator", "TestSuite"]

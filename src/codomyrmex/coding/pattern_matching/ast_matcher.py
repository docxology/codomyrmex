"""Pattern matching on Python Abstract Syntax Trees.

Parses Python source code into an AST and searches for structural patterns
such as design patterns, anti-patterns, and user-defined templates.
"""

from __future__ import annotations

import ast
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class ASTMatchResult:
    """A single AST match result.

    Attributes:
        pattern_name: Name of the matched pattern or anti-pattern.
        node_type: The AST node type (e.g. ``"ClassDef"``, ``"FunctionDef"``).
        line: Source line number (1-based).
        col: Source column offset (0-based).
        name: Name of the matched element (class/function name), if applicable.
        details: Additional information about the match.
    """

    pattern_name: str
    node_type: str
    line: int
    col: int
    name: str = ""
    details: str = ""


class ASTMatcher:
    """Pattern matching on Abstract Syntax Trees.

    Currently supports Python source code via the built-in ``ast`` module.

    Usage::

        matcher = ASTMatcher()
        tree = matcher.parse_code("class Foo: pass")
        patterns = matcher.find_pattern(source_code, "singleton")
        anti = matcher.find_antipatterns(source_code)
    """

    SUPPORTED_LANGUAGES = ("python",)

    # Known anti-pattern detectors
    _ANTIPATTERN_CHECKS = (
        "_check_bare_except",
        "_check_mutable_default_arg",
        "_check_star_import",
        "_check_nested_function_depth",
    )

    def __init__(self) -> None:
        """Execute   Init   operations natively."""
        pass

    def parse_code(self, source: str, language: str = "python") -> dict:
        """Parse source code and return a simplified AST representation.

        Args:
            source: The source code string.
            language: Programming language (currently only ``"python"`` is
                supported).

        Returns:
            A dict with ``"language"``, ``"node_count"``, and ``"top_level"``
            (list of top-level node summaries).

        Raises:
            ValueError: If the language is unsupported.
            SyntaxError: If the source cannot be parsed.
        """
        if language not in self.SUPPORTED_LANGUAGES:
            raise ValueError(
                f"Unsupported language '{language}'. "
                f"Supported: {', '.join(self.SUPPORTED_LANGUAGES)}"
            )

        tree = ast.parse(source)
        nodes = list(ast.walk(tree))

        top_level = []
        for node in ast.iter_child_nodes(tree):
            summary: dict = {"type": type(node).__name__}
            if hasattr(node, "name"):
                summary["name"] = node.name
            if hasattr(node, "lineno"):
                summary["line"] = node.lineno
            top_level.append(summary)

        return {
            "language": language,
            "node_count": len(nodes),
            "top_level": top_level,
        }

    def find_pattern(self, code: str, pattern_name: str) -> list[ASTMatchResult]:
        """Search for a named structural pattern in Python code.

        Supported pattern names:
            - ``"singleton"`` -- classes with ``__new__`` or ``_instance``
            - ``"factory"`` -- functions/methods returning class instances
            - ``"decorator"`` -- decorated functions or classes
            - ``"context_manager"`` -- classes implementing ``__enter__``/``__exit__``

        Args:
            code: Python source code.
            pattern_name: Name of the pattern to search for.

        Returns:
            A list of :class:`ASTMatchResult` for each occurrence found.
        """
        tree = ast.parse(code)
        dispatchers = {
            "singleton": self._find_singleton,
            "factory": self._find_factory,
            "decorator": self._find_decorated,
            "context_manager": self._find_context_manager,
        }

        finder = dispatchers.get(pattern_name)
        if finder is None:
            logger.warning("Unknown pattern '%s'", pattern_name)
            return []

        return finder(tree)

    def find_antipatterns(self, code: str) -> list[ASTMatchResult]:
        """Scan code for common anti-patterns.

        Checks:
            - Bare ``except:`` clauses
            - Mutable default arguments (list/dict/set literals)
            - Star imports (``from x import *``)
            - Deeply nested functions (depth > 2)

        Args:
            code: Python source code.

        Returns:
            A list of :class:`ASTMatchResult` describing each anti-pattern found.
        """
        tree = ast.parse(code)
        results: list[ASTMatchResult] = []

        for check_name in self._ANTIPATTERN_CHECKS:
            checker = getattr(self, check_name)
            results.extend(checker(tree))

        return results

    def match_structure(self, code: str, template: str) -> bool:
        """Check if the code's top-level AST structure matches a template.

        The template is also valid Python.  Matching compares the sequence
        and types of top-level nodes (ClassDef, FunctionDef, Assign, etc.).
        Names are **not** compared -- the template defines the expected
        shape (number and types of top-level constructs), not the specific
        identifiers.

        Args:
            code: Python source code to test.
            template: Python source code defining the expected structure.

        Returns:
            ``True`` if the top-level node types match in order and count.
        """
        try:
            code_tree = ast.parse(code)
            tmpl_tree = ast.parse(template)
        except SyntaxError as e:
            logger.warning("Failed to parse code or template for structure matching: %s", e)
            return False

        code_nodes = list(ast.iter_child_nodes(code_tree))
        tmpl_nodes = list(ast.iter_child_nodes(tmpl_tree))

        if len(code_nodes) != len(tmpl_nodes):
            return False

        for c_node, t_node in zip(code_nodes, tmpl_nodes):
            if type(c_node) != type(t_node):
                return False

        return True

    # ------------------------------------------------------------------
    # Pattern finders
    # ------------------------------------------------------------------

    @staticmethod
    def _find_singleton(tree: ast.Module) -> list[ASTMatchResult]:
        """Execute  Find Singleton operations natively."""
        results = []
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                method_names = {
                    n.name
                    for n in node.body
                    if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
                }
                # Heuristic: overrides __new__ or has _instance attribute
                has_new = "__new__" in method_names
                has_instance_attr = any(
                    isinstance(n, ast.Assign)
                    and any(
                        isinstance(t, ast.Name) and t.id == "_instance"
                        for t in n.targets
                    )
                    for n in node.body
                )
                if has_new or has_instance_attr:
                    results.append(ASTMatchResult(
                        pattern_name="singleton",
                        node_type="ClassDef",
                        line=node.lineno,
                        col=node.col_offset,
                        name=node.name,
                        details="Overrides __new__" if has_new else "Has _instance attribute",
                    ))
        return results

    @staticmethod
    def _find_factory(tree: ast.Module) -> list[ASTMatchResult]:
        """Execute  Find Factory operations natively."""
        results = []
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                # Heuristic: function name contains "create" or "make" or "build"
                name_lower = node.name.lower()
                if any(kw in name_lower for kw in ("create", "make", "build", "factory")):
                    results.append(ASTMatchResult(
                        pattern_name="factory",
                        node_type=type(node).__name__,
                        line=node.lineno,
                        col=node.col_offset,
                        name=node.name,
                        details="Function name suggests factory pattern",
                    ))
        return results

    @staticmethod
    def _find_decorated(tree: ast.Module) -> list[ASTMatchResult]:
        """Execute  Find Decorated operations natively."""
        results = []
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                if node.decorator_list:
                    dec_names = []
                    for dec in node.decorator_list:
                        if isinstance(dec, ast.Name):
                            dec_names.append(dec.id)
                        elif isinstance(dec, ast.Attribute):
                            dec_names.append(dec.attr)
                        elif isinstance(dec, ast.Call):
                            if isinstance(dec.func, ast.Name):
                                dec_names.append(dec.func.id)
                    results.append(ASTMatchResult(
                        pattern_name="decorator",
                        node_type=type(node).__name__,
                        line=node.lineno,
                        col=node.col_offset,
                        name=getattr(node, "name", ""),
                        details=f"Decorators: {', '.join(dec_names)}",
                    ))
        return results

    @staticmethod
    def _find_context_manager(tree: ast.Module) -> list[ASTMatchResult]:
        """Execute  Find Context Manager operations natively."""
        results = []
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                method_names = {
                    n.name
                    for n in node.body
                    if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
                }
                if "__enter__" in method_names and "__exit__" in method_names:
                    results.append(ASTMatchResult(
                        pattern_name="context_manager",
                        node_type="ClassDef",
                        line=node.lineno,
                        col=node.col_offset,
                        name=node.name,
                        details="Implements __enter__ and __exit__",
                    ))
        return results

    # ------------------------------------------------------------------
    # Anti-pattern checkers
    # ------------------------------------------------------------------

    @staticmethod
    def _check_bare_except(tree: ast.Module) -> list[ASTMatchResult]:
        """Execute  Check Bare Except operations natively."""
        results = []
        for node in ast.walk(tree):
            if isinstance(node, ast.ExceptHandler) and node.type is None:
                results.append(ASTMatchResult(
                    pattern_name="bare_except",
                    node_type="ExceptHandler",
                    line=node.lineno,
                    col=node.col_offset,
                    details="Bare 'except:' catches all exceptions including KeyboardInterrupt",
                ))
        return results

    @staticmethod
    def _check_mutable_default_arg(tree: ast.Module) -> list[ASTMatchResult]:
        """Execute  Check Mutable Default Arg operations natively."""
        results = []
        mutable_types = (ast.List, ast.Dict, ast.Set)
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                for default in node.args.defaults + node.args.kw_defaults:
                    if isinstance(default, mutable_types):
                        results.append(ASTMatchResult(
                            pattern_name="mutable_default_arg",
                            node_type=type(node).__name__,
                            line=node.lineno,
                            col=node.col_offset,
                            name=node.name,
                            details="Mutable default argument (list/dict/set literal)",
                        ))
                        break  # one per function is enough
        return results

    @staticmethod
    def _check_star_import(tree: ast.Module) -> list[ASTMatchResult]:
        """Execute  Check Star Import operations natively."""
        results = []
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                for alias in node.names:
                    if alias.name == "*":
                        module_name = node.module or "<unknown>"
                        results.append(ASTMatchResult(
                            pattern_name="star_import",
                            node_type="ImportFrom",
                            line=node.lineno,
                            col=node.col_offset,
                            details=f"from {module_name} import *",
                        ))
        return results

    @staticmethod
    def _check_nested_function_depth(
        tree: ast.Module,
        max_depth: int = 2,
    ) -> list[ASTMatchResult]:
        """Execute  Check Nested Function Depth operations natively."""
        results: list[ASTMatchResult] = []

        def _walk(node: ast.AST, depth: int) -> None:
            """Execute  Walk operations natively."""
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if depth > max_depth:
                    results.append(ASTMatchResult(
                        pattern_name="deep_nesting",
                        node_type=type(node).__name__,
                        line=node.lineno,
                        col=node.col_offset,
                        name=node.name,
                        details=f"Function nested {depth} levels deep (max {max_depth})",
                    ))
                for child in ast.iter_child_nodes(node):
                    _walk(child, depth + 1)
            else:
                for child in ast.iter_child_nodes(node):
                    _walk(child, depth)

        for child in ast.iter_child_nodes(tree):
            _walk(child, 0)

        return results

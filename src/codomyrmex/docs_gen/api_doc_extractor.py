"""API documentation extractor.

Extracts docstrings, signatures, and metadata from Python
modules for generating API reference documentation.
"""

from __future__ import annotations

import ast
from dataclasses import dataclass, field


@dataclass
class FunctionDoc:
    """Documentation for a function.

    Attributes:
        name: Function name.
        signature: Parameter signature string.
        docstring: Parsed docstring.
        module: Containing module.
        decorators: Decorator names.
        is_async: Whether the function is async.
    """

    name: str
    signature: str = ""
    docstring: str = ""
    module: str = ""
    decorators: list[str] = field(default_factory=list)
    is_async: bool = False


@dataclass
class ClassDoc:
    """Documentation for a class.

    Attributes:
        name: Class name.
        docstring: Class docstring.
        module: Containing module.
        methods: Documented methods.
        bases: Base class names.
    """

    name: str
    docstring: str = ""
    module: str = ""
    methods: list[FunctionDoc] = field(default_factory=list)
    bases: list[str] = field(default_factory=list)


@dataclass
class ModuleDoc:
    """Documentation for a module.

    Attributes:
        name: Module name.
        docstring: Module-level docstring.
        path: File path.
        classes: Documented classes.
        functions: Top-level functions.
        exports: __all__ exports.
    """

    name: str
    docstring: str = ""
    path: str = ""
    classes: list[ClassDoc] = field(default_factory=list)
    functions: list[FunctionDoc] = field(default_factory=list)
    exports: list[str] = field(default_factory=list)


class APIDocExtractor:
    """Extract API documentation from Python source code.

    Parses source using AST to extract classes, functions,
    docstrings, and signatures.

    Example::

        extractor = APIDocExtractor()
        doc = extractor.extract_from_source(source_code, "mymodule")
    """

    def extract_from_source(self, source: str, module_name: str = "") -> ModuleDoc:
        """Extract documentation from Python source.

        Args:
            source: Python source code.
            module_name: Module name for context.

        Returns:
            ModuleDoc with extracted documentation.
        """
        tree = ast.parse(source)
        module_doc = ModuleDoc(name=module_name)

        # Module docstring
        if (tree.body and isinstance(tree.body[0], ast.Expr)
                and isinstance(tree.body[0].value, ast.Constant)
                and isinstance(tree.body[0].value.value, str)):
            module_doc.docstring = tree.body[0].value.value.strip()

        # Extract __all__
        for node in ast.walk(tree):
            if (isinstance(node, ast.Assign)
                    and any(isinstance(t, ast.Name) and t.id == "__all__" for t in node.targets)):
                if isinstance(node.value, ast.List):
                    module_doc.exports = [
                        elt.value for elt in node.value.elts
                        if isinstance(elt, ast.Constant) and isinstance(elt.value, str)
                    ]

        for node in tree.body:
            if isinstance(node, ast.ClassDef):
                module_doc.classes.append(self._extract_class(node, module_name))
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                module_doc.functions.append(self._extract_function(node, module_name))

        return module_doc

    def _extract_class(self, node: ast.ClassDef, module: str) -> ClassDoc:
        """Extract class documentation."""
        doc = ClassDoc(
            name=node.name,
            module=module,
            docstring=ast.get_docstring(node) or "",
            bases=[self._name_str(b) for b in node.bases],
        )

        for item in node.body:
            if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                doc.methods.append(self._extract_function(item, module))

        return doc

    def _extract_function(self, node: ast.FunctionDef | ast.AsyncFunctionDef, module: str) -> FunctionDoc:
        """Extract function documentation."""
        params = []
        for arg in node.args.args:
            params.append(arg.arg)

        decorators = []
        for dec in node.decorator_list:
            if isinstance(dec, ast.Name):
                decorators.append(dec.id)
            elif isinstance(dec, ast.Attribute):
                decorators.append(dec.attr)

        return FunctionDoc(
            name=node.name,
            signature=f"({', '.join(params)})",
            docstring=ast.get_docstring(node) or "",
            module=module,
            decorators=decorators,
            is_async=isinstance(node, ast.AsyncFunctionDef),
        )

    @staticmethod
    def _name_str(node: ast.expr) -> str:
        """name Str ."""
        if isinstance(node, ast.Name):
            return node.id
        if isinstance(node, ast.Attribute):
            return node.attr
        return ""

    def to_markdown(self, doc: ModuleDoc) -> str:
        """Render module documentation as markdown."""
        lines = [f"# `{doc.name}`", ""]
        if doc.docstring:
            lines.extend([doc.docstring, ""])

        for cls in doc.classes:
            lines.extend([f"## `{cls.name}`", ""])
            if cls.docstring:
                lines.extend([cls.docstring, ""])
            for method in cls.methods:
                lines.append(f"### `{method.name}{method.signature}`")
                if method.docstring:
                    lines.extend(["", method.docstring, ""])

        for func in doc.functions:
            lines.extend([f"## `{func.name}{func.signature}`", ""])
            if func.docstring:
                lines.extend([func.docstring, ""])

        return "\n".join(lines)


__all__ = ["APIDocExtractor", "ClassDoc", "FunctionDoc", "ModuleDoc"]

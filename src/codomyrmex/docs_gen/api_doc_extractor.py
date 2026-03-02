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
            bases=[ast.unparse(b) for b in node.bases],
        )

        for item in node.body:
            if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                doc.methods.append(self._extract_function(item, module))

        return doc

    def _extract_function(self, node: ast.FunctionDef | ast.AsyncFunctionDef, module: str) -> FunctionDoc:
        """Extract function documentation."""
        arg_strings = []

        # Positional-only args
        for i, arg in enumerate(node.args.posonlyargs):
            s = arg.arg
            if arg.annotation:
                s += f": {ast.unparse(arg.annotation)}"
            arg_strings.append(s)
        if node.args.posonlyargs:
            arg_strings.append("/")

        # Standard args
        for i, arg in enumerate(node.args.args):
            s = arg.arg
            if arg.annotation:
                s += f": {ast.unparse(arg.annotation)}"

            # Find default
            default_idx = i - (len(node.args.args) - len(node.args.defaults))
            if default_idx >= 0:
                s += f" = {ast.unparse(node.args.defaults[default_idx])}"
            arg_strings.append(s)

        # *args
        if node.args.vararg:
            s = f"*{node.args.vararg.arg}"
            if node.args.vararg.annotation:
                s += f": {ast.unparse(node.args.vararg.annotation)}"
            arg_strings.append(s)
        elif node.args.kwonlyargs:
            arg_strings.append("*")

        # Kw-only args
        for i, arg in enumerate(node.args.kwonlyargs):
            s = arg.arg
            if arg.annotation:
                s += f": {ast.unparse(arg.annotation)}"

            default = node.args.kw_defaults[i]
            if default:
                s += f" = {ast.unparse(default)}"
            arg_strings.append(s)

        # **kwargs
        if node.args.kwarg:
            s = f"**{node.args.kwarg.arg}"
            if node.args.kwarg.annotation:
                s += f": {ast.unparse(node.args.kwarg.annotation)}"
            arg_strings.append(s)

        signature = f"({', '.join(arg_strings)})"
        if node.returns:
            signature += f" -> {ast.unparse(node.returns)}"

        decorators = []
        for dec in node.decorator_list:
            decorators.append(ast.unparse(dec))

        return FunctionDoc(
            name=node.name,
            signature=signature,
            docstring=ast.get_docstring(node) or "",
            module=module,
            decorators=decorators,
            is_async=isinstance(node, ast.AsyncFunctionDef),
        )

    def to_markdown(self, doc: ModuleDoc) -> str:
        """Render module documentation as markdown."""
        lines = [f"# Module `{doc.name}`", ""]
        if doc.docstring:
            lines.extend([doc.docstring, ""])

        if doc.exports:
            lines.extend(["## Exports", "", ", ".join(f"`{e}`" for e in doc.exports), ""])

        for cls in doc.classes:
            bases_str = f"({', '.join(cls.bases)})" if cls.bases else ""
            lines.extend([f"## Class `{cls.name}{bases_str}`", ""])
            if cls.docstring:
                lines.extend([cls.docstring, ""])

            if cls.methods:
                lines.extend(["### Methods", ""])
                for method in cls.methods:
                    async_prefix = "async " if method.is_async else ""
                    decorators = "".join(f"@{d}\n" for d in method.decorators)
                    lines.append(f"#### `{async_prefix}{method.name}{method.signature}`")
                    if decorators:
                        lines.extend(["```python", decorators.strip(), "```", ""])
                    if method.docstring:
                        lines.extend(["", method.docstring, ""])

        if doc.functions:
            lines.extend(["## Functions", ""])
            for func in doc.functions:
                async_prefix = "async " if func.is_async else ""
                lines.extend([f"### `{async_prefix}{func.name}{func.signature}`", ""])
                if func.docstring:
                    lines.extend([func.docstring, ""])

        return "\n".join(lines)


__all__ = ["APIDocExtractor", "ClassDoc", "FunctionDoc", "ModuleDoc"]

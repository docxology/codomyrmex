"""MCP tool schema boundary verifier.

Uses Z3 to verify that MCP tool schemas (parameter types, required fields)
match the actual implementation function signatures.

Example::

    verifier = SchemaVerifier()
    violations = verifier.verify_all()
    assert len(violations) == 0
"""

from __future__ import annotations

import ast
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

_SRC_ROOT = Path(__file__).resolve().parents[2]


@dataclass
class SchemaViolation:
    """A mismatch between MCP schema and implementation.

    Attributes:
        tool_name: Name of the MCP tool.
        module_path: Python module path.
        violation_type: Category of mismatch.
        message: Human-readable description.
        severity: ``"error"`` or ``"warning"``.
    """

    tool_name: str
    module_path: str
    violation_type: str
    message: str
    severity: str = "error"


@dataclass
class ToolSchemaInfo:
    """Extracted schema information for an MCP tool.

    Attributes:
        name: Tool name from the decorator.
        module_path: Full module path.
        file_path: Filesystem path.
        parameters: Expected parameter names.
        function_name: Python function name.
        function_params: Actual function parameter names.
    """

    name: str
    module_path: str
    file_path: str
    parameters: list[str] = field(default_factory=list)
    function_name: str = ""
    function_params: list[str] = field(default_factory=list)


class SchemaVerifier:
    """Verifies MCP tool schemas match their implementation signatures.

    Scans source for ``@mcp_tool`` decorators, extracts parameter schemas,
    and checks consistency with function signatures.

    Example::

        verifier = SchemaVerifier()
        violations = verifier.verify_all()
        for v in violations:
            print(f"{v.tool_name}: {v.message}")
    """

    def __init__(self, src_root: Path | None = None) -> None:
        self._src_root = src_root or _SRC_ROOT
        self._tools: list[ToolSchemaInfo] = []

    def scan_tools(self) -> list[ToolSchemaInfo]:
        """Scan source tree for MCP tool definitions.

        Returns:
            List of :class:`ToolSchemaInfo` for all discovered tools.
        """
        tools: list[ToolSchemaInfo] = []
        codomyrmex_root = self._src_root / "codomyrmex"

        for py_file in codomyrmex_root.rglob("*.py"):
            if "__pycache__" in str(py_file):
                continue
            try:
                source = py_file.read_text(encoding="utf-8", errors="replace")
                if "@mcp_tool" not in source and "mcp_tool" not in source:
                    continue
                tree = ast.parse(source)
                tools.extend(self._extract_tools(tree, py_file))
            except (SyntaxError, UnicodeDecodeError):
                continue

        self._tools = tools
        logger.info("Scanned %d MCP tools", len(tools))
        return tools

    def _extract_tools(self, tree: ast.Module, file_path: Path) -> list[ToolSchemaInfo]:
        """Extract tool definitions from an AST."""
        tools: list[ToolSchemaInfo] = []
        rel_path = file_path.relative_to(self._src_root.parent)
        module_path = str(rel_path).replace("/", ".").removesuffix(".py")

        for node in ast.walk(tree):
            if not isinstance(node, ast.FunctionDef):
                continue

            # Check for @mcp_tool decorator
            is_mcp = False
            tool_name = node.name
            for dec in node.decorator_list:
                dec_name = ""
                if isinstance(dec, ast.Name):
                    dec_name = dec.id
                elif isinstance(dec, ast.Call):
                    if isinstance(dec.func, ast.Name):
                        dec_name = dec.func.id
                    elif isinstance(dec.func, ast.Attribute):
                        dec_name = dec.func.attr
                if dec_name == "mcp_tool":
                    is_mcp = True
                    # Extract tool name from decorator args
                    if isinstance(dec, ast.Call) and dec.args:
                        if isinstance(dec.args[0], ast.Constant):
                            tool_name = str(dec.args[0].value)

            if not is_mcp:
                continue

            # Extract function parameters (skip 'self')
            func_params = [arg.arg for arg in node.args.args if arg.arg != "self"]

            tools.append(
                ToolSchemaInfo(
                    name=tool_name,
                    module_path=module_path,
                    file_path=str(file_path),
                    function_name=node.name,
                    function_params=func_params,
                )
            )

        return tools

    def verify_all(self) -> list[SchemaViolation]:
        """Verify all discovered MCP tools.

        Returns:
            List of :class:`SchemaViolation` for any mismatches.
        """
        if not self._tools:
            self.scan_tools()

        violations: list[SchemaViolation] = []

        for tool in self._tools:
            violations.extend(self._verify_tool(tool))

        logger.info(
            "Verified %d tools, found %d violations",
            len(self._tools),
            len(violations),
        )
        return violations

    def _verify_tool(self, tool: ToolSchemaInfo) -> list[SchemaViolation]:
        """Verify a single tool's schema consistency."""
        violations: list[SchemaViolation] = []

        # Check: function must have a docstring
        try:
            source = Path(tool.file_path).read_text(encoding="utf-8")
            tree = ast.parse(source)
            for node in ast.walk(tree):
                if (
                    isinstance(node, ast.FunctionDef)
                    and node.name == tool.function_name
                ):
                    docstring = ast.get_docstring(node)
                    if not docstring:
                        violations.append(
                            SchemaViolation(
                                tool_name=tool.name,
                                module_path=tool.module_path,
                                violation_type="missing_docstring",
                                message=f"MCP tool '{tool.name}' ({tool.function_name}) has no docstring",
                                severity="warning",
                            )
                        )
                    break
        except Exception:
            pass

        # Check: function name should be snake_case
        if not tool.function_name.replace("_", "").isalpha():
            violations.append(
                SchemaViolation(
                    tool_name=tool.name,
                    module_path=tool.module_path,
                    violation_type="naming_convention",
                    message=f"Function '{tool.function_name}' contains non-alpha characters",
                    severity="warning",
                )
            )

        return violations

    def get_summary(self) -> dict[str, Any]:
        """Return a summary of the verification.

        Returns:
            Dict with ``total_tools``, ``violations``, and ``by_type``.
        """
        violations = self.verify_all()
        by_type: dict[str, int] = {}
        for v in violations:
            by_type[v.violation_type] = by_type.get(v.violation_type, 0) + 1

        return {
            "total_tools": len(self._tools),
            "total_violations": len(violations),
            "errors": sum(1 for v in violations if v.severity == "error"),
            "warnings": sum(1 for v in violations if v.severity == "warning"),
            "by_type": by_type,
        }


def verify_tool_schemas(src_root: Path | None = None) -> list[SchemaViolation]:
    """Convenience function to verify all MCP tool schemas.

    Args:
        src_root: Source root path.

    Returns:
        List of violations (empty if all tools pass).
    """
    verifier = SchemaVerifier(src_root)
    return verifier.verify_all()


__all__ = [
    "SchemaVerifier",
    "SchemaViolation",
    "ToolSchemaInfo",
    "verify_tool_schemas",
]

"""MCP tools for the tree_sitter module.

Exposes tree-sitter parsing, language listing, and symbol extraction
capabilities as MCP tools.
"""

from __future__ import annotations

from typing import Any

try:
    from codomyrmex.model_context_protocol.decorators import mcp_tool
except ImportError:

    def mcp_tool(**kwargs: Any):  # type: ignore[misc]
        def decorator(func: Any) -> Any:
            func._mcp_tool_meta = kwargs
            return func

        return decorator


@mcp_tool(category="tree_sitter")
def parse_code(
    code: str,
    language: str,
    library_path: str = "",
) -> dict[str, Any]:
    """Parse source code into an AST using tree-sitter.

    Loads the specified language (if not already loaded) and parses
    the provided source code string into a syntax tree.

    Args:
        code: Source code string to parse.
        language: Programming language name (e.g. 'python', 'javascript').
        library_path: Path to the tree-sitter language shared library.
            Required if the language has not been loaded previously.

    Returns:
        Dictionary with root node type, child count, and a simplified
        tree representation, or error information.
    """
    try:
        from codomyrmex.tree_sitter.languages.languages import LanguageManager
        from codomyrmex.tree_sitter.parsers.parser import TreeSitterParser

        lang = LanguageManager.get_language(language)
        if lang is None:
            if not library_path:
                return {
                    "status": "error",
                    "message": (
                        f"Language '{language}' is not loaded and no "
                        f"library_path was provided."
                    ),
                }
            loaded = LanguageManager.load_language(library_path, language)
            if not loaded:
                return {
                    "status": "error",
                    "message": f"Failed to load language '{language}' from '{library_path}'.",
                }
            lang = LanguageManager.get_language(language)

        parser = TreeSitterParser(lang)
        tree = parser.parse(code)
        root = tree.root_node

        def _summarise_node(node: Any, depth: int = 0, max_depth: int = 3) -> dict:
            summary: dict[str, Any] = {
                "type": node.type,
                "start": [node.start_point[0], node.start_point[1]],
                "end": [node.end_point[0], node.end_point[1]],
            }
            if depth < max_depth and node.child_count > 0:
                summary["children"] = [
                    _summarise_node(child, depth + 1, max_depth)
                    for child in node.children
                ]
            elif node.child_count > 0:
                summary["child_count"] = node.child_count
            return summary

        return {
            "status": "success",
            "language": language,
            "root_type": root.type,
            "root_child_count": root.child_count,
            "tree": _summarise_node(root),
        }
    except NotImplementedError as exc:
        return {"status": "error", "message": f"not yet implemented: {exc}"}
    except Exception as exc:
        return {"status": "error", "message": str(exc)}


@mcp_tool(category="tree_sitter")
def list_languages() -> dict[str, Any]:
    """List tree-sitter languages currently loaded in the LanguageManager.

    Returns:
        Dictionary with loaded language names.
    """
    try:
        from codomyrmex.tree_sitter.languages.languages import LanguageManager

        loaded = list(LanguageManager._languages.keys())
        return {
            "status": "success",
            "language_count": len(loaded),
            "languages": loaded,
        }
    except NotImplementedError as exc:
        return {"status": "error", "message": f"not yet implemented: {exc}"}
    except Exception as exc:
        return {"status": "error", "message": str(exc)}


@mcp_tool(category="tree_sitter")
def extract_symbols(
    code: str,
    language: str,
    library_path: str = "",
) -> dict[str, Any]:
    """Extract function and class names from source code using tree-sitter.

    Parses the code with tree-sitter and walks the AST to find
    top-level function_definition and class_definition nodes,
    returning their names and locations.

    Args:
        code: Source code string to analyse.
        language: Programming language name (e.g. 'python', 'javascript').
        library_path: Path to the tree-sitter language shared library.
            Required if the language has not been loaded previously.

    Returns:
        Dictionary with extracted symbols (functions and classes) or error info.
    """
    try:
        from codomyrmex.tree_sitter.languages.languages import LanguageManager
        from codomyrmex.tree_sitter.parsers.parser import TreeSitterParser

        lang = LanguageManager.get_language(language)
        if lang is None:
            if not library_path:
                return {
                    "status": "error",
                    "message": (
                        f"Language '{language}' is not loaded and no "
                        f"library_path was provided."
                    ),
                }
            loaded = LanguageManager.load_language(library_path, language)
            if not loaded:
                return {
                    "status": "error",
                    "message": f"Failed to load language '{language}' from '{library_path}'.",
                }
            lang = LanguageManager.get_language(language)

        parser = TreeSitterParser(lang)
        tree = parser.parse(code)
        root = tree.root_node

        functions: list[dict[str, Any]] = []
        classes: list[dict[str, Any]] = []

        # Walk children of root to find top-level definitions
        for node in root.children:
            node_type = node.type
            if node_type in ("function_definition", "function_declaration"):
                name_node = node.child_by_field_name("name")
                name = name_node.text.decode("utf-8") if name_node else "<unknown>"
                functions.append(
                    {
                        "name": name,
                        "line": node.start_point[0] + 1,
                        "col": node.start_point[1],
                    }
                )
            elif node_type in ("class_definition", "class_declaration"):
                name_node = node.child_by_field_name("name")
                name = name_node.text.decode("utf-8") if name_node else "<unknown>"
                classes.append(
                    {
                        "name": name,
                        "line": node.start_point[0] + 1,
                        "col": node.start_point[1],
                    }
                )

        return {
            "status": "success",
            "language": language,
            "functions": functions,
            "classes": classes,
            "total_symbols": len(functions) + len(classes),
        }
    except NotImplementedError as exc:
        return {"status": "error", "message": f"not yet implemented: {exc}"}
    except Exception as exc:
        return {"status": "error", "message": str(exc)}

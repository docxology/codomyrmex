"""MCP tools for the docs_gen module."""

from codomyrmex.model_context_protocol.decorators import mcp_tool


@mcp_tool(category="docs_gen")
def docs_gen_extract_api(
    source_code: str,
    module_name: str = "",
) -> dict:
    """Extract API documentation from Python source code.

    Parses docstrings, type signatures, classes, and functions from the
    provided source code string using the APIDocExtractor.

    Args:
        source_code: Python source code to extract documentation from.
        module_name: Optional module name label for the output.

    Returns:
        Dictionary with extracted functions, classes, and module docstring.
    """
    try:
        from codomyrmex.docs_gen import APIDocExtractor

        extractor = APIDocExtractor()
        doc = extractor.extract_from_source(source_code, module_name=module_name)
        return {
            "status": "success",
            "module_name": doc.name,
            "docstring": doc.docstring,
            "functions": [
                {"name": f.name, "signature": f.signature, "docstring": f.docstring}
                for f in doc.functions
            ],
            "classes": [
                {
                    "name": c.name,
                    "docstring": c.docstring,
                    "methods": [m.name for m in c.methods],
                }
                for c in doc.classes
            ],
            "function_count": len(doc.functions),
            "class_count": len(doc.classes),
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


@mcp_tool(category="docs_gen")
def docs_gen_build_search_index(
    source_code: str,
    module_name: str = "",
) -> dict:
    """Extract API docs and build a searchable in-memory index.

    Combines APIDocExtractor with SearchIndex to produce a full-text
    searchable index of the provided source code's documentation.

    Args:
        source_code: Python source code to index.
        module_name: Optional module name label.

    Returns:
        Dictionary with index statistics and example search capability.
    """
    try:
        from codomyrmex.docs_gen import APIDocExtractor, SearchIndex

        extractor = APIDocExtractor()
        doc = extractor.extract_from_source(source_code, module_name=module_name)

        index = SearchIndex()
        # Index each function and class as a separate entry
        for fn in doc.functions:
            index.add(
                fn.name, title=fn.name, content=fn.docstring or "", tags=["function"]
            )
        for cls in doc.classes:
            index.add(
                cls.name, title=cls.name, content=cls.docstring or "", tags=["class"]
            )

        return {
            "status": "success",
            "module_name": doc.name,
            "indexed_entries": len(doc.functions) + len(doc.classes),
            "function_count": len(doc.functions),
            "class_count": len(doc.classes),
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

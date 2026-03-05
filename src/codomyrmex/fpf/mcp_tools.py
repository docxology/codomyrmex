"""MCP tool definitions for the fpf (First Principles Framework) module.

Exposes FPF specification parsing and pattern listing as MCP tools.
"""

from __future__ import annotations

from typing import Any

from codomyrmex.model_context_protocol.decorators import mcp_tool


def _get_parser():
    """Lazy import of FPFParser."""
    from codomyrmex.fpf.core.parser import FPFParser

    return FPFParser


def _get_models():
    """Lazy import of FPF core models."""
    from codomyrmex.fpf.core import models

    return models


@mcp_tool(
    category="fpf",
    description="List available FPF pattern statuses and relationship types.",
)
def fpf_list_types() -> dict[str, Any]:
    """List all FPF pattern statuses, concept types, and relationship types.

    Returns:
        dict with keys: status, pattern_statuses, concept_types, relationship_types
    """
    try:
        models = _get_models()
        return {
            "status": "success",
            "pattern_statuses": [ps.value for ps in models.PatternStatus],
            "concept_types": [ct.value for ct in models.ConceptType],
            "relationship_types": [rt.value for rt in models.RelationshipType],
        }
    except Exception as exc:
        return {"status": "error", "message": str(exc)}


@mcp_tool(
    category="fpf",
    description=(
        "Parse FPF specification markdown content and return extracted patterns "
        "with their IDs, titles, and statuses."
    ),
)
def fpf_parse_spec(
    markdown_content: str,
    source_path: str = "",
) -> dict[str, Any]:
    """Parse FPF specification markdown and extract patterns.

    Args:
        markdown_content: Raw markdown content of an FPF specification.
        source_path: Optional source path or URL for provenance tracking.

    Returns:
        dict with keys: status, version, pattern_count, patterns (list of summaries)
    """
    try:
        parser_cls = _get_parser()
        parser = parser_cls()
        spec = parser.parse_spec(markdown_content, source_path=source_path or None)

        pattern_summaries = [
            {
                "id": p.id,
                "title": p.title,
                "status": p.status,
                "keywords": p.keywords[:5],
                "section_count": len(p.sections),
            }
            for p in spec.patterns
        ]

        return {
            "status": "success",
            "version": spec.version,
            "pattern_count": len(spec.patterns),
            "patterns": pattern_summaries,
        }
    except Exception as exc:
        return {"status": "error", "message": str(exc)}


@mcp_tool(
    category="fpf",
    description=(
        "Search parsed FPF patterns by keyword in an FPFIndex. "
        "Requires markdown content to parse first."
    ),
)
def fpf_search_patterns(
    markdown_content: str,
    query: str,
    status_filter: str = "",
) -> dict[str, Any]:
    """Parse FPF markdown and search patterns by query string.

    Args:
        markdown_content: Raw markdown content of an FPF specification.
        query: Search query to match against pattern titles, keywords, and content.
        status_filter: Optional pattern status filter (Stable, Draft, Stub, New).

    Returns:
        dict with keys: status, query, match_count, matches
    """
    try:
        parser_cls = _get_parser()
        parser = parser_cls()
        spec = parser.parse_spec(markdown_content)

        from codomyrmex.fpf.analysis.indexer import FPFIndexer

        indexer = FPFIndexer()
        indexer.build_index(spec)

        filters = {}
        if status_filter:
            filters["status"] = status_filter

        results = indexer.search_patterns(query, filters or None)

        matches = [
            {
                "id": p.id,
                "title": p.title,
                "status": p.status,
            }
            for p in results
        ]

        return {
            "status": "success",
            "query": query,
            "match_count": len(matches),
            "matches": matches,
        }
    except Exception as exc:
        return {"status": "error", "message": str(exc)}

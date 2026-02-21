"""MCP tool definitions for the scrape module.

Exposes web crawling and content extraction as MCP tools.
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


@mcp_tool(
    category="scrape",
    description="Extract structured content (title, headings, links) from raw HTML.",
)
def scrape_extract_content(
    html: str,
    base_url: str = "",
) -> dict[str, Any]:
    """Extract structured data from HTML content.

    Args:
        html: Raw HTML string.
        base_url: Base URL for resolving relative links.
    """
    try:
        from codomyrmex.scrape.content_extractor import ContentExtractor
        extractor = ContentExtractor(base_url=base_url)
        result = extractor.extract(html)
        return {
            "status": "ok",
            "title": result.title,
            "headings": [{"level": h[0], "text": h[1]} for h in result.headings],
            "paragraph_count": len(result.paragraphs),
            "link_count": len(result.links),
            "image_count": len(result.images),
            "word_count": result.word_count,
            "content_hash": result.content_hash,
            "meta": result.meta,
        }
    except Exception as exc:
        return {"status": "error", "error": str(exc)}


@mcp_tool(
    category="scrape",
    description="Compute text similarity between two strings using Jaccard index.",
)
def scrape_text_similarity(
    text_a: str,
    text_b: str,
) -> dict[str, Any]:
    """Compute Jaccard word-level similarity between two texts.

    Args:
        text_a: First text.
        text_b: Second text.
    """
    try:
        from codomyrmex.scrape.content_extractor import text_similarity
        score = text_similarity(text_a, text_b)
        return {"status": "ok", "similarity": score}
    except Exception as exc:
        return {"status": "error", "error": str(exc)}

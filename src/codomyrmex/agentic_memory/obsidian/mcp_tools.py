"""
Obsidian MCP Tool Definitions.

Exposes Obsidian vault operations as MCP tools for AI agent consumption.
Read operations are unrestricted; write operations follow trust gateway patterns.
"""

from __future__ import annotations

from typing import Any, Dict, List

from codomyrmex.model_context_protocol.decorators import mcp_tool


@mcp_tool(category="obsidian", description="Load an Obsidian vault and return metadata.")
def obsidian_load_vault(vault_path: str) -> Dict[str, Any]:
    """Load an Obsidian vault and return its metadata summary.

    Args:
        vault_path: Absolute path to the Obsidian vault root directory.

    Returns:
        Dict with vault metadata including note count, tags, links.
    """
    try:
        from .vault import ObsidianVault

        vault = ObsidianVault(vault_path)
        meta = vault.metadata
        return {
            "status": "ok",
            "path": str(meta.path),
            "note_count": meta.note_count,
            "tag_count": meta.tag_count,
            "link_count": meta.link_count,
            "broken_link_count": meta.broken_link_count,
            "orphan_count": meta.orphan_count,
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}


@mcp_tool(category="obsidian", description="Read a note from an Obsidian vault.")
def obsidian_read_note(vault_path: str, note_path: str) -> Dict[str, Any]:
    """Read and parse a note from an Obsidian vault.

    Args:
        vault_path: Absolute path to the Obsidian vault root directory.
        note_path: Relative path to the note within the vault.

    Returns:
        Dict with note content, frontmatter, links, tags, and headings.
    """
    try:
        from .crud import read_note
        from .vault import ObsidianVault

        vault = ObsidianVault(vault_path)
        note = read_note(vault, note_path)
        return {
            "status": "ok",
            "title": note.title,
            "path": str(note.path),
            "frontmatter": note.frontmatter,
            "content": note.content,
            "links": [{"target": l.target, "alias": l.alias} for l in note.links],
            "tags": [{"name": t.name, "source": t.source} for t in note.tags],
            "headings": [{"level": h[0], "text": h[1]} for h in note.headings],
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}


@mcp_tool(category="obsidian", description="Search notes in an Obsidian vault.")
def obsidian_search(vault_path: str, query: str, limit: int = 20) -> Dict[str, Any]:
    """Search notes in an Obsidian vault by content, title, or tags.

    Args:
        vault_path: Absolute path to the Obsidian vault root directory.
        query: Search query string.
        limit: Maximum number of results.

    Returns:
        Dict with list of search results including scores and context.
    """
    try:
        from .search import search_vault
        from .vault import ObsidianVault

        vault = ObsidianVault(vault_path)
        results = search_vault(vault, query, limit=limit)
        return {
            "status": "ok",
            "count": len(results),
            "results": [
                {
                    "title": r.note.title,
                    "path": str(r.note.path),
                    "score": r.score,
                    "context": r.context,
                    "match_type": r.match_type,
                }
                for r in results
            ],
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}


@mcp_tool(category="obsidian", description="Get backlinks for a note in an Obsidian vault.")
def obsidian_get_backlinks(vault_path: str, note_path: str) -> Dict[str, Any]:
    """Get all notes that link to the specified note.

    Args:
        vault_path: Absolute path to the Obsidian vault root directory.
        note_path: Relative path or title of the target note.

    Returns:
        Dict with list of backlinking notes.
    """
    try:
        from .graph import get_backlinks
        from .vault import ObsidianVault

        vault = ObsidianVault(vault_path)
        backlinks = get_backlinks(vault, note_path)
        return {
            "status": "ok",
            "count": len(backlinks),
            "backlinks": [
                {"title": n.title, "path": str(n.path)} for n in backlinks
            ],
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}


@mcp_tool(category="obsidian", description="List all tags in an Obsidian vault.")
def obsidian_list_tags(vault_path: str) -> Dict[str, Any]:
    """List all tags in the vault with occurrence counts.

    Args:
        vault_path: Absolute path to the Obsidian vault root directory.

    Returns:
        Dict with tag names and counts.
    """
    try:
        from .vault import ObsidianVault

        vault = ObsidianVault(vault_path)
        tags = vault.get_all_tags()
        return {
            "status": "ok",
            "count": len(tags),
            "tags": [{"name": k, "count": v} for k, v in sorted(tags.items())],
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}


@mcp_tool(category="obsidian", description="Get vault statistics and metadata.")
def obsidian_vault_stats(vault_path: str) -> Dict[str, Any]:
    """Get comprehensive vault statistics including link graph metrics.

    Args:
        vault_path: Absolute path to the Obsidian vault root directory.

    Returns:
        Dict with note count, link stats, graph density, and top linked notes.
    """
    try:
        from .graph import get_link_stats
        from .vault import ObsidianVault

        vault = ObsidianVault(vault_path)
        meta = vault.metadata
        link_stats = get_link_stats(vault)
        return {
            "status": "ok",
            "note_count": meta.note_count,
            "tag_count": meta.tag_count,
            "link_count": meta.link_count,
            "broken_link_count": meta.broken_link_count,
            "orphan_count": meta.orphan_count,
            "graph": link_stats,
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}


@mcp_tool(category="obsidian", description="Find broken links in an Obsidian vault.")
def obsidian_find_broken_links(vault_path: str) -> Dict[str, Any]:
    """Find wikilinks that point to non-existent notes.

    Args:
        vault_path: Absolute path to the Obsidian vault root directory.

    Returns:
        Dict with list of broken links and their source notes.
    """
    try:
        from .graph import find_broken_links
        from .vault import ObsidianVault

        vault = ObsidianVault(vault_path)
        broken = find_broken_links(vault)
        return {
            "status": "ok",
            "count": len(broken),
            "broken_links": [
                {
                    "source_note": note.title,
                    "source_path": str(note.path),
                    "target": link.target,
                    "raw": link.raw,
                }
                for note, link in broken
            ],
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}


@mcp_tool(category="obsidian", description="Parse an Obsidian canvas file.")
def obsidian_read_canvas(canvas_path: str) -> Dict[str, Any]:
    """Parse an Obsidian .canvas file and return its structure.

    Args:
        canvas_path: Absolute path to the .canvas file.

    Returns:
        Dict with canvas nodes and edges.
    """
    try:
        from .canvas import canvas_to_dict, parse_canvas

        canvas = parse_canvas(canvas_path)
        result = canvas_to_dict(canvas)
        result["status"] = "ok"
        return result
    except Exception as e:
        return {"status": "error", "error": str(e)}


# --- Write tools (trust-gated) ---


@mcp_tool(category="obsidian", description="Create a new note in an Obsidian vault.")
def obsidian_create_note(
    vault_path: str,
    note_path: str,
    content: str = "",
    frontmatter: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    """Create a new note in an Obsidian vault.

    Args:
        vault_path: Absolute path to the Obsidian vault root directory.
        note_path: Relative path for the new note.
        content: Note body content.
        frontmatter: Optional YAML frontmatter dict.

    Returns:
        Dict with created note info.
    """
    try:
        from .crud import create_note
        from .vault import ObsidianVault

        vault = ObsidianVault(vault_path)
        note = create_note(vault, note_path, content=content, frontmatter=frontmatter)
        return {
            "status": "ok",
            "title": note.title,
            "path": str(note.path),
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}


@mcp_tool(category="obsidian", description="Update a note in an Obsidian vault.")
def obsidian_update_note(
    vault_path: str,
    note_path: str,
    content: str | None = None,
    frontmatter: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    """Update a note's content and/or frontmatter.

    Args:
        vault_path: Absolute path to the Obsidian vault root directory.
        note_path: Relative path to the note.
        content: New body content (None = keep existing).
        frontmatter: Dict to merge into frontmatter (None = keep existing).

    Returns:
        Dict with updated note info.
    """
    try:
        from .crud import update_note
        from .vault import ObsidianVault

        vault = ObsidianVault(vault_path)
        note = update_note(vault, note_path, content=content, frontmatter=frontmatter)
        return {
            "status": "ok",
            "title": note.title,
            "path": str(note.path),
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}


@mcp_tool(category="obsidian", description="Delete a note from an Obsidian vault.")
def obsidian_delete_note(vault_path: str, note_path: str) -> Dict[str, Any]:
    """Delete a note from an Obsidian vault.

    Args:
        vault_path: Absolute path to the Obsidian vault root directory.
        note_path: Relative path to the note.

    Returns:
        Dict with deletion status.
    """
    try:
        from .crud import delete_note
        from .vault import ObsidianVault

        vault = ObsidianVault(vault_path)
        deleted = delete_note(vault, note_path)
        return {
            "status": "ok" if deleted else "not_found",
            "deleted": deleted,
            "path": note_path,
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}

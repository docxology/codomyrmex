"""
Obsidian Vault Tooling.

Full-featured Obsidian vault interaction module for reading, parsing,
editing, searching, and analyzing Obsidian vaults. Supports wikilinks,
embeds, callouts, tags, frontmatter, canvas files, and link graph analysis.
"""

__version__ = "0.1.0"

from .models import (
    Canvas,
    CanvasEdge,
    CanvasNode,
    Callout,
    Embed,
    Note,
    SearchResult,
    Tag,
    VaultMetadata,
    WikiLink,
)
from .parser import (
    extract_callouts,
    extract_embeds,
    extract_headings,
    extract_tags,
    extract_wikilinks,
    parse_frontmatter,
    parse_note,
    serialize_note,
)
from .vault import ObsidianVault
from .crud import (
    create_note,
    delete_note,
    get_frontmatter,
    read_note,
    rename_note,
    set_frontmatter,
    update_note,
)
from .graph import (
    build_link_graph,
    find_broken_links,
    find_orphans,
    get_backlinks,
    get_forward_links,
    get_link_stats,
)
from .search import (
    filter_by_date,
    filter_by_frontmatter,
    filter_by_tag,
    search_vault,
)
from .canvas import (
    add_canvas_edge,
    add_canvas_node,
    canvas_from_dict,
    canvas_to_dict,
    create_canvas,
    parse_canvas,
)
from .mcp_tools import (
    obsidian_create_note,
    obsidian_delete_note,
    obsidian_find_broken_links,
    obsidian_get_backlinks,
    obsidian_list_tags,
    obsidian_load_vault,
    obsidian_read_canvas,
    obsidian_read_note,
    obsidian_search,
    obsidian_update_note,
    obsidian_vault_stats,
)


def cli_commands():
    """Return CLI commands for the obsidian module."""

    def _vault(path: str = "."):
        """Show vault statistics for a path."""
        vault = ObsidianVault(path)
        meta = vault.metadata
        print(f"Vault: {meta.path}")
        print(f"  Notes: {meta.note_count}")
        print(f"  Tags: {meta.tag_count}")
        print(f"  Links: {meta.link_count}")
        print(f"  Broken links: {meta.broken_link_count}")
        print(f"  Orphans: {meta.orphan_count}")

    def _search(path: str = ".", query: str = ""):
        """Search vault by query."""
        if not query:
            print("Usage: obsidian search --path <vault> --query <term>")
            return
        vault = ObsidianVault(path)
        results = search_vault(vault, query)
        if not results:
            print(f"No results for: {query}")
            return
        for r in results:
            print(f"  [{r.score:.1f}] {r.note.title} ({r.match_type})")

    def _tags(path: str = "."):
        """List all tags in vault."""
        vault = ObsidianVault(path)
        tags = vault.get_all_tags()
        for name, count in sorted(tags.items()):
            print(f"  #{name}: {count}")

    def _broken_links(path: str = "."):
        """Find broken wikilinks."""
        vault = ObsidianVault(path)
        broken = find_broken_links(vault)
        if not broken:
            print("No broken links found.")
            return
        for note, link in broken:
            print(f"  {note.title} -> [[{link.target}]]")

    return {
        "vault": _vault,
        "search": _search,
        "tags": _tags,
        "broken-links": _broken_links,
    }


__all__ = [
    # Models
    "Canvas",
    "CanvasEdge",
    "CanvasNode",
    "Callout",
    "Embed",
    "Note",
    "SearchResult",
    "Tag",
    "VaultMetadata",
    "WikiLink",
    # Parser
    "extract_callouts",
    "extract_embeds",
    "extract_headings",
    "extract_tags",
    "extract_wikilinks",
    "parse_frontmatter",
    "parse_note",
    "serialize_note",
    # Vault
    "ObsidianVault",
    # CRUD
    "create_note",
    "delete_note",
    "get_frontmatter",
    "read_note",
    "rename_note",
    "set_frontmatter",
    "update_note",
    # Graph
    "build_link_graph",
    "find_broken_links",
    "find_orphans",
    "get_backlinks",
    "get_forward_links",
    "get_link_stats",
    # Search
    "filter_by_date",
    "filter_by_frontmatter",
    "filter_by_tag",
    "search_vault",
    # Canvas
    "add_canvas_edge",
    "add_canvas_node",
    "canvas_from_dict",
    "canvas_to_dict",
    "create_canvas",
    "parse_canvas",
    # MCP Tools
    "obsidian_create_note",
    "obsidian_delete_note",
    "obsidian_find_broken_links",
    "obsidian_get_backlinks",
    "obsidian_list_tags",
    "obsidian_load_vault",
    "obsidian_read_canvas",
    "obsidian_read_note",
    "obsidian_search",
    "obsidian_update_note",
    "obsidian_vault_stats",
    # CLI
    "cli_commands",
]

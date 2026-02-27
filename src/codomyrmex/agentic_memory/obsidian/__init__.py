"""Obsidian vault integration — parser, CRUD, graph, search, canvas, CLI.

Provides both filesystem-direct operations (no Obsidian app required) and
CLI-backed commands (requires Obsidian ≥1.12 with CLI enabled).

Quick usage::

    from codomyrmex.agentic_memory.obsidian import ObsidianVault, Note
    vault = ObsidianVault("/path/to/vault")
    note = vault.get_note("My Note")
"""

# ── filesystem models ────────────────────────────────────────────────

from codomyrmex.agentic_memory.obsidian.models import (
    Callout,
    Canvas,
    CanvasEdge,
    CanvasNode,
    CodeBlock,
    DataviewField,
    Embed,
    MathBlock,
    Note,
    SearchResult,
    Tag,
    VaultMetadata,
    Wikilink,
)

# ── filesystem core ──────────────────────────────────────────────────

from codomyrmex.agentic_memory.obsidian.vault import ObsidianVault

from codomyrmex.agentic_memory.obsidian.parser import (
    extract_callouts,
    extract_code_blocks,
    extract_dataview_fields,
    extract_embeds,
    extract_headings,
    extract_math,
    extract_tags,
    extract_wikilinks,
    parse_frontmatter,
    parse_note,
    serialize_note,
)

from codomyrmex.agentic_memory.obsidian.crud import (
    append_note,
    create_note,
    delete_note,
    get_frontmatter,
    move_note,
    prepend_note,
    read_note,
    read_note_raw,
    remove_frontmatter_key,
    rename_note,
    set_frontmatter,
    update_note,
)

from codomyrmex.agentic_memory.obsidian.graph import (
    build_link_graph,
    find_broken_links,
    find_dead_ends,
    find_hubs,
    find_orphans,
    get_backlinks,
    get_forward_links,
    get_link_stats,
    get_shortest_path,
)

from codomyrmex.agentic_memory.obsidian.search import (
    filter_by_date,
    filter_by_frontmatter,
    filter_by_frontmatter_exists,
    filter_by_tag,
    filter_by_tags,
    find_notes_linking_to,
    find_notes_with_embeds,
    search_regex,
    search_vault,
)

from codomyrmex.agentic_memory.obsidian.canvas import (
    add_canvas_edge,
    add_canvas_node,
    canvas_from_dict,
    canvas_to_dict,
    connect_nodes,
    create_canvas,
    create_file_node,
    create_link_node,
    create_text_node,
    parse_canvas,
    remove_canvas_edge,
    remove_canvas_node,
    save_canvas,
)

# ── CLI infrastructure ───────────────────────────────────────────────

from codomyrmex.agentic_memory.obsidian.cli import (
    CLIResult,
    ObsidianCLI,
    ObsidianCLIError,
    ObsidianCLINotAvailable,
)

# ── CLI domain models ────────────────────────────────────────────────

from codomyrmex.agentic_memory.obsidian.bookmarks import BookmarkItem
from codomyrmex.agentic_memory.obsidian.commands import (
    DiffResult,
    HistoryEntry,
    OutlineItem,
    WordCount,
)
from codomyrmex.agentic_memory.obsidian.developer import ConsoleEntry
from codomyrmex.agentic_memory.obsidian.plugins import (
    PluginInfo,
    SnippetInfo,
    ThemeInfo,
)
from codomyrmex.agentic_memory.obsidian.properties import PropertyValue
from codomyrmex.agentic_memory.obsidian.sync import (
    PublishStatus,
    SyncHistoryEntry,
    SyncStatus,
)
from codomyrmex.agentic_memory.obsidian.tasks import TaskItem
from codomyrmex.agentic_memory.obsidian.templates import TemplateInfo

__all__ = [
    # Filesystem models
    "Callout",
    "Canvas",
    "CanvasEdge",
    "CanvasNode",
    "CodeBlock",
    "DataviewField",
    "Embed",
    "MathBlock",
    "Note",
    "SearchResult",
    "Tag",
    "VaultMetadata",
    "Wikilink",
    # Vault
    "ObsidianVault",
    # Parser
    "extract_callouts",
    "extract_code_blocks",
    "extract_dataview_fields",
    "extract_embeds",
    "extract_headings",
    "extract_math",
    "extract_tags",
    "extract_wikilinks",
    "parse_frontmatter",
    "parse_note",
    "serialize_note",
    # CRUD
    "append_note",
    "create_note",
    "delete_note",
    "get_frontmatter",
    "move_note",
    "prepend_note",
    "read_note",
    "read_note_raw",
    "remove_frontmatter_key",
    "rename_note",
    "set_frontmatter",
    "update_note",
    # Graph
    "build_link_graph",
    "find_broken_links",
    "find_dead_ends",
    "find_hubs",
    "find_orphans",
    "get_backlinks",
    "get_forward_links",
    "get_link_stats",
    "get_shortest_path",
    # Search
    "filter_by_date",
    "filter_by_frontmatter",
    "filter_by_frontmatter_exists",
    "filter_by_tag",
    "filter_by_tags",
    "find_notes_linking_to",
    "find_notes_with_embeds",
    "search_regex",
    "search_vault",
    # Canvas
    "add_canvas_edge",
    "add_canvas_node",
    "canvas_from_dict",
    "canvas_to_dict",
    "connect_nodes",
    "create_canvas",
    "create_file_node",
    "create_link_node",
    "create_text_node",
    "parse_canvas",
    "remove_canvas_edge",
    "remove_canvas_node",
    "save_canvas",
    # CLI core
    "CLIResult",
    "ObsidianCLI",
    "ObsidianCLIError",
    "ObsidianCLINotAvailable",
    # CLI domain models
    "BookmarkItem",
    "ConsoleEntry",
    "DiffResult",
    "HistoryEntry",
    "OutlineItem",
    "PluginInfo",
    "PropertyValue",
    "PublishStatus",
    "SnippetInfo",
    "SyncHistoryEntry",
    "SyncStatus",
    "TaskItem",
    "TemplateInfo",
    "ThemeInfo",
    "WordCount",
]

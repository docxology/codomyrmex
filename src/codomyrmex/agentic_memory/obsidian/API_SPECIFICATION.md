# Obsidian Vault Module — API Specification

**Version**: v0.1.7 | **Last Updated**: February 2026

## Module: `models.py`

All models are `@dataclass` (frozen where noted).

```python
@dataclass
class WikiLink:
    target: str
    alias: str = ""
    anchor: str = ""

@dataclass
class Embed:
    target: str
    anchor: str = ""

@dataclass
class Callout:
    type: str
    title: str = ""
    content: str = ""

@dataclass
class Tag:
    name: str
    source: str  # "inline" | "frontmatter"

@dataclass
class Note:
    path: str
    title: str
    frontmatter: dict
    content: str
    wikilinks: list[WikiLink]
    embeds: list[Embed]
    callouts: list[Callout]
    tags: list[Tag]
    headings: list[tuple[int, str]]

@dataclass
class SearchResult:
    note: Note
    context: str
    score: float = 1.0

@dataclass
class VaultMetadata:
    vault_path: str
    note_count: int
    tag_index: dict[str, list[str]]
    link_index: dict[str, list[str]]
    last_indexed: datetime

@dataclass
class CanvasNode:
    id: str
    type: str          # "text" | "file" | "link" | "group"
    x: int
    y: int
    width: int
    height: int
    label: str = ""
    file: str = ""     # for type="file"
    url: str = ""      # for type="link"
    color: str = ""

@dataclass
class CanvasEdge:
    id: str
    from_node: str
    to_node: str
    label: str = ""

@dataclass
class Canvas:
    nodes: list[CanvasNode]
    edges: list[CanvasEdge]
```

---

## Module: `parser.py`

### `ObsidianParser`

```python
class ObsidianParser:
    def parse_file(self, path: str | Path) -> Note:
        """Parse an Obsidian markdown file into a Note dataclass."""

    def parse_frontmatter(self, text: str) -> dict:
        """Extract and parse YAML frontmatter from markdown text.
        Returns empty dict if no frontmatter block found."""

    def parse_wikilinks(self, text: str) -> list[WikiLink]:
        """Extract all [[wikilinks]] from text, excluding embeds."""

    def parse_embeds(self, text: str) -> list[Embed]:
        """Extract all ![[embeds]] from text."""

    def parse_callouts(self, text: str) -> list[Callout]:
        """Extract all > [!type] callout blocks."""

    def parse_tags(self, text: str, frontmatter: dict = None) -> list[Tag]:
        """Extract inline #tags and frontmatter tags list."""

    def parse_headings(self, text: str) -> list[tuple[int, str]]:
        """Return list of (level, heading_text) tuples."""
```

---

## Module: `vault.py`

### `ObsidianVault`

```python
class ObsidianVault:
    def load(self, vault_path: str | Path) -> None:
        """Scan vault_path recursively for *.md files, parse each, build indexes.
        Skips .obsidian/ and .trash/ directories."""

    def reload(self) -> None:
        """Re-scan and re-index the vault (clears existing index)."""

    def get_note(self, title_or_path: str) -> Note | None:
        """Look up a note by title (stem) or relative path.
        Returns None if not found."""

    def list_notes(self) -> list[Note]:
        """Return all indexed notes in undefined order."""

    def get_metadata(self) -> VaultMetadata:
        """Return vault-level statistics."""
```

---

## Module: `crud.py`

```python
def create_note(
    vault: ObsidianVault,
    path: str,
    content: str,
    frontmatter: dict = None,
) -> Note:
    """Create a new note at path (relative to vault root).
    Raises NoteExistsError if file already exists.
    Returns the parsed Note."""

def read_note(vault: ObsidianVault, path: str) -> Note:
    """Read and parse a note. Raises NoteNotFoundError if missing."""

def update_note(
    vault: ObsidianVault,
    path: str,
    content: str,
    preserve_frontmatter: bool = True,
) -> Note:
    """Overwrite note body. If preserve_frontmatter=True (default),
    existing frontmatter is retained. Returns updated Note."""

def delete_note(vault: ObsidianVault, path: str) -> None:
    """Delete note file and remove from vault index.
    Raises NoteNotFoundError if missing."""

def rename_note(
    vault: ObsidianVault,
    old_path: str,
    new_path: str,
    update_backlinks: bool = True,
) -> Note:
    """Rename note file. If update_backlinks=True (default), rewrites
    all WikiLink targets across the vault. Returns updated Note."""

def update_frontmatter(
    vault: ObsidianVault,
    path: str,
    updates: dict,
) -> Note:
    """Merge updates into existing frontmatter (shallow merge).
    Preserves unknown keys. Returns updated Note."""
```

---

## Module: `graph.py`

### `LinkGraph`

```python
class LinkGraph:
    def build(self, vault: ObsidianVault) -> None:
        """Construct a directed NetworkX graph from vault note links.
        Nodes: note titles. Edges: WikiLink source -> target."""

    def backlinks(self, note_title: str) -> list[str]:
        """Return titles of notes that link TO note_title."""

    def forward_links(self, note_title: str) -> list[str]:
        """Return titles of notes that note_title links TO."""

    def orphans(self) -> list[str]:
        """Return titles of notes with in-degree == 0 and out-degree == 0."""

    def broken_links(self) -> list[tuple[str, str]]:
        """Return list of (source_title, target_title) for WikiLinks
        where target_title has no corresponding Note in the vault."""
```

---

## Module: `search.py`

```python
def search_fulltext(
    vault: ObsidianVault,
    query: str,
    limit: int = 20,
    case_sensitive: bool = False,
) -> list[SearchResult]:
    """Case-insensitive substring search across note title and content.
    Returns up to limit results sorted by relevance score."""

def search_by_tag(
    vault: ObsidianVault,
    tag: str,
    case_sensitive: bool = False,
) -> list[Note]:
    """Return all notes that have the given tag (inline or frontmatter)."""

def search_by_frontmatter(
    vault: ObsidianVault,
    key: str,
    value: Any = None,
) -> list[Note]:
    """Return notes where frontmatter[key] exists.
    If value is provided, also filter for equality."""

def search_by_date(
    vault: ObsidianVault,
    field: str,
    start: date | str | None = None,
    end: date | str | None = None,
) -> list[Note]:
    """Filter notes by a date frontmatter field within [start, end] inclusive.
    Dates are parsed with dateutil.parser.parse."""
```

---

## Module: `canvas.py`

### `CanvasParser`

```python
class CanvasParser:
    def load(self, path: str | Path) -> Canvas:
        """Parse a .canvas JSON file into a Canvas dataclass."""

    def save(self, canvas: Canvas, path: str | Path) -> None:
        """Serialize Canvas to JSON and write to path (indent=2)."""

    def add_node(self, canvas: Canvas, node: CanvasNode) -> Canvas:
        """Return a new Canvas with node appended (immutable update)."""

    def add_edge(self, canvas: Canvas, edge: CanvasEdge) -> Canvas:
        """Return a new Canvas with edge appended (immutable update)."""
```

---

## Exceptions

```python
class ObsidianError(Exception): ...
class NoteNotFoundError(ObsidianError): ...   # note path does not exist
class NoteExistsError(ObsidianError): ...     # create collision
class VaultNotLoadedError(ObsidianError): ... # vault.load() not called
```

## Navigation

- [README](README.md) | [SPEC](SPEC.md) | [MCP_TOOL_SPECIFICATION](MCP_TOOL_SPECIFICATION.md) | [PAI](PAI.md)

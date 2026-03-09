"""Comprehensive tests for agentic_memory.obsidian.models — zero-mock.

Covers: Wikilink, Embed, Tag, Callout, CodeBlock, MathBlock, DataviewField,
Note (with word_count and aliases properties), SearchResult, VaultMetadata,
CanvasNode, CanvasEdge, Canvas (with get_node/get_edge).
"""

import pytest

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


class TestWikilink:
    def test_basic(self):
        link = Wikilink(target="MyNote")
        assert link.target == "MyNote"
        assert link.alias is None

    def test_with_heading(self):
        link = Wikilink(target="Note", heading="Section 1")
        assert link.heading == "Section 1"

    def test_with_block(self):
        link = Wikilink(target="Note", block="abc123")
        assert link.block == "abc123"


class TestEmbed:
    def test_basic(self):
        embed = Embed(target="image.png")
        assert embed.width is None

    def test_with_dimensions(self):
        embed = Embed(target="photo.jpg", width=800, height=600)
        assert embed.width == 800


class TestTag:
    def test_default_source(self):
        tag = Tag(name="python")
        assert tag.source == "content"

    def test_frontmatter_source(self):
        tag = Tag(name="project", source="frontmatter")
        assert tag.source == "frontmatter"


class TestCallout:
    def test_basic(self):
        c = Callout(type="NOTE", title="Important")
        assert c.foldable is False

    def test_foldable(self):
        c = Callout(type="WARNING", foldable=True, default_open=True)
        assert c.foldable is True


class TestCodeBlock:
    def test_basic(self):
        cb = CodeBlock(language="python", content="print('hello')", line_start=10)
        assert cb.language == "python"


class TestMathBlock:
    def test_block(self):
        mb = MathBlock(content="E = mc^2", inline=False)
        assert not mb.inline

    def test_inline(self):
        mb = MathBlock(content="x^2", inline=True)
        assert mb.inline


class TestDataviewField:
    def test_basic(self):
        f = DataviewField(key="status", value="done", line=5)
        assert f.key == "status"


class TestNote:
    def test_create_note(self):
        note = Note(title="My Note")
        assert note.title == "My Note"
        assert note.links == []

    def test_word_count(self):
        note = Note(title="Test", content="This is a test note with seven words")
        assert note.word_count == 8

    def test_word_count_empty(self):
        note = Note(title="Empty")
        assert note.word_count == 0

    def test_aliases_from_list(self):
        note = Note(title="Test", frontmatter={"aliases": ["Alias1", "Alias2"]})
        assert note.aliases == ["Alias1", "Alias2"]

    def test_aliases_from_string(self):
        note = Note(title="Test", frontmatter={"aliases": "SingleAlias"})
        assert note.aliases == ["SingleAlias"]

    def test_aliases_missing(self):
        note = Note(title="Test", frontmatter={})
        assert note.aliases == []

    def test_note_with_links(self):
        note = Note(title="Linked", links=[Wikilink(target="A"), Wikilink(target="B")])
        assert len(note.links) == 2


class TestSearchResult:
    def test_basic(self):
        note = Note(title="Found")
        sr = SearchResult(note=note, score=0.95, match_type="title")
        assert sr.score == 0.95


class TestVaultMetadata:
    def test_defaults(self):
        vm = VaultMetadata()
        assert vm.note_count == 0

    def test_with_values(self):
        vm = VaultMetadata(note_count=100, tag_count=50, link_count=200)
        assert vm.note_count == 100


class TestCanvasNode:
    def test_create(self):
        node = CanvasNode(id="n1", type="text", text="Hello")
        assert node.id == "n1"
        assert node.width == 250

    def test_file_node(self):
        node = CanvasNode(id="n2", type="file", file="path/to/note.md")
        assert node.file == "path/to/note.md"


class TestCanvasEdge:
    def test_create(self):
        edge = CanvasEdge(id="e1", fromNode="n1", toNode="n2")
        assert edge.fromNode == "n1"

    def test_with_label(self):
        edge = CanvasEdge(id="e2", fromNode="a", toNode="b", label="links")
        assert edge.label == "links"


class TestCanvas:
    def test_empty(self):
        canvas = Canvas()
        assert canvas.nodes == []

    def test_get_node_found(self):
        node = CanvasNode(id="n1", type="text")
        canvas = Canvas(nodes=[node])
        assert canvas.get_node("n1") is node

    def test_get_node_not_found(self):
        canvas = Canvas()
        assert canvas.get_node("x") is None

    def test_get_edge_found(self):
        edge = CanvasEdge(id="e1", fromNode="a", toNode="b")
        canvas = Canvas(edges=[edge])
        assert canvas.get_edge("e1") is edge

    def test_get_edge_not_found(self):
        canvas = Canvas()
        assert canvas.get_edge("x") is None

    def test_full_canvas(self):
        nodes = [CanvasNode(id="n1", type="text"), CanvasNode(id="n2", type="text")]
        edges = [CanvasEdge(id="e1", fromNode="n1", toNode="n2")]
        canvas = Canvas(nodes=nodes, edges=edges)
        assert len(canvas.nodes) == 2
        assert len(canvas.edges) == 1

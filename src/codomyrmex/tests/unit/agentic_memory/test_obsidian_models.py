"""Tests for agentic_memory.obsidian.models."""

from pathlib import Path

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
        w = Wikilink(target="My Note")
        assert w.target == "My Note"
        assert w.alias is None
        assert w.heading is None
        assert w.block is None

    def test_with_alias(self):
        w = Wikilink(target="My Note", alias="Click here")
        assert w.alias == "Click here"

    def test_with_heading(self):
        w = Wikilink(target="My Note", heading="Section 1")
        assert w.heading == "Section 1"

    def test_with_block(self):
        w = Wikilink(target="My Note", block="abc123")
        assert w.block == "abc123"


class TestEmbed:
    def test_basic(self):
        e = Embed(target="image.png")
        assert e.target == "image.png"
        assert e.width is None
        assert e.height is None

    def test_with_dimensions(self):
        e = Embed(target="image.png", width=400, height=300)
        assert e.width == 400
        assert e.height == 300


class TestTag:
    def test_defaults(self):
        t = Tag(name="python")
        assert t.name == "python"
        assert t.source == "content"

    def test_frontmatter_source(self):
        t = Tag(name="python", source="frontmatter")
        assert t.source == "frontmatter"


class TestCallout:
    def test_defaults(self):
        c = Callout(type="info")
        assert c.type == "info"
        assert c.title == ""
        assert c.content == ""
        assert c.foldable is False
        assert c.default_open is False

    def test_full(self):
        c = Callout(
            type="warning",
            title="Be careful",
            content="This is dangerous",
            foldable=True,
            default_open=True,
        )
        assert c.title == "Be careful"
        assert c.foldable is True
        assert c.default_open is True


class TestCodeBlock:
    def test_defaults(self):
        cb = CodeBlock()
        assert cb.language == ""
        assert cb.content == ""
        assert cb.line_start == 0

    def test_with_values(self):
        cb = CodeBlock(language="python", content="print('hello')", line_start=5)
        assert cb.language == "python"
        assert cb.line_start == 5


class TestMathBlock:
    def test_defaults(self):
        m = MathBlock()
        assert m.content == ""
        assert m.inline is False

    def test_inline(self):
        m = MathBlock(content="E=mc^2", inline=True)
        assert m.inline is True


class TestDataviewField:
    def test_construction(self):
        df = DataviewField(key="status", value="done")
        assert df.key == "status"
        assert df.value == "done"
        assert df.line == 0

    def test_with_line(self):
        df = DataviewField(key="author", value="Alice", line=12)
        assert df.line == 12


class TestNote:
    def test_basic(self):
        n = Note(title="My Note")
        assert n.title == "My Note"
        assert n.path is None
        assert n.content == ""
        assert n.frontmatter == {}

    def test_word_count_empty(self):
        n = Note(title="t")
        assert n.word_count == 0

    def test_word_count_nonempty(self):
        n = Note(title="t", content="hello world foo")
        assert n.word_count == 3

    def test_word_count_with_extra_spaces(self):
        n = Note(title="t", content="  hello   world  ")
        # str.split() handles multiple spaces
        assert n.word_count == 2

    def test_aliases_empty_frontmatter(self):
        n = Note(title="t")
        assert n.aliases == []

    def test_aliases_list(self):
        n = Note(title="t", frontmatter={"aliases": ["A", "B"]})
        assert n.aliases == ["A", "B"]

    def test_aliases_string(self):
        n = Note(title="t", frontmatter={"aliases": "single"})
        assert n.aliases == ["single"]

    def test_aliases_non_list_non_string(self):
        n = Note(title="t", frontmatter={"aliases": 42})
        assert n.aliases == []

    def test_independent_default_lists(self):
        n1 = Note(title="a")
        n2 = Note(title="b")
        n1.links.append(Wikilink(target="x"))
        assert len(n2.links) == 0

    def test_with_path(self):
        p = Path("/vault/notes/test.md")
        n = Note(title="test", path=p)
        assert n.path == p


class TestSearchResult:
    def test_construction(self):
        note = Note(title="Result Note")
        sr = SearchResult(note=note, score=0.85, match_type="title", context="some context")
        assert sr.note.title == "Result Note"
        assert sr.score == 0.85
        assert sr.match_type == "title"

    def test_defaults(self):
        note = Note(title="t")
        sr = SearchResult(note=note)
        assert sr.score == 0.0
        assert sr.match_type == "content"
        assert sr.context == ""


class TestVaultMetadata:
    def test_defaults(self):
        vm = VaultMetadata()
        assert vm.note_count == 0
        assert vm.tag_count == 0
        assert vm.link_count == 0
        assert vm.total_words == 0
        assert vm.folder_count == 0

    def test_with_values(self):
        vm = VaultMetadata(note_count=100, tag_count=50, link_count=200, total_words=50000, folder_count=10)
        assert vm.note_count == 100
        assert vm.folder_count == 10


class TestCanvasNode:
    def test_required_fields(self):
        node = CanvasNode(id="n1", type="text")
        assert node.id == "n1"
        assert node.type == "text"

    def test_defaults(self):
        node = CanvasNode(id="n1", type="file")
        assert node.x == 0
        assert node.y == 0
        assert node.width == 250
        assert node.height == 140
        assert node.text is None
        assert node.file is None
        assert node.color is None

    def test_with_text(self):
        node = CanvasNode(id="n1", type="text", text="Hello world")
        assert node.text == "Hello world"


class TestCanvasEdge:
    def test_required_field(self):
        e = CanvasEdge(id="e1")
        assert e.id == "e1"
        assert e.fromNode == ""
        assert e.toNode == ""

    def test_with_nodes(self):
        e = CanvasEdge(id="e1", fromNode="n1", toNode="n2", label="connects")
        assert e.fromNode == "n1"
        assert e.toNode == "n2"
        assert e.label == "connects"


class TestCanvas:
    def test_empty_canvas(self):
        c = Canvas()
        assert c.nodes == []
        assert c.edges == []
        assert c.path is None

    def test_get_node_found(self):
        node = CanvasNode(id="n1", type="text")
        c = Canvas(nodes=[node])
        assert c.get_node("n1") is node

    def test_get_node_not_found(self):
        c = Canvas()
        assert c.get_node("missing") is None

    def test_get_edge_found(self):
        edge = CanvasEdge(id="e1", fromNode="n1", toNode="n2")
        c = Canvas(edges=[edge])
        assert c.get_edge("e1") is edge

    def test_get_edge_not_found(self):
        c = Canvas()
        assert c.get_edge("missing") is None

    def test_independent_default_lists(self):
        c1 = Canvas()
        c2 = Canvas()
        c1.nodes.append(CanvasNode(id="x", type="text"))
        assert len(c2.nodes) == 0

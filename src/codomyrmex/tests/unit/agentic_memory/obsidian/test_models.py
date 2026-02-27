"""Tests for agentic_memory.obsidian.models — pure Python, no filesystem."""

from pathlib import Path

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
    def test_minimal(self):
        w = Wikilink("SomeNote")
        assert w.target == "SomeNote"
        assert w.alias is None
        assert w.heading is None
        assert w.block is None

    def test_with_alias(self):
        w = Wikilink("Note", alias="Display")
        assert w.alias == "Display"

    def test_with_heading(self):
        w = Wikilink("Note", heading="Section")
        assert w.heading == "Section"

    def test_with_block(self):
        w = Wikilink("Note", block="^abc123")
        assert w.block == "^abc123"


class TestEmbed:
    def test_minimal(self):
        e = Embed("img.png")
        assert e.target == "img.png"
        assert e.width is None
        assert e.height is None

    def test_with_dimensions(self):
        e = Embed("img.png", width=400, height=300)
        assert e.width == 400
        assert e.height == 300

    def test_target_preserved(self):
        e = Embed("path/to/file.pdf")
        assert e.target == "path/to/file.pdf"


class TestTag:
    def test_default_source_is_content(self):
        t = Tag("project")
        assert t.source == "content"

    def test_frontmatter_source(self):
        t = Tag("draft", source="frontmatter")
        assert t.source == "frontmatter"

    def test_name_preserved(self):
        t = Tag("#project")
        assert t.name == "#project"


class TestCallout:
    def test_minimal(self):
        c = Callout("note")
        assert c.type == "note"
        assert c.title == ""
        assert c.content == ""
        assert c.foldable is False
        assert c.default_open is False

    def test_with_title_and_content(self):
        c = Callout("warning", title="Heads up", content="Be careful")
        assert c.title == "Heads up"
        assert c.content == "Be careful"

    def test_foldable(self):
        c = Callout("info", foldable=True)
        assert c.foldable is True

    def test_default_open(self):
        c = Callout("tip", default_open=True)
        assert c.default_open is True


class TestCodeBlock:
    def test_defaults(self):
        cb = CodeBlock()
        assert cb.language == ""
        assert cb.content == ""
        assert cb.line_start == 0

    def test_with_language(self):
        cb = CodeBlock(language="python")
        assert cb.language == "python"

    def test_with_line_position(self):
        cb = CodeBlock(line_start=42)
        assert cb.line_start == 42


class TestMathBlock:
    def test_default_not_inline(self):
        m = MathBlock()
        assert m.inline is False

    def test_inline_math(self):
        m = MathBlock(content="x^2", inline=True)
        assert m.inline is True

    def test_content_preserved(self):
        expr = r"\sum_{i=0}^n"
        m = MathBlock(content=expr)
        assert m.content == expr


class TestDataviewField:
    def test_required_fields(self):
        d = DataviewField(key="status", value="active")
        assert d.key == "status"
        assert d.value == "active"

    def test_default_line(self):
        d = DataviewField(key="k", value="v")
        assert d.line == 0

    def test_with_line(self):
        d = DataviewField("k", "v", line=15)
        assert d.line == 15


class TestNote:
    def test_minimal_title_only(self):
        n = Note(title="My Note")
        assert n.title == "My Note"
        assert n.links == []
        assert n.embeds == []
        assert n.tags == []
        assert n.headings == []
        assert n.callouts == []
        assert n.code_blocks == []
        assert n.math_blocks == []
        assert n.dataview_fields == []

    def test_word_count_empty_content(self):
        n = Note(title="T")
        assert n.word_count == 0

    def test_word_count_with_content(self):
        n = Note(title="T", content="hello world")
        assert n.word_count == 2

    def test_aliases_no_key(self):
        n = Note(title="T")
        assert n.aliases == []

    def test_aliases_list_value(self):
        n = Note(title="T", frontmatter={"aliases": ["a", "b"]})
        assert n.aliases == ["a", "b"]

    def test_aliases_string_value(self):
        n = Note(title="T", frontmatter={"aliases": "single"})
        assert n.aliases == ["single"]

    def test_aliases_non_string_non_list(self):
        n = Note(title="T", frontmatter={"aliases": 42})
        assert n.aliases == []

    def test_path_can_be_none(self):
        n = Note(title="T")
        assert n.path is None

    def test_path_can_be_path_object(self):
        p = Path("/vault/note.md")
        n = Note(title="T", path=p)
        assert n.path == p

    def test_frontmatter_mutable_per_instance(self):
        n1 = Note(title="A")
        n2 = Note(title="B")
        n1.frontmatter["key"] = "val"
        assert "key" not in n2.frontmatter

    def test_links_assigned(self):
        w = Wikilink("Target")
        n = Note(title="T", links=[w])
        assert n.links == [w]

    def test_tags_assigned(self):
        t = Tag("todo")
        n = Note(title="T", tags=[t])
        assert n.tags == [t]

    def test_headings_store_tuples(self):
        n = Note(title="T", headings=[(1, "Intro"), (2, "Body")])
        assert n.headings[0] == (1, "Intro")
        assert n.headings[1] == (2, "Body")


class TestSearchResult:
    def test_minimal(self):
        note = Note(title="T")
        r = SearchResult(note=note)
        assert r.score == 0.0
        assert r.match_type == "content"
        assert r.context == ""

    def test_score_preserved(self):
        note = Note(title="T")
        r = SearchResult(note=note, score=0.95)
        assert r.score == 0.95

    def test_match_type_variants(self):
        note = Note(title="T")
        for mt in ("title", "tag", "content"):
            r = SearchResult(note=note, match_type=mt)
            assert r.match_type == mt

    def test_note_same_object(self):
        note = Note(title="T")
        r = SearchResult(note=note)
        assert r.note is note


class TestVaultMetadata:
    def test_all_defaults_zero(self):
        v = VaultMetadata()
        assert v.note_count == 0
        assert v.tag_count == 0
        assert v.link_count == 0
        assert v.total_words == 0
        assert v.folder_count == 0

    def test_with_values(self):
        v = VaultMetadata(note_count=42, link_count=100)
        assert v.note_count == 42
        assert v.link_count == 100

    def test_all_five_fields_settable(self):
        v = VaultMetadata(
            note_count=1, tag_count=2, link_count=3, total_words=4, folder_count=5
        )
        assert v.note_count == 1
        assert v.tag_count == 2
        assert v.link_count == 3
        assert v.total_words == 4
        assert v.folder_count == 5


class TestCanvasNode:
    def test_required_fields(self):
        n = CanvasNode(id="n1", type="text")
        assert n.id == "n1"
        assert n.type == "text"

    def test_text_node(self):
        n = CanvasNode(id="n1", type="text", text="Hello")
        assert n.type == "text"
        assert n.text == "Hello"

    def test_file_node(self):
        n = CanvasNode(id="n2", type="file", file="path/note.md")
        assert n.type == "file"
        assert n.file == "path/note.md"

    def test_link_node(self):
        n = CanvasNode(id="n3", type="link", url="https://example.com")
        assert n.type == "link"
        assert n.url == "https://example.com"

    def test_default_dimensions(self):
        n = CanvasNode(id="n1", type="text")
        assert n.width == 250
        assert n.height == 140


class TestCanvasEdge:
    def test_required_id(self):
        e = CanvasEdge(id="e1")
        assert e.id == "e1"

    def test_from_to_nodes(self):
        e = CanvasEdge(id="e1", fromNode="n1", toNode="n2")
        assert e.fromNode == "n1"
        assert e.toNode == "n2"

    def test_optional_label(self):
        e = CanvasEdge("e1", label="causes")
        assert e.label == "causes"


class TestCanvas:
    def test_empty_canvas(self):
        c = Canvas()
        assert c.nodes == []
        assert c.edges == []

    def test_get_node_found(self):
        node = CanvasNode(id="n1", type="text", text="hello")
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

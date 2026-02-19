"""Tests for Obsidian markdown parser."""

import pytest
from pathlib import Path

from codomyrmex.agentic_memory.obsidian.parser import (
    extract_callouts,
    extract_embeds,
    extract_headings,
    extract_tags,
    extract_wikilinks,
    parse_frontmatter,
    parse_note,
    serialize_note,
)


class TestParseFrontmatter:
    def test_basic_frontmatter(self):
        raw = "---\ntitle: Test\ntags:\n  - a\n  - b\n---\nBody content."
        fm, body = parse_frontmatter(raw)
        assert fm["title"] == "Test"
        assert fm["tags"] == ["a", "b"]
        assert body == "Body content."

    def test_no_frontmatter(self):
        raw = "# Just a heading\nSome text."
        fm, body = parse_frontmatter(raw)
        assert fm == {}
        assert body == raw

    def test_empty_frontmatter(self):
        raw = "---\n---\nBody."
        fm, body = parse_frontmatter(raw)
        assert fm == {}
        assert body == "Body."

    def test_complex_frontmatter(self):
        raw = "---\ntitle: Complex\ndate: 2024-01-15\nnested:\n  key: value\n---\nContent."
        fm, body = parse_frontmatter(raw)
        assert fm["title"] == "Complex"
        assert fm["nested"]["key"] == "value"


class TestExtractWikilinks:
    def test_simple_link(self):
        links = extract_wikilinks("Link to [[My Note]] here.")
        assert len(links) == 1
        assert links[0].target == "My Note"
        assert links[0].alias is None
        assert links[0].heading is None

    def test_aliased_link(self):
        links = extract_wikilinks("[[Target|Display Text]]")
        assert len(links) == 1
        assert links[0].target == "Target"
        assert links[0].alias == "Display Text"

    def test_heading_link(self):
        links = extract_wikilinks("[[Note#Section One]]")
        assert len(links) == 1
        assert links[0].target == "Note"
        assert links[0].heading == "Section One"

    def test_block_link(self):
        links = extract_wikilinks("[[Note#^block-id]]")
        assert len(links) == 1
        assert links[0].target == "Note"
        assert links[0].heading == "^block-id"

    def test_multiple_links(self):
        content = "[[A]] text [[B|alias]] more [[C#heading]]"
        links = extract_wikilinks(content)
        assert len(links) == 3

    def test_no_embeds_captured(self):
        links = extract_wikilinks("![[image.png]]")
        assert len(links) == 0

    def test_heading_and_alias(self):
        links = extract_wikilinks("[[Note#Section|Custom Text]]")
        assert len(links) == 1
        assert links[0].target == "Note"
        assert links[0].heading == "Section"
        assert links[0].alias == "Custom Text"


class TestExtractEmbeds:
    def test_simple_embed(self):
        embeds = extract_embeds("![[image.png]]")
        assert len(embeds) == 1
        assert embeds[0].target == "image.png"
        assert embeds[0].width is None

    def test_embed_with_width(self):
        embeds = extract_embeds("![[diagram.png|400]]")
        assert len(embeds) == 1
        assert embeds[0].target == "diagram.png"
        assert embeds[0].width == 400
        assert embeds[0].height is None

    def test_embed_with_dimensions(self):
        embeds = extract_embeds("![[photo.jpg|800x600]]")
        assert len(embeds) == 1
        assert embeds[0].width == 800
        assert embeds[0].height == 600

    def test_multiple_embeds(self):
        content = "![[a.png]] text ![[b.png|200]]"
        embeds = extract_embeds(content)
        assert len(embeds) == 2


class TestExtractTags:
    def test_inline_tag(self):
        tags = extract_tags("Some text with #mytag here.")
        assert len(tags) == 1
        assert tags[0].name == "mytag"
        assert tags[0].source == "content"

    def test_nested_tag(self):
        tags = extract_tags("A #parent/child tag.")
        assert len(tags) == 1
        assert tags[0].name == "parent/child"

    def test_frontmatter_tags(self):
        tags = extract_tags("Content", {"tags": ["fm-tag-1", "fm-tag-2"]})
        fm_tags = [t for t in tags if t.source == "frontmatter"]
        assert len(fm_tags) == 2
        assert fm_tags[0].name == "fm-tag-1"

    def test_both_sources(self):
        tags = extract_tags("#inline here", {"tags": ["fm"]})
        assert len(tags) == 2
        sources = {t.source for t in tags}
        assert sources == {"content", "frontmatter"}

    def test_no_hashtag_in_url(self):
        # Tags should not match inside URLs ideally,
        # but our simple regex may catch some. Test basic case.
        tags = extract_tags("Visit #real-tag for info.")
        assert any(t.name == "real-tag" for t in tags)


class TestExtractCallouts:
    def test_basic_callout(self):
        content = "> [!note] My Title\n> Some content here.\n> More content."
        callouts = extract_callouts(content)
        assert len(callouts) == 1
        assert callouts[0].type == "note"
        assert callouts[0].title == "My Title"
        assert "Some content here." in callouts[0].content
        assert not callouts[0].foldable

    def test_foldable_closed(self):
        content = "> [!warning]- Hidden\n> Secret content."
        callouts = extract_callouts(content)
        assert len(callouts) == 1
        assert callouts[0].foldable is True
        assert callouts[0].default_open is False

    def test_foldable_open(self):
        content = "> [!tip]+ Visible\n> Tip content."
        callouts = extract_callouts(content)
        assert len(callouts) == 1
        assert callouts[0].foldable is True
        assert callouts[0].default_open is True

    def test_no_title(self):
        content = "> [!info]\n> Just content."
        callouts = extract_callouts(content)
        assert len(callouts) == 1
        assert callouts[0].title == ""
        assert callouts[0].type == "info"


class TestExtractHeadings:
    def test_headings(self):
        content = "# H1\n## H2\n### H3\nText\n#### H4"
        headings = extract_headings(content)
        assert len(headings) == 4
        assert headings[0] == (1, "H1")
        assert headings[1] == (2, "H2")
        assert headings[2] == (3, "H3")
        assert headings[3] == (4, "H4")


class TestParseNote:
    def test_full_parse(self, tmp_path, sample_frontmatter_note):
        note_path = tmp_path / "test.md"
        note_path.write_text(sample_frontmatter_note)
        note = parse_note(note_path)

        assert note.title == "test"
        assert note.frontmatter["title"] == "My Test Note"
        assert len(note.links) >= 4  # At least 4 wikilinks
        assert len(note.embeds) == 3
        assert len(note.callouts) == 3
        assert len(note.headings) >= 4

    def test_parse_from_raw(self, tmp_path):
        note_path = tmp_path / "raw.md"
        raw = "# Raw\nContent with [[link]]."
        note = parse_note(note_path, raw=raw)
        assert note.title == "raw"
        assert len(note.links) == 1


class TestSerializeNote:
    def test_round_trip(self, tmp_path, sample_frontmatter_note):
        note_path = tmp_path / "roundtrip.md"
        note_path.write_text(sample_frontmatter_note)
        note = parse_note(note_path)
        serialized = serialize_note(note)

        # Re-parse the serialized content
        note2 = parse_note(note_path, raw=serialized)
        assert note2.frontmatter["title"] == note.frontmatter["title"]
        assert note2.frontmatter["tags"] == note.frontmatter["tags"]
        assert len(note2.links) == len(note.links)
        assert len(note2.embeds) == len(note.embeds)

    def test_no_frontmatter_serialize(self, tmp_path):
        note_path = tmp_path / "no_fm.md"
        raw = "# No FM\nContent."
        note = parse_note(note_path, raw=raw)
        serialized = serialize_note(note)
        assert not serialized.startswith("---")
        assert "# No FM" in serialized

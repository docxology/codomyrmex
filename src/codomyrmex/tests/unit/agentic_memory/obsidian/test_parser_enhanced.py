"""Tests for Obsidian parser — enhanced features.

Tests for code block extraction, math extraction, Dataview field
parsing, block reference handling, and comma-separated tags.
"""

from codomyrmex.agentic_memory.obsidian.parser import (
    extract_code_blocks,
    extract_dataview_fields,
    extract_math,
    extract_tags,
    extract_wikilinks,
    parse_note,
)


class TestExtractCodeBlocks:
    def test_single_block(self):
        content = "text\n```python\ndef hello():\n    pass\n```\nmore"
        blocks = extract_code_blocks(content)
        assert len(blocks) == 1
        assert blocks[0].language == "python"
        assert "def hello" in blocks[0].content

    def test_multiple_blocks(self):
        content = "```js\nconst x = 1;\n```\ntext\n```css\n.cls { }\n```\n"
        blocks = extract_code_blocks(content)
        assert len(blocks) == 2
        assert blocks[0].language == "js"
        assert blocks[1].language == "css"

    def test_no_language(self):
        content = "```\nplain code\n```\n"
        blocks = extract_code_blocks(content)
        assert len(blocks) == 1
        assert blocks[0].language == ""

    def test_line_start(self):
        content = "line1\nline2\n```py\ncode\n```\n"
        blocks = extract_code_blocks(content)
        assert blocks[0].line_start == 3  # starts on line 3


class TestExtractMath:
    def test_display_math(self):
        content = "Text $$E = mc^2$$ more."
        blocks = extract_math(content)
        display = [b for b in blocks if not b.inline]
        assert len(display) == 1
        assert display[0].content == "E = mc^2"

    def test_inline_math(self):
        content = "Inline $x + y$ equation."
        blocks = extract_math(content)
        inline = [b for b in blocks if b.inline]
        assert len(inline) == 1
        assert inline[0].content == "x + y"

    def test_multiline_display(self):
        content = "$$\na + b\n= c\n$$\n"
        blocks = extract_math(content)
        assert len(blocks) >= 1
        assert "a + b" in blocks[0].content


class TestExtractDataviewFields:
    def test_basic_field(self):
        content = "Due:: 2024-01-15\nPriority:: High"
        fields = extract_dataview_fields(content)
        assert len(fields) == 2
        assert fields[0].key == "Due"
        assert fields[0].value == "2024-01-15"
        assert fields[1].key == "Priority"

    def test_line_numbers(self):
        content = "Line 1\nStatus:: Active\nLine 3"
        fields = extract_dataview_fields(content)
        assert fields[0].line == 2

    def test_no_false_positives(self):
        content = "Normal text: not a field\nAlso not:: but this is"
        fields = extract_dataview_fields(content)
        # Only "Also not:: but this is" should match if the key is alphanumeric
        # "Also" starts with alpha but has a space, depends on regex
        assert len(fields) == 0  # "Also not" has a space so it won't match


class TestExtractWikilinksEnhanced:
    def test_block_ref(self):
        links = extract_wikilinks("See [[Note#^abc123]]")
        assert links[0].block == "abc123"
        assert links[0].heading is None

    def test_heading_vs_block(self):
        content = "[[A#heading]] and [[B#^block]]"
        links = extract_wikilinks(content)
        assert links[0].heading == "heading"
        assert links[0].block is None
        assert links[1].heading is None
        assert links[1].block == "block"


class TestExtractTagsEnhanced:
    def test_comma_separated_frontmatter_tags(self):
        tags = extract_tags("content", {"tags": "alpha, beta, gamma"})
        fm_tags = [t for t in tags if t.source == "frontmatter"]
        assert len(fm_tags) == 3
        assert fm_tags[0].name == "alpha"
        assert fm_tags[1].name == "beta"


class TestParseNoteEnhanced:
    def test_full_parse_with_new_features(self, tmp_path, sample_frontmatter_note):
        note_path = tmp_path / "enhanced.md"
        note_path.write_text(sample_frontmatter_note)
        note = parse_note(note_path)

        assert len(note.code_blocks) >= 2  # python + javascript blocks
        assert len(note.math_blocks) >= 2  # display + inline
        assert len(note.dataview_fields) >= 3  # Due, Priority, Category
        assert note.word_count > 0
        assert "Test Note" in note.aliases

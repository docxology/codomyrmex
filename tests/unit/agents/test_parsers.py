"""Tests for agent output parsers: JSON extraction, code blocks, structured output, clean_response."""

import pytest

from codomyrmex.agents.core.parsers import (
    CodeBlock,
    ParseResult,
    clean_response,
    extract_between,
    parse_code_blocks,
    parse_first_code_block,
    parse_json_response,
    parse_key_value_pairs,
    parse_structured_output,
    split_on_pattern,
)


# ── parse_json_response ──────────────────────────────────────────────────


class TestParseJsonResponse:
    def test_pure_json(self):
        result = parse_json_response('{"key": "value"}')
        assert result.success
        assert result.data == {"key": "value"}

    def test_json_in_markdown(self):
        text = 'Here:\n```json\n{"a": 1}\n```\nDone.'
        result = parse_json_response(text)
        assert result.success
        assert result.data == {"a": 1}

    def test_json_array(self):
        result = parse_json_response("[1, 2, 3]")
        assert result.success
        assert result.data == [1, 2, 3]

    def test_no_json_strict(self):
        result = parse_json_response("just plain text", strict=True)
        assert not result.success

    def test_empty_input(self):
        result = parse_json_response("")
        assert not result.success


# ── parse_code_blocks ─────────────────────────────────────────────────────


class TestParseCodeBlocks:
    def test_single_block(self):
        text = "Some text\n```python\nprint('hi')\n```\nMore text"
        blocks = parse_code_blocks(text)
        assert len(blocks) == 1
        assert blocks[0].language == "python"
        assert "print('hi')" in blocks[0].code

    def test_multiple_blocks(self):
        text = "```python\na = 1\n```\n\n```javascript\nlet b = 2;\n```"
        blocks = parse_code_blocks(text)
        assert len(blocks) == 2

    def test_filter_by_language(self):
        text = "```python\nx\n```\n```javascript\ny\n```"
        blocks = parse_code_blocks(text, language="python")
        assert len(blocks) == 1
        assert blocks[0].language == "python"

    def test_empty_input(self):
        assert parse_code_blocks("") == []
        assert parse_code_blocks(None) == []

    def test_code_block_str(self):
        cb = CodeBlock(language="py", code="x = 1")
        assert str(cb) == "x = 1"


# ── parse_first_code_block ────────────────────────────────────────────────


class TestParseFirstCodeBlock:
    def test_returns_first(self):
        text = "```python\nfirst\n```\n```python\nsecond\n```"
        block = parse_first_code_block(text)
        assert block is not None
        assert "first" in block.code

    def test_returns_none(self):
        assert parse_first_code_block("no code here") is None


# ── parse_structured_output ───────────────────────────────────────────────


class TestParseStructuredOutput:
    def test_extract_fields(self):
        text = "Name: Alice\nAge: 30\nCity: Wonderland"
        result = parse_structured_output(text, {
            "name": r"Name:\s*(.*)",
            "age": r"Age:\s*(\d+)",
        })
        assert result["name"] == "Alice"
        assert result["age"] == "30"

    def test_missing_field(self):
        result = parse_structured_output("hello", {"x": r"missing:\s*(.*)"})
        assert result["x"] is None


# ── extract_between ───────────────────────────────────────────────────────


class TestExtractBetween:
    def test_basic_extraction(self):
        text = "<start>content here<end>"
        assert extract_between(text, "<start>", "<end>") == "content here"

    def test_missing_markers(self):
        assert extract_between("nothing", "<a>", "<b>") is None


# ── parse_key_value_pairs ─────────────────────────────────────────────────


class TestParseKeyValuePairs:
    def test_colon_separated(self):
        text = "key1: val1\nkey2: val2"
        kv = parse_key_value_pairs(text)
        assert kv == {"key1": "val1", "key2": "val2"}

    def test_custom_separator(self):
        text = "a=1\nb=2"
        kv = parse_key_value_pairs(text, separator="=")
        assert kv == {"a": "1", "b": "2"}

    def test_skips_bad_lines(self):
        text = "good: yes\nbad line\nfine: ok"
        kv = parse_key_value_pairs(text)
        assert len(kv) == 2


# ── clean_response ────────────────────────────────────────────────────────


class TestCleanResponse:
    def test_strips_whitespace(self):
        assert clean_response("  hello  ") == "hello"

    def test_removes_multiple_blank_lines(self):
        text = "a\n\n\n\n\nb"
        cleaned = clean_response(text)
        assert "\n\n\n" not in cleaned

    def test_empty(self):
        assert clean_response("") == ""
        assert clean_response(None) == ""


# ── split_on_pattern ──────────────────────────────────────────────────────


class TestSplitOnPattern:
    def test_basic_split(self):
        text = "Section A\n## Header\nSection B"
        parts = split_on_pattern(text, r"## \w+")
        assert len(parts) >= 1


# ── ParseResult ───────────────────────────────────────────────────────────


class TestParseResult:
    def test_bool(self):
        assert bool(ParseResult(success=True))
        assert not bool(ParseResult(success=False))

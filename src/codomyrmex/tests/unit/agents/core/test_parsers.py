"""
Unit tests for agents.core.parsers — Zero-Mock compliant.

Covers: CodeBlock, ParseResult, parse_json_response, parse_code_blocks,
parse_first_code_block, parse_structured_output, extract_between,
parse_key_value_pairs, clean_response, split_on_pattern.
"""

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

# ── CodeBlock ──────────────────────────────────────────────────────────────


@pytest.mark.unit
class TestCodeBlock:
    def test_str_returns_code(self):
        block = CodeBlock(language="python", code="x = 1")
        assert str(block) == "x = 1"

    def test_fields(self):
        block = CodeBlock(language="js", code="console.log(1)", start_line=5, end_line=7)
        assert block.language == "js"
        assert block.start_line == 5
        assert block.end_line == 7


# ── ParseResult ───────────────────────────────────────────────────────────


@pytest.mark.unit
class TestParseResult:
    def test_bool_true_on_success(self):
        r = ParseResult(success=True, data={"key": "val"})
        assert bool(r) is True

    def test_bool_false_on_failure(self):
        r = ParseResult(success=False, error="oops")
        assert bool(r) is False

    def test_defaults(self):
        r = ParseResult(success=True)
        assert r.data is None
        assert r.error is None
        assert r.raw_text == ""


# ── parse_json_response ───────────────────────────────────────────────────


@pytest.mark.unit
class TestParseJsonResponse:
    def test_pure_json_object(self):
        result = parse_json_response('{"key": "value"}')
        assert result.success is True
        assert result.data["key"] == "value"

    def test_pure_json_array(self):
        result = parse_json_response("[1, 2, 3]")
        assert result.success is True
        assert result.data == [1, 2, 3]

    def test_json_in_markdown_block(self):
        text = '```json\n{"a": 1}\n```'
        result = parse_json_response(text)
        assert result.success is True
        assert result.data["a"] == 1

    def test_json_in_plain_code_block(self):
        text = '```\n{"b": 2}\n```'
        result = parse_json_response(text)
        assert result.success is True
        assert result.data["b"] == 2

    def test_json_embedded_in_text(self):
        text = 'Here is the result: {"status": "ok"} done'
        result = parse_json_response(text)
        assert result.success is True
        assert result.data["status"] == "ok"

    def test_empty_input_fails(self):
        result = parse_json_response("")
        assert result.success is False
        assert result.error is not None

    def test_no_json_in_text(self):
        result = parse_json_response("just plain text")
        assert result.success is False

    def test_strict_mode_fails_on_no_json(self):
        result = parse_json_response("no json here", strict=True)
        assert result.success is False
        assert result.error == "No valid JSON found"

    def test_whitespace_only_fails(self):
        result = parse_json_response("   ")
        assert result.success is False


# ── parse_code_blocks ─────────────────────────────────────────────────────


@pytest.mark.unit
class TestParseCodeBlocks:
    def test_empty_text_returns_empty(self):
        assert parse_code_blocks("") == []

    def test_single_block(self):
        text = "```python\nx = 1\n```"
        blocks = parse_code_blocks(text)
        assert len(blocks) == 1
        assert blocks[0].language == "python"
        assert blocks[0].code == "x = 1"

    def test_multiple_blocks(self):
        text = "```python\nx = 1\n```\n\n```js\nconsole.log(1)\n```"
        blocks = parse_code_blocks(text)
        assert len(blocks) == 2

    def test_filter_by_language(self):
        text = "```python\npy_code\n```\n```js\njs_code\n```"
        blocks = parse_code_blocks(text, language="python")
        assert len(blocks) == 1
        assert blocks[0].language == "python"

    def test_no_language_tag(self):
        text = "```\nsome code\n```"
        blocks = parse_code_blocks(text)
        assert len(blocks) == 1
        assert blocks[0].language == "text"

    def test_line_numbers_calculated(self):
        text = "intro\n```python\ncode\n```"
        blocks = parse_code_blocks(text)
        assert blocks[0].start_line > 0

    def test_case_insensitive_language_filter(self):
        text = "```Python\nx = 1\n```"
        blocks = parse_code_blocks(text, language="python")
        assert len(blocks) == 1


# ── parse_first_code_block ─────────────────────────────────────────────────


@pytest.mark.unit
class TestParseFirstCodeBlock:
    def test_returns_first_block(self):
        text = "```python\nfirst\n```\n```js\nsecond\n```"
        block = parse_first_code_block(text)
        assert block is not None
        assert block.code == "first"

    def test_returns_none_when_no_blocks(self):
        assert parse_first_code_block("no code here") is None

    def test_filtered_by_language(self):
        text = "```python\npy\n```\n```js\njs\n```"
        block = parse_first_code_block(text, language="js")
        assert block is not None
        assert block.code == "js"


# ── parse_structured_output ────────────────────────────────────────────────


@pytest.mark.unit
class TestParseStructuredOutput:
    def test_single_pattern_match(self):
        text = "Status: active\nUser: alice"
        result = parse_structured_output(text, {"status": r"Status:\s*(.*)"})
        assert result["status"] == "active"

    def test_missing_field_returns_none(self):
        text = "only some text"
        result = parse_structured_output(text, {"missing": r"Missing:\s*(.*)"})
        assert result["missing"] is None

    def test_multiple_patterns(self):
        text = "Name: Bob\nAge: 30"
        result = parse_structured_output(
            text, {"name": r"Name:\s*(.*)", "age": r"Age:\s*(.*)"}
        )
        assert result["name"] == "Bob"
        assert result["age"] == "30"

    def test_empty_patterns(self):
        result = parse_structured_output("some text", {})
        assert result == {}


# ── extract_between ────────────────────────────────────────────────────────


@pytest.mark.unit
class TestExtractBetween:
    def test_basic_extraction(self):
        result = extract_between("hello [world] there", "[", "]")
        assert result == "world"

    def test_no_start_marker(self):
        assert extract_between("hello world", "[", "]") is None

    def test_no_end_marker(self):
        assert extract_between("hello [world", "[", "]") is None

    def test_empty_content_between(self):
        result = extract_between("hello [] there", "[", "]")
        assert result == ""

    def test_multichar_markers(self):
        result = extract_between("prefix<START>content<END>suffix", "<START>", "<END>")
        assert result == "content"


# ── parse_key_value_pairs ──────────────────────────────────────────────────


@pytest.mark.unit
class TestParseKeyValuePairs:
    def test_basic_pairs(self):
        text = "name: Alice\nage: 30"
        result = parse_key_value_pairs(text)
        assert result["name"] == "Alice"
        assert result["age"] == "30"

    def test_custom_separator(self):
        text = "name=Bob\nrole=admin"
        result = parse_key_value_pairs(text, separator="=")
        assert result["name"] == "Bob"
        assert result["role"] == "admin"

    def test_line_without_separator_skipped(self):
        text = "no separator here\nkey: value"
        result = parse_key_value_pairs(text)
        assert "no separator here" not in result
        assert result["key"] == "value"

    def test_empty_text(self):
        assert parse_key_value_pairs("") == {}

    def test_value_with_separator_in_it(self):
        text = "url: http://example.com:8080"
        result = parse_key_value_pairs(text)
        assert result["url"] == "http://example.com:8080"

    def test_empty_key_skipped(self):
        text = ": no key"
        result = parse_key_value_pairs(text)
        # Empty key should be skipped
        assert "" not in result


# ── clean_response ─────────────────────────────────────────────────────────


@pytest.mark.unit
class TestCleanResponse:
    def test_empty_returns_empty(self):
        assert clean_response("") == ""

    def test_strips_whitespace(self):
        assert clean_response("  hello  ") == "hello"

    def test_removes_triple_blank_lines(self):
        text = "a\n\n\n\nb"
        result = clean_response(text)
        assert "\n\n\n" not in result
        assert "a" in result
        assert "b" in result

    def test_strips_sure_prefix(self):
        text = "Sure, here is the code: x = 1"
        result = clean_response(text)
        assert not result.startswith("Sure")

    def test_strips_certainly_prefix(self):
        text = "Certainly! Here you go."
        result = clean_response(text)
        assert not result.startswith("Certainly")

    def test_strips_of_course_prefix(self):
        text = "Of course! Let me help."
        result = clean_response(text)
        assert not result.startswith("Of course")

    def test_preserves_normal_content(self):
        text = "This is a normal sentence without prefixes."
        result = clean_response(text)
        assert "normal sentence" in result


# ── split_on_pattern ──────────────────────────────────────────────────────


@pytest.mark.unit
class TestSplitOnPattern:
    def test_split_on_word(self):
        result = split_on_pattern("hello SPLIT world SPLIT again", "SPLIT")
        assert len(result) >= 2

    def test_no_match_returns_full(self):
        result = split_on_pattern("no match here", "NOTFOUND")
        assert len(result) == 1
        assert "no match here" in result[0]

    def test_empty_chunks_excluded(self):
        result = split_on_pattern("SPLIT content SPLIT", "SPLIT")
        # Only non-empty chunks returned
        for chunk in result:
            assert chunk.strip()

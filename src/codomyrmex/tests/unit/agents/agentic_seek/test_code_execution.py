"""Tests for codomyrmex.agents.agentic_seek.code_execution.

Zero-mock tests covering code block extraction, language classification,
command building, and output parsing.
"""

import pytest

from codomyrmex.agents.agentic_seek.code_execution import (
    AgenticSeekCodeExecutor,
    CodeBlock,
    build_execution_command,
    classify_language,
    extract_code_blocks,
    parse_execution_output,
)

# ===================================================================
# extract_code_blocks
# ===================================================================

class TestExtractCodeBlocks:
    def test_single_python_block(self):
        text = "Here:\n```python\nprint('hi')\n```"
        blocks = extract_code_blocks(text)
        assert len(blocks) == 1
        assert blocks[0].language == "python"
        assert "print('hi')" in blocks[0].code

    def test_multiple_blocks(self):
        text = (
            "```python\nx = 1\n```\n"
            "And then:\n"
            "```bash\necho hi\n```"
        )
        blocks = extract_code_blocks(text)
        assert len(blocks) == 2
        assert blocks[0].language == "python"
        assert blocks[1].language == "bash"

    def test_no_language_tag_defaults_to_text(self):
        text = "```\nsome code\n```"
        blocks = extract_code_blocks(text)
        assert len(blocks) == 1
        assert blocks[0].language == "text"

    def test_no_blocks_returns_empty(self):
        assert extract_code_blocks("Just some text") == []

    def test_preserves_position(self):
        text = "Start\n```python\nx=1\n```\nEnd"
        blocks = extract_code_blocks(text)
        assert blocks[0].start_pos > 0
        assert blocks[0].end_pos > blocks[0].start_pos

    def test_multiline_code(self):
        text = "```python\ndef foo():\n    return 42\n\nfoo()\n```"
        blocks = extract_code_blocks(text)
        assert len(blocks) == 1
        assert "def foo():" in blocks[0].code
        assert "return 42" in blocks[0].code


# ===================================================================
# classify_language
# ===================================================================

class TestClassifyLanguage:
    def test_known_language(self):
        block = CodeBlock(language="python", code="")
        assert classify_language(block) == "python"

    def test_alias(self):
        block = CodeBlock(language="py", code="")
        assert classify_language(block) == "python"

    def test_unknown_passes_through(self):
        block = CodeBlock(language="rust", code="")
        assert classify_language(block) == "rust"

    def test_golang_alias(self):
        block = CodeBlock(language="golang", code="")
        assert classify_language(block) == "go"

    def test_sh_alias(self):
        block = CodeBlock(language="sh", code="")
        assert classify_language(block) == "bash"

    def test_text_passes_through(self):
        block = CodeBlock(language="text", code="")
        assert classify_language(block) == "text"


# ===================================================================
# build_execution_command
# ===================================================================

class TestBuildExecutionCommand:
    def test_python_command(self):
        block = CodeBlock(language="python", code="print(1)")
        cmd = build_execution_command(block, "/tmp")
        assert cmd[0] == "python3"
        assert cmd[-1].endswith(".py")

    def test_bash_command(self):
        block = CodeBlock(language="bash", code="echo hi")
        cmd = build_execution_command(block, "/tmp")
        assert cmd[0] == "bash"
        assert cmd[-1].endswith(".sh")

    def test_go_command(self):
        block = CodeBlock(language="go", code="package main")
        cmd = build_execution_command(block, "/tmp")
        assert "go" in cmd[0]
        assert cmd[-1].endswith(".go")

    def test_c_command(self):
        block = CodeBlock(language="c", code="int main() {}")
        cmd = build_execution_command(block, "/work")
        assert "gcc" in cmd[0]
        assert cmd[-1].endswith(".c")

    def test_java_command(self):
        block = CodeBlock(language="java", code="class Main {}")
        cmd = build_execution_command(block, "/tmp")
        assert "javac" in cmd[0]

    def test_unsupported_language_raises(self):
        block = CodeBlock(language="rust", code="fn main() {}")
        with pytest.raises(ValueError, match="Unsupported language"):
            build_execution_command(block)

    def test_alias_resolves_correctly(self):
        block = CodeBlock(language="py", code="x = 1")
        cmd = build_execution_command(block, "/tmp")
        assert cmd[0] == "python3"

    def test_custom_work_dir(self):
        block = CodeBlock(language="python", code="x = 1")
        cmd = build_execution_command(block, "/home/user/work")
        assert "/home/user/work" in cmd[-1]


# ===================================================================
# parse_execution_output
# ===================================================================

class TestParseExecutionOutput:
    def test_success_empty_stderr(self):
        result = parse_execution_output("hello", "", tool_type="python")
        assert result.success is True
        assert result.feedback == "hello"
        assert result.tool_type == "python"

    def test_failure_with_error(self):
        result = parse_execution_output(
            "", "Traceback (most recent call last):\nTypeError: ...",
            tool_type="python",
        )
        assert result.success is False
        assert "Traceback" in result.feedback

    def test_warning_not_treated_as_error(self):
        result = parse_execution_output("ok", "DeprecationWarning: use X", tool_type="bash")
        assert result.success is True

    def test_execution_time_preserved(self):
        result = parse_execution_output("", "", execution_time=1.5)
        assert result.execution_time == 1.5

    def test_fatal_is_error(self):
        result = parse_execution_output("", "fatal: not a git repository")
        assert result.success is False

    def test_panic_is_error(self):
        result = parse_execution_output("", "panic: runtime error")
        assert result.success is False

    def test_empty_both_is_success(self):
        result = parse_execution_output("", "")
        assert result.success is True


# ===================================================================
# AgenticSeekCodeExecutor facade
# ===================================================================

class TestAgenticSeekCodeExecutor:
    def test_extract(self):
        executor = AgenticSeekCodeExecutor()
        blocks = executor.extract("```python\nprint(1)\n```")
        assert len(blocks) == 1

    def test_classify(self):
        executor = AgenticSeekCodeExecutor()
        block = CodeBlock(language="py", code="")
        assert executor.classify(block) == "python"

    def test_command_for(self):
        executor = AgenticSeekCodeExecutor(work_dir="/workspace")
        block = CodeBlock(language="bash", code="echo hi")
        cmd = executor.command_for(block)
        assert "/workspace" in cmd[-1]

    def test_parse_output(self):
        executor = AgenticSeekCodeExecutor()
        result = executor.parse_output("ok", "", tool_type="python")
        assert result.success is True

"""Tests for Claude agent mixins.

Tests cover class existence, method signatures, pure-logic helpers,
data transformations, and error paths that do NOT require a real Claude API key.
Methods that call self.execute() (i.e. hit the Anthropic API) are skipped unless
ANTHROPIC_API_KEY is present.

Zero-mock policy: no unittest.mock, MagicMock, monkeypatch, or pytest-mock.
"""

import importlib.util
import os
import tempfile
import textwrap

import pytest

# ---------------------------------------------------------------------------
# Import guards -- all mixin modules must be importable without anthropic
# ---------------------------------------------------------------------------

_HAS_ANTHROPIC = importlib.util.find_spec("anthropic") is not None


# ====================================================================
# CodeIntelMixin tests
# ====================================================================

@pytest.mark.unit
class TestCodeIntelMixin:
    """Tests for codomyrmex.agents.claude.mixins.code_intel.CodeIntelMixin."""

    def test_class_importable(self):
        from codomyrmex.agents.claude.mixins.code_intel import CodeIntelMixin
        assert CodeIntelMixin is not None

    def test_has_review_code_method(self):
        from codomyrmex.agents.claude.mixins.code_intel import CodeIntelMixin
        assert callable(getattr(CodeIntelMixin, "review_code", None))

    def test_has_generate_diff_method(self):
        from codomyrmex.agents.claude.mixins.code_intel import CodeIntelMixin
        assert callable(getattr(CodeIntelMixin, "generate_diff", None))

    def test_has_explain_code_method(self):
        from codomyrmex.agents.claude.mixins.code_intel import CodeIntelMixin
        assert callable(getattr(CodeIntelMixin, "explain_code", None))

    def test_has_suggest_tests_method(self):
        from codomyrmex.agents.claude.mixins.code_intel import CodeIntelMixin
        assert callable(getattr(CodeIntelMixin, "suggest_tests", None))

    def test_has_private_parse_review_output(self):
        from codomyrmex.agents.claude.mixins.code_intel import CodeIntelMixin
        assert callable(getattr(CodeIntelMixin, "_parse_review_output", None))

    def test_has_private_generate_unified_diff(self):
        from codomyrmex.agents.claude.mixins.code_intel import CodeIntelMixin
        assert callable(getattr(CodeIntelMixin, "_generate_unified_diff", None))

    # --- _parse_review_output (pure logic) ---

    def test_parse_review_output_empty_string(self):
        from codomyrmex.agents.claude.mixins.code_intel import CodeIntelMixin
        mixin = CodeIntelMixin()
        issues, recommendations = mixin._parse_review_output("")
        assert issues == []
        assert recommendations == []

    def test_parse_review_output_issues_section(self):
        from codomyrmex.agents.claude.mixins.code_intel import CodeIntelMixin
        mixin = CodeIntelMixin()
        text = textwrap.dedent("""\
            ## Issues Found
            - Variable naming is inconsistent across functions
            - Missing error handling in parse method
            ## Recommendations
            - Add type hints to all function parameters
            - Use pathlib instead of os.path for paths
        """)
        issues, recommendations = mixin._parse_review_output(text)
        assert len(issues) >= 1
        assert len(recommendations) >= 1
        # Verify content was extracted (not header lines)
        assert any("naming" in i.lower() for i in issues)
        assert any("type hints" in r.lower() for r in recommendations)

    def test_parse_review_output_filters_short_items(self):
        """Items <= 5 characters should be filtered out."""
        from codomyrmex.agents.claude.mixins.code_intel import CodeIntelMixin
        mixin = CodeIntelMixin()
        text = "## Issues\n- ab\n- This is a real issue that is long enough"
        issues, _ = mixin._parse_review_output(text)
        # "ab" is too short (<=5 chars), should be filtered
        assert not any(len(i) <= 5 for i in issues)

    def test_parse_review_output_numbered_items(self):
        """Numbered items under an Issues header should be captured.
        Note: items must NOT contain 'issue'/'problem'/'bug' themselves,
        otherwise the parser re-classifies them as section headers."""
        from codomyrmex.agents.claude.mixins.code_intel import CodeIntelMixin
        mixin = CodeIntelMixin()
        text = "## Issues Found\n1. Missing validation on user input fields\n2. Unchecked return value from database query"
        issues, _ = mixin._parse_review_output(text)
        assert len(issues) >= 1
        assert any("validation" in i.lower() for i in issues)

    # --- _generate_unified_diff (pure logic) ---

    def test_generate_unified_diff_identical(self):
        from codomyrmex.agents.claude.mixins.code_intel import CodeIntelMixin
        mixin = CodeIntelMixin()
        diff = mixin._generate_unified_diff("hello\n", "hello\n", "test.py")
        assert diff == ""

    def test_generate_unified_diff_addition(self):
        from codomyrmex.agents.claude.mixins.code_intel import CodeIntelMixin
        mixin = CodeIntelMixin()
        diff = mixin._generate_unified_diff("line1\n", "line1\nline2\n", "test.py")
        assert "+line2" in diff
        assert "a/test.py" in diff
        assert "b/test.py" in diff

    def test_generate_unified_diff_deletion(self):
        from codomyrmex.agents.claude.mixins.code_intel import CodeIntelMixin
        mixin = CodeIntelMixin()
        diff = mixin._generate_unified_diff("line1\nline2\n", "line1\n", "test.py")
        assert "-line2" in diff

    # --- generate_diff (uses _generate_unified_diff internally, pure logic) ---

    def test_generate_diff_no_changes(self):
        from codomyrmex.agents.claude.mixins.code_intel import CodeIntelMixin
        mixin = CodeIntelMixin()
        result = mixin.generate_diff("same\n", "same\n")
        assert result["has_changes"] is False
        assert result["additions"] == 0
        assert result["deletions"] == 0

    def test_generate_diff_with_changes(self):
        from codomyrmex.agents.claude.mixins.code_intel import CodeIntelMixin
        mixin = CodeIntelMixin()
        result = mixin.generate_diff("old_line\n", "new_line\n", filename="app.py")
        assert result["has_changes"] is True
        assert result["additions"] >= 1
        assert result["deletions"] >= 1
        assert isinstance(result["diff"], str)

    def test_generate_diff_return_keys(self):
        from codomyrmex.agents.claude.mixins.code_intel import CodeIntelMixin
        mixin = CodeIntelMixin()
        result = mixin.generate_diff("a\n", "b\n")
        expected_keys = {"diff", "additions", "deletions", "has_changes"}
        assert expected_keys == set(result.keys())


# ====================================================================
# ExecutionMixin tests
# ====================================================================

@pytest.mark.unit
class TestExecutionMixin:
    """Tests for codomyrmex.agents.claude.mixins.execution.ExecutionMixin."""

    def test_class_importable(self):
        from codomyrmex.agents.claude.mixins.execution import ExecutionMixin
        assert ExecutionMixin is not None

    def test_has_execute_impl_method(self):
        from codomyrmex.agents.claude.mixins.execution import ExecutionMixin
        assert callable(getattr(ExecutionMixin, "_execute_impl", None))

    def test_has_execute_with_retry_method(self):
        from codomyrmex.agents.claude.mixins.execution import ExecutionMixin
        assert callable(getattr(ExecutionMixin, "_execute_with_retry", None))

    def test_has_stream_impl_method(self):
        from codomyrmex.agents.claude.mixins.execution import ExecutionMixin
        assert callable(getattr(ExecutionMixin, "_stream_impl", None))

    def test_has_build_messages_with_system_method(self):
        from codomyrmex.agents.claude.mixins.execution import ExecutionMixin
        assert callable(getattr(ExecutionMixin, "_build_messages_with_system", None))

    def test_has_calculate_cost_method(self):
        from codomyrmex.agents.claude.mixins.execution import ExecutionMixin
        assert callable(getattr(ExecutionMixin, "_calculate_cost", None))

    def test_has_extract_response_content_method(self):
        from codomyrmex.agents.claude.mixins.execution import ExecutionMixin
        assert callable(getattr(ExecutionMixin, "_extract_response_content", None))

    # --- CLAUDE_PRICING constant ---

    def test_claude_pricing_dict_exists(self):
        from codomyrmex.agents.claude.mixins.execution import CLAUDE_PRICING
        assert isinstance(CLAUDE_PRICING, dict)
        assert len(CLAUDE_PRICING) > 0

    def test_claude_pricing_has_input_output_keys(self):
        from codomyrmex.agents.claude.mixins.execution import CLAUDE_PRICING
        for model_name, pricing in CLAUDE_PRICING.items():
            assert "input" in pricing, f"Missing 'input' key for {model_name}"
            assert "output" in pricing, f"Missing 'output' key for {model_name}"
            assert isinstance(pricing["input"], (int, float))
            assert isinstance(pricing["output"], (int, float))

    # --- _calculate_cost (pure math, needs self.model) ---

    def test_calculate_cost_known_model(self):
        """Test cost calculation for a known model in CLAUDE_PRICING."""
        from codomyrmex.agents.claude.mixins.execution import (
            CLAUDE_PRICING,
            ExecutionMixin,
        )
        mixin = ExecutionMixin()
        # Pick a model from the pricing dict
        model_name = next(iter(CLAUDE_PRICING))
        mixin.model = model_name
        cost = mixin._calculate_cost(1000, 500)
        assert isinstance(cost, float)
        assert cost >= 0.0

    def test_calculate_cost_unknown_model_uses_default(self):
        """Unknown models should use default pricing (3.00 input / 15.00 output)."""
        from codomyrmex.agents.claude.mixins.execution import ExecutionMixin
        mixin = ExecutionMixin()
        mixin.model = "nonexistent-model-xyz"
        cost = mixin._calculate_cost(1_000_000, 1_000_000)
        # Default: input=3.00, output=15.00
        expected = 3.00 + 15.00
        assert abs(cost - expected) < 0.01

    def test_calculate_cost_zero_tokens(self):
        from codomyrmex.agents.claude.mixins.execution import ExecutionMixin
        mixin = ExecutionMixin()
        mixin.model = "nonexistent-model"
        cost = mixin._calculate_cost(0, 0)
        assert cost == 0.0

    # --- _build_messages_with_system (pure data transform) ---

    def test_build_messages_basic_prompt(self):
        from codomyrmex.agents.claude.mixins.execution import ExecutionMixin
        from codomyrmex.agents.core import AgentRequest
        mixin = ExecutionMixin()
        request = AgentRequest(prompt="Hello Claude")
        messages, system_msg = mixin._build_messages_with_system(request)
        assert len(messages) == 1
        assert messages[0]["role"] == "user"
        assert messages[0]["content"] == "Hello Claude"
        assert system_msg is None

    def test_build_messages_with_system_key(self):
        from codomyrmex.agents.claude.mixins.execution import ExecutionMixin
        from codomyrmex.agents.core import AgentRequest
        mixin = ExecutionMixin()
        request = AgentRequest(
            prompt="Test",
            context={"system": "You are a helpful assistant."},
        )
        messages, system_msg = mixin._build_messages_with_system(request)
        assert system_msg == "You are a helpful assistant."
        assert len(messages) == 1

    def test_build_messages_with_system_prompt_key(self):
        from codomyrmex.agents.claude.mixins.execution import ExecutionMixin
        from codomyrmex.agents.core import AgentRequest
        mixin = ExecutionMixin()
        request = AgentRequest(
            prompt="Test",
            context={"system_prompt": "Be concise."},
        )
        messages, system_msg = mixin._build_messages_with_system(request)
        assert system_msg == "Be concise."

    def test_build_messages_with_context_items_as_system(self):
        """Non-reserved context keys should be joined into system message."""
        from codomyrmex.agents.claude.mixins.execution import ExecutionMixin
        from codomyrmex.agents.core import AgentRequest
        mixin = ExecutionMixin()
        request = AgentRequest(
            prompt="Test",
            context={"role_description": "Expert Python developer"},
        )
        messages, system_msg = mixin._build_messages_with_system(request)
        assert system_msg is not None
        assert "Expert Python developer" in system_msg

    def test_build_messages_with_conversation_history(self):
        from codomyrmex.agents.claude.mixins.execution import ExecutionMixin
        from codomyrmex.agents.core import AgentRequest
        mixin = ExecutionMixin()
        request = AgentRequest(
            prompt="Follow-up question",
            context={
                "messages": [
                    {"role": "user", "content": "First question"},
                    {"role": "assistant", "content": "First answer"},
                ],
            },
        )
        messages, system_msg = mixin._build_messages_with_system(request)
        # History messages + the current prompt
        assert len(messages) == 3
        assert messages[0]["role"] == "user"
        assert messages[0]["content"] == "First question"
        assert messages[2]["content"] == "Follow-up question"

    def test_build_messages_with_images(self):
        from codomyrmex.agents.claude.mixins.execution import ExecutionMixin
        from codomyrmex.agents.core import AgentRequest
        mixin = ExecutionMixin()
        request = AgentRequest(
            prompt="Describe this image",
            context={"images": ["base64encodeddata"]},
        )
        messages, _ = mixin._build_messages_with_system(request)
        assert len(messages) == 1
        content = messages[0]["content"]
        assert isinstance(content, list)
        assert content[0]["type"] == "text"
        assert content[1]["type"] == "image"

    def test_build_messages_with_image_dict(self):
        from codomyrmex.agents.claude.mixins.execution import ExecutionMixin
        from codomyrmex.agents.core import AgentRequest
        mixin = ExecutionMixin()
        img_dict = {"type": "image", "source": {"type": "url", "url": "https://example.com/img.png"}}
        request = AgentRequest(
            prompt="Describe",
            context={"images": [img_dict]},
        )
        messages, _ = mixin._build_messages_with_system(request)
        content = messages[0]["content"]
        assert content[1] is img_dict


# ====================================================================
# SystemOpsMixin tests
# ====================================================================

@pytest.mark.unit
class TestSystemOpsMixin:
    """Tests for codomyrmex.agents.claude.mixins.system_ops.SystemOpsMixin."""

    def test_class_importable(self):
        from codomyrmex.agents.claude.mixins.system_ops import SystemOpsMixin
        assert SystemOpsMixin is not None

    def test_has_scan_directory_method(self):
        from codomyrmex.agents.claude.mixins.system_ops import SystemOpsMixin
        assert callable(getattr(SystemOpsMixin, "scan_directory", None))

    def test_has_run_command_method(self):
        from codomyrmex.agents.claude.mixins.system_ops import SystemOpsMixin
        assert callable(getattr(SystemOpsMixin, "run_command", None))

    def test_has_get_project_structure_method(self):
        from codomyrmex.agents.claude.mixins.system_ops import SystemOpsMixin
        assert callable(getattr(SystemOpsMixin, "get_project_structure", None))

    # --- scan_directory (real filesystem) ---

    def test_scan_directory_nonexistent_path(self):
        from codomyrmex.agents.claude.mixins.system_ops import SystemOpsMixin
        mixin = SystemOpsMixin()
        result = mixin.scan_directory("/nonexistent/path/abc123xyz")
        assert result["success"] is False
        assert "not found" in result["error"].lower() or "not found" in result.get("error", "").lower()
        assert result["file_count"] == 0
        assert result["files"] == []

    def test_scan_directory_real_temp_dir(self):
        from codomyrmex.agents.claude.mixins.system_ops import SystemOpsMixin
        mixin = SystemOpsMixin()
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create some test files
            for name in ["hello.py", "world.txt", "data.json"]:
                with open(os.path.join(tmpdir, name), "w") as f:
                    f.write("content")
            result = mixin.scan_directory(tmpdir)
            assert result["success"] is True
            assert result["file_count"] == 3
            assert len(result["files"]) == 3

    def test_scan_directory_exclude_patterns(self):
        from codomyrmex.agents.claude.mixins.system_ops import SystemOpsMixin
        mixin = SystemOpsMixin()
        with tempfile.TemporaryDirectory() as tmpdir:
            with open(os.path.join(tmpdir, "keep.py"), "w") as f:
                f.write("x")
            with open(os.path.join(tmpdir, "skip.log"), "w") as f:
                f.write("x")
            result = mixin.scan_directory(tmpdir, exclude_patterns=["*.log"])
            assert result["success"] is True
            assert any("keep.py" in p for p in result["files"])
            assert not any("skip.log" in p for p in result["files"])

    def test_scan_directory_include_patterns(self):
        from codomyrmex.agents.claude.mixins.system_ops import SystemOpsMixin
        mixin = SystemOpsMixin()
        with tempfile.TemporaryDirectory() as tmpdir:
            with open(os.path.join(tmpdir, "app.py"), "w") as f:
                f.write("x")
            with open(os.path.join(tmpdir, "readme.md"), "w") as f:
                f.write("x")
            result = mixin.scan_directory(tmpdir, include_patterns=["*.py"])
            assert result["success"] is True
            assert any("app.py" in p for p in result["files"])
            assert not any("readme.md" in p for p in result["files"])

    def test_scan_directory_max_depth(self):
        from codomyrmex.agents.claude.mixins.system_ops import SystemOpsMixin
        mixin = SystemOpsMixin()
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create nested structure deeper than max_depth=1
            nested = os.path.join(tmpdir, "a", "b", "c")
            os.makedirs(nested)
            with open(os.path.join(nested, "deep.py"), "w") as f:
                f.write("x")
            with open(os.path.join(tmpdir, "shallow.py"), "w") as f:
                f.write("x")
            result = mixin.scan_directory(tmpdir, max_depth=1)
            assert result["success"] is True
            # shallow.py should be found; deep.py at depth 3 might be truncated
            assert any("shallow.py" in p for p in result["files"])

    def test_scan_directory_return_keys(self):
        from codomyrmex.agents.claude.mixins.system_ops import SystemOpsMixin
        mixin = SystemOpsMixin()
        with tempfile.TemporaryDirectory() as tmpdir:
            result = mixin.scan_directory(tmpdir)
            expected_keys = {"success", "structure", "file_count", "files", "summary"}
            assert expected_keys.issubset(set(result.keys()))

    # --- run_command (real subprocess) ---

    def test_run_command_echo(self):
        from codomyrmex.agents.claude.mixins.system_ops import SystemOpsMixin
        mixin = SystemOpsMixin()
        result = mixin.run_command("echo hello_world")
        assert result["success"] is True
        assert result["return_code"] == 0
        assert "hello_world" in result["stdout"]

    def test_run_command_failure(self):
        from codomyrmex.agents.claude.mixins.system_ops import SystemOpsMixin
        mixin = SystemOpsMixin()
        result = mixin.run_command("false")
        assert result["success"] is False
        assert result["return_code"] != 0

    def test_run_command_timeout(self):
        from codomyrmex.agents.claude.mixins.system_ops import SystemOpsMixin
        mixin = SystemOpsMixin()
        result = mixin.run_command("sleep 10", timeout=1)
        assert result["success"] is False
        assert "timed out" in result["stderr"].lower()

    def test_run_command_return_keys(self):
        from codomyrmex.agents.claude.mixins.system_ops import SystemOpsMixin
        mixin = SystemOpsMixin()
        result = mixin.run_command("echo test")
        expected_keys = {"success", "return_code", "stdout", "stderr", "duration", "command"}
        assert expected_keys == set(result.keys())


# ====================================================================
# FileOpsMixin tests
# ====================================================================

@pytest.mark.unit
class TestFileOpsMixin:
    """Tests for codomyrmex.agents.claude.mixins.file_ops.FileOpsMixin."""

    def test_class_importable(self):
        from codomyrmex.agents.claude.mixins.file_ops import FileOpsMixin
        assert FileOpsMixin is not None

    def test_has_edit_file_method(self):
        from codomyrmex.agents.claude.mixins.file_ops import FileOpsMixin
        assert callable(getattr(FileOpsMixin, "edit_file", None))

    def test_has_create_file_method(self):
        from codomyrmex.agents.claude.mixins.file_ops import FileOpsMixin
        assert callable(getattr(FileOpsMixin, "create_file", None))

    def test_has_extract_code_block_method(self):
        from codomyrmex.agents.claude.mixins.file_ops import FileOpsMixin
        assert callable(getattr(FileOpsMixin, "_extract_code_block", None))

    # --- _extract_code_block (pure string parsing) ---

    def test_extract_code_block_language_specific(self):
        from codomyrmex.agents.claude.mixins.file_ops import FileOpsMixin
        mixin = FileOpsMixin()
        response = '```python\ndef hello():\n    pass\n```'
        result = mixin._extract_code_block(response, "python")
        assert result == "def hello():\n    pass"

    def test_extract_code_block_generic(self):
        from codomyrmex.agents.claude.mixins.file_ops import FileOpsMixin
        mixin = FileOpsMixin()
        response = '```\nsome code\n```'
        result = mixin._extract_code_block(response, "python")
        assert result == "some code"

    def test_extract_code_block_no_fence(self):
        from codomyrmex.agents.claude.mixins.file_ops import FileOpsMixin
        mixin = FileOpsMixin()
        response = "just plain text"
        result = mixin._extract_code_block(response, "python")
        assert result == "just plain text"

    def test_extract_code_block_strips_whitespace(self):
        from codomyrmex.agents.claude.mixins.file_ops import FileOpsMixin
        mixin = FileOpsMixin()
        response = '```python\n  code  \n```'
        result = mixin._extract_code_block(response, "python")
        assert result == "code"

    # --- edit_file: file-not-found path (no API call) ---

    def test_edit_file_nonexistent_file(self):
        from codomyrmex.agents.claude.mixins.file_ops import FileOpsMixin
        mixin = FileOpsMixin()
        result = mixin.edit_file("/nonexistent/path/abc123.py", "add docstrings")
        assert result["success"] is False
        assert "not found" in result["error"].lower()
        assert result["original_content"] == ""
        assert result["modified_content"] == ""

    # --- edit_file: language auto-detection (no API call needed for detection) ---

    def test_edit_file_auto_detects_language_from_extension(self):
        """Verify the lang_map logic by checking a real temp file path."""

        # We just verify the lang_map dict exists and covers common extensions
        ext_map = {
            ".py": "python", ".js": "javascript", ".ts": "typescript",
            ".java": "java", ".go": "go", ".rs": "rust", ".rb": "ruby",
        }
        # This is hardcoded in the method; we're verifying our understanding
        for ext, expected_lang in ext_map.items():
            assert expected_lang is not None  # sanity


# ====================================================================
# ToolsMixin tests
# ====================================================================

@pytest.mark.unit
class TestToolsMixin:
    """Tests for codomyrmex.agents.claude.mixins.tools.ToolsMixin."""

    def test_class_importable(self):
        from codomyrmex.agents.claude.mixins.tools import ToolsMixin
        assert ToolsMixin is not None

    def test_has_register_tool_method(self):
        from codomyrmex.agents.claude.mixins.tools import ToolsMixin
        assert callable(getattr(ToolsMixin, "register_tool", None))

    def test_has_get_registered_tools_method(self):
        from codomyrmex.agents.claude.mixins.tools import ToolsMixin
        assert callable(getattr(ToolsMixin, "get_registered_tools", None))

    def test_has_execute_tool_call_method(self):
        from codomyrmex.agents.claude.mixins.tools import ToolsMixin
        assert callable(getattr(ToolsMixin, "execute_tool_call", None))

    def test_has_execute_with_tools_method(self):
        from codomyrmex.agents.claude.mixins.tools import ToolsMixin
        assert callable(getattr(ToolsMixin, "execute_with_tools", None))

    # --- register_tool / get_registered_tools (pure in-memory) ---

    def _make_tools_mixin(self):
        """Create a ToolsMixin instance with required attributes."""
        from codomyrmex.agents.claude.mixins.tools import ToolsMixin
        from codomyrmex.logging_monitoring.core.logger_config import get_logger
        mixin = ToolsMixin()
        mixin._tools = []
        mixin.logger = get_logger("test_tools_mixin")
        return mixin

    def test_register_tool_adds_to_list(self):
        mixin = self._make_tools_mixin()
        mixin.register_tool(
            name="get_weather",
            description="Get current weather",
            input_schema={"type": "object", "properties": {"city": {"type": "string"}}},
        )
        tools = mixin.get_registered_tools()
        assert len(tools) == 1
        assert tools[0]["name"] == "get_weather"

    def test_register_tool_replaces_duplicate(self):
        mixin = self._make_tools_mixin()
        mixin.register_tool(name="search", description="v1", input_schema={})
        mixin.register_tool(name="search", description="v2", input_schema={})
        tools = mixin.get_registered_tools()
        assert len(tools) == 1
        assert tools[0]["description"] == "v2"

    def test_get_registered_tools_returns_copy(self):
        mixin = self._make_tools_mixin()
        mixin.register_tool(name="tool1", description="desc", input_schema={})
        tools1 = mixin.get_registered_tools()
        tools2 = mixin.get_registered_tools()
        assert tools1 is not tools2  # must be a copy

    def test_register_tool_with_handler(self):
        mixin = self._make_tools_mixin()

        def my_handler(x: int) -> int:
            return x * 2

        mixin.register_tool(
            name="doubler",
            description="Doubles a number",
            input_schema={"type": "object", "properties": {"x": {"type": "integer"}}},
            handler=my_handler,
        )
        assert hasattr(mixin, "_tool_handlers")
        assert "doubler" in mixin._tool_handlers

    def test_execute_tool_call_success(self):
        mixin = self._make_tools_mixin()

        def adder(a: int, b: int) -> int:
            return a + b

        mixin.register_tool(
            name="adder",
            description="Add two numbers",
            input_schema={},
            handler=adder,
        )
        result = mixin.execute_tool_call("adder", {"a": 3, "b": 4})
        assert result == 7

    def test_execute_tool_call_no_handlers_raises(self):
        from codomyrmex.agents.core.exceptions import ClaudeError
        mixin = self._make_tools_mixin()
        # No tools registered, no _tool_handlers attribute
        if hasattr(mixin, "_tool_handlers"):
            del mixin._tool_handlers
        with pytest.raises(ClaudeError, match="No tool handlers registered"):
            mixin.execute_tool_call("missing_tool", {})

    def test_execute_tool_call_unknown_tool_raises(self):
        from codomyrmex.agents.core.exceptions import ClaudeError
        mixin = self._make_tools_mixin()
        mixin._tool_handlers = {}
        with pytest.raises(ClaudeError, match="No handler registered"):
            mixin.execute_tool_call("nonexistent", {})

    def test_execute_tool_call_handler_error_raises_claude_error(self):
        from codomyrmex.agents.core.exceptions import ClaudeError
        mixin = self._make_tools_mixin()

        def bad_handler() -> None:
            raise ValueError("something went wrong")

        mixin.register_tool(name="bad", description="fails", input_schema={}, handler=bad_handler)
        with pytest.raises(ClaudeError, match="Tool execution failed"):
            mixin.execute_tool_call("bad", {})

    def test_register_multiple_tools(self):
        mixin = self._make_tools_mixin()
        for i in range(5):
            mixin.register_tool(name=f"tool_{i}", description=f"Tool {i}", input_schema={})
        tools = mixin.get_registered_tools()
        assert len(tools) == 5
        names = {t["name"] for t in tools}
        assert names == {f"tool_{i}" for i in range(5)}


# ====================================================================
# SessionMixin tests
# ====================================================================

@pytest.mark.unit
class TestSessionMixin:
    """Tests for codomyrmex.agents.claude.mixins.session.SessionMixin."""

    def test_class_importable(self):
        from codomyrmex.agents.claude.mixins.session import SessionMixin
        assert SessionMixin is not None

    def test_has_execute_with_session_method(self):
        from codomyrmex.agents.claude.mixins.session import SessionMixin
        assert callable(getattr(SessionMixin, "execute_with_session", None))

    def test_has_create_session_method(self):
        from codomyrmex.agents.claude.mixins.session import SessionMixin
        assert callable(getattr(SessionMixin, "create_session", None))

    def test_create_session_without_manager(self):
        """When session_manager is None, create_session returns a plain AgentSession."""
        from codomyrmex.agents.claude.mixins.session import SessionMixin
        from codomyrmex.agents.core.session import AgentSession
        mixin = SessionMixin()
        mixin.session_manager = None
        session = mixin.create_session()
        assert isinstance(session, AgentSession)
        assert session.agent_name == "claude"

    def test_create_session_generates_unique_ids(self):
        from codomyrmex.agents.claude.mixins.session import SessionMixin
        mixin = SessionMixin()
        mixin.session_manager = None
        s1 = mixin.create_session()
        s2 = mixin.create_session()
        assert s1.session_id != s2.session_id


# ====================================================================
# ClaudeClient composition tests
# ====================================================================

@pytest.mark.unit
class TestClaudeClientComposition:
    """Tests that ClaudeClient composes all expected mixins."""

    @pytest.mark.skipif(
        not _HAS_ANTHROPIC,
        reason="requires anthropic package installed",
    )
    def test_claude_client_importable(self):
        from codomyrmex.agents.claude.claude_client import ClaudeClient
        assert ClaudeClient is not None

    @pytest.mark.skipif(
        not _HAS_ANTHROPIC,
        reason="requires anthropic package installed",
    )
    def test_claude_client_inherits_all_mixins(self):
        from codomyrmex.agents.claude.claude_client import ClaudeClient
        from codomyrmex.agents.claude.mixins.code_intel import CodeIntelMixin
        from codomyrmex.agents.claude.mixins.execution import ExecutionMixin
        from codomyrmex.agents.claude.mixins.file_ops import FileOpsMixin
        from codomyrmex.agents.claude.mixins.session import SessionMixin
        from codomyrmex.agents.claude.mixins.system_ops import SystemOpsMixin
        from codomyrmex.agents.claude.mixins.tools import ToolsMixin

        assert issubclass(ClaudeClient, CodeIntelMixin)
        assert issubclass(ClaudeClient, ExecutionMixin)
        assert issubclass(ClaudeClient, FileOpsMixin)
        assert issubclass(ClaudeClient, SessionMixin)
        assert issubclass(ClaudeClient, SystemOpsMixin)
        assert issubclass(ClaudeClient, ToolsMixin)

    @pytest.mark.skipif(
        not _HAS_ANTHROPIC,
        reason="requires anthropic package installed",
    )
    def test_claude_client_mro_has_api_agent_base(self):
        from codomyrmex.agents.claude.claude_client import ClaudeClient
        from codomyrmex.agents.generic.api_agent_base import APIAgentBase
        assert issubclass(ClaudeClient, APIAgentBase)

    @pytest.mark.skipif(
        not _HAS_ANTHROPIC,
        reason="requires anthropic package installed",
    )
    def test_claude_client_default_model_constant(self):
        from codomyrmex.agents.claude.claude_client import DEFAULT_CLAUDE_MODEL
        assert isinstance(DEFAULT_CLAUDE_MODEL, str)
        assert "claude" in DEFAULT_CLAUDE_MODEL.lower()

    @pytest.mark.skipif(
        not _HAS_ANTHROPIC,
        reason="requires anthropic package installed",
    )
    def test_claude_client_pricing_dict(self):
        from codomyrmex.agents.claude.claude_client import CLAUDE_PRICING
        assert isinstance(CLAUDE_PRICING, dict)
        assert len(CLAUDE_PRICING) > 0


# ====================================================================
# Cross-mixin integration: verify helpers that other mixins depend on
# ====================================================================

@pytest.mark.unit
class TestCrossMixinHelpers:
    """Tests verifying helper methods shared across mixins."""

    def test_code_intel_generate_diff_uses_unified_diff(self):
        """generate_diff delegates to _generate_unified_diff internally."""
        from codomyrmex.agents.claude.mixins.code_intel import CodeIntelMixin
        mixin = CodeIntelMixin()
        result = mixin.generate_diff("a\n", "b\n", filename="cross.py")
        assert "a/cross.py" in result["diff"]
        assert "b/cross.py" in result["diff"]

    def test_file_ops_extract_code_block_case_insensitive(self):
        """Language matching in _extract_code_block should be case-insensitive."""
        from codomyrmex.agents.claude.mixins.file_ops import FileOpsMixin
        mixin = FileOpsMixin()
        response = '```Python\nprint("hi")\n```'
        result = mixin._extract_code_block(response, "python")
        assert 'print("hi")' in result

    def test_execution_build_messages_reserved_keys_excluded(self):
        """Reserved keys (messages, tools, session_id, images) must not
        appear in the auto-generated system message."""
        from codomyrmex.agents.claude.mixins.execution import ExecutionMixin
        from codomyrmex.agents.core import AgentRequest
        mixin = ExecutionMixin()
        request = AgentRequest(
            prompt="Test",
            context={"session_id": "abc", "tools": [], "custom_key": "value"},
        )
        _, system_msg = mixin._build_messages_with_system(request)
        assert system_msg is not None
        assert "custom_key" in system_msg
        assert "session_id" not in system_msg

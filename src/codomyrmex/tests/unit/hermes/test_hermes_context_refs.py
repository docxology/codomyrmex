"""Unit tests for Hermes @ context reference parsing and expansion.

Zero-Mock Policy: tests use real Files and directories (tmp_path).
The upstream context_references module is imported from the same checkout as
:mod:`codomyrmex.agents.hermes.hermes_paths` (``HERMES_AGENT_REPO`` or defaults).

Tests cover:
- parse_context_references(): token parsing
- _strip_trailing_punctuation(): punctuation handling
- _remove_reference_tokens(): token removal from message
- _is_binary_file(): binary detection
- preprocess_context_references_async(): end-to-end expansion
"""

from __future__ import annotations

import asyncio
from pathlib import Path

import pytest

from codomyrmex.agents.hermes.hermes_paths import discover_hermes_agent_repo

# ---------------------------------------------------------------------------
# Import helpers
# ---------------------------------------------------------------------------


def _hermes_agent_root() -> Path | None:
    return discover_hermes_agent_repo()


def _import_ctx():
    """Import agent.context_references from the unified hermes-agent checkout, or skip."""
    import sys

    root = _hermes_agent_root()
    if root is None:
        pytest.skip(
            "hermes-agent not found — set HERMES_AGENT_REPO or install under ~/.hermes/hermes-agent"
        )

    if str(root) not in sys.path:
        sys.path.insert(0, str(root))

    try:
        import agent.context_references as ctx

        return ctx
    except ImportError as e:
        pytest.skip(f"agent.context_references not importable: {e}")


# ---------------------------------------------------------------------------
# parse_context_references()
# ---------------------------------------------------------------------------


class TestParseContextReferences:
    """Token parsing: extracts typed ContextReference objects from message text."""

    def test_empty_message_returns_empty(self):
        ctx = _import_ctx()
        refs = ctx.parse_context_references("")
        assert refs == []

    def test_no_references_returns_empty(self):
        ctx = _import_ctx()
        refs = ctx.parse_context_references("Just a normal message without at-refs.")
        assert refs == []

    def test_parse_diff_simple(self):
        ctx = _import_ctx()
        refs = ctx.parse_context_references("Show me @diff")
        assert len(refs) == 1
        assert refs[0].kind == "diff"
        assert refs[0].target == ""

    def test_parse_staged_simple(self):
        ctx = _import_ctx()
        refs = ctx.parse_context_references("What did I stage? @staged")
        assert len(refs) == 1
        assert refs[0].kind == "staged"

    def test_parse_file_reference(self):
        ctx = _import_ctx()
        refs = ctx.parse_context_references("Look at @file:src/main.py please")
        assert len(refs) == 1
        ref = refs[0]
        assert ref.kind == "file"
        assert ref.target == "src/main.py"
        assert ref.line_start is None
        assert ref.line_end is None

    def test_parse_file_with_line_range(self):
        ctx = _import_ctx()
        refs = ctx.parse_context_references("Lines @file:src/main.py:10-20 please")
        assert len(refs) == 1
        ref = refs[0]
        assert ref.kind == "file"
        assert ref.target == "src/main.py"
        assert ref.line_start == 10
        assert ref.line_end == 20

    def test_parse_file_single_line(self):
        ctx = _import_ctx()
        refs = ctx.parse_context_references("@file:config.yaml:42")
        assert len(refs) == 1
        ref = refs[0]
        assert ref.line_start == 42
        assert ref.line_end == 42

    def test_parse_folder_reference(self):
        ctx = _import_ctx()
        refs = ctx.parse_context_references("list @folder:src/")
        assert len(refs) == 1
        assert refs[0].kind == "folder"
        assert refs[0].target == "src/"

    def test_parse_url_reference(self):
        ctx = _import_ctx()
        refs = ctx.parse_context_references("Read @url:https://example.com/page")
        assert len(refs) == 1
        ref = refs[0]
        assert ref.kind == "url"
        assert ref.target == "https://example.com/page"

    def test_parse_git_reference(self):
        ctx = _import_ctx()
        refs = ctx.parse_context_references("Show @git:3 commits")
        assert len(refs) == 1
        ref = refs[0]
        assert ref.kind == "git"
        assert ref.target == "3"

    def test_multiple_references(self):
        ctx = _import_ctx()
        refs = ctx.parse_context_references("@file:a.py and @diff and @staged")
        assert len(refs) == 3
        kinds = {r.kind for r in refs}
        assert kinds == {"file", "diff", "staged"}

    def test_raw_text_preserved(self):
        ctx = _import_ctx()
        refs = ctx.parse_context_references("See @file:src/main.py for details")
        assert refs[0].raw == "@file:src/main.py"


# ---------------------------------------------------------------------------
# _strip_trailing_punctuation()
# ---------------------------------------------------------------------------


class TestStripTrailingPunctuation:
    """Trailing punctuation stripped but balanced brackets preserved."""

    def test_comma_stripped(self):
        ctx = _import_ctx()
        assert ctx._strip_trailing_punctuation("src/main.py,") == "src/main.py"

    def test_period_stripped(self):
        ctx = _import_ctx()
        assert ctx._strip_trailing_punctuation("main.py.") == "main.py"

    def test_clean_path_unchanged(self):
        ctx = _import_ctx()
        assert ctx._strip_trailing_punctuation("src/main.py") == "src/main.py"

    def test_balanced_parens_preserved(self):
        ctx = _import_ctx()
        # Balanced parens not stripped
        result = ctx._strip_trailing_punctuation("func(arg)")
        assert "(" in result or result == "func(arg)"

    def test_empty_string(self):
        ctx = _import_ctx()
        assert ctx._strip_trailing_punctuation("") == ""


# ---------------------------------------------------------------------------
# _remove_reference_tokens()
# ---------------------------------------------------------------------------


class TestRemoveReferenceTokens:
    """Reference tokens removed cleanly from the parent message."""

    def test_single_token_removed(self):
        ctx = _import_ctx()
        refs = ctx.parse_context_references("Show me @diff please")
        result = ctx._remove_reference_tokens("Show me @diff please", refs)
        assert "@diff" not in result
        assert "Show me" in result
        assert "please" in result

    def test_multiple_tokens_removed(self):
        ctx = _import_ctx()
        msg = "Look at @file:a.py and @diff"
        refs = ctx.parse_context_references(msg)
        result = ctx._remove_reference_tokens(msg, refs)
        assert "@file:" not in result
        assert "@diff" not in result

    def test_no_tokens_returns_unchanged(self):
        ctx = _import_ctx()
        msg = "Just a normal message."
        refs = ctx.parse_context_references(msg)
        result = ctx._remove_reference_tokens(msg, refs)
        assert result.strip() == msg.strip()

    def test_double_spaces_collapsed(self):
        ctx = _import_ctx()
        msg = "See @file:x.py for info"
        refs = ctx.parse_context_references(msg)
        result = ctx._remove_reference_tokens(msg, refs)
        assert "  " not in result  # no double spaces


# ---------------------------------------------------------------------------
# _is_binary_file()
# ---------------------------------------------------------------------------


class TestIsBinaryFile:
    """Binary file detection via MIME type and null byte check."""

    def test_text_py_not_binary(self, tmp_path):
        ctx = _import_ctx()
        f = tmp_path / "script.py"
        f.write_text("print('hello')")
        assert ctx._is_binary_file(f) is False

    def test_text_md_not_binary(self, tmp_path):
        ctx = _import_ctx()
        f = tmp_path / "README.md"
        f.write_text("# Title\n")
        assert ctx._is_binary_file(f) is False

    def test_binary_null_byte_detected(self, tmp_path):
        ctx = _import_ctx()
        f = tmp_path / "binary.bin"
        f.write_bytes(b"\x00\x01\x02\x03binary content here")
        assert ctx._is_binary_file(f) is True

    def test_empty_file_not_binary(self, tmp_path):
        ctx = _import_ctx()
        f = tmp_path / "empty.txt"
        f.write_bytes(b"")
        assert ctx._is_binary_file(f) is False


# ---------------------------------------------------------------------------
# preprocess_context_references_async() — end-to-end
# ---------------------------------------------------------------------------


class TestPreprocessContextReferencesAsync:
    """End-to-end expansion with real temp files."""

    def _run(self, coro):
        return asyncio.run(coro)

    def test_no_refs_returns_unchanged(self, tmp_path):
        ctx = _import_ctx()
        msg = "Just a normal message"
        result = self._run(
            ctx.preprocess_context_references_async(
                msg, cwd=tmp_path, context_length=128000
            )
        )
        assert result.message == msg
        assert result.expanded is False
        assert result.blocked is False
        assert result.references == []

    def test_file_reference_expanded(self, tmp_path):
        ctx = _import_ctx()
        f = tmp_path / "hello.py"
        f.write_text("def greet(): return 'hello'\n")

        msg = f"What does @file:{f} do?"
        result = self._run(
            ctx.preprocess_context_references_async(
                msg, cwd=tmp_path, context_length=128000
            )
        )
        assert result.expanded is True
        assert result.blocked is False
        assert "greet" in result.message
        assert "Attached Context" in result.message

    def test_file_not_found_produces_warning(self, tmp_path):
        ctx = _import_ctx()
        msg = "@file:nonexistent_xyz_123.py check this"
        result = self._run(
            ctx.preprocess_context_references_async(
                msg, cwd=tmp_path, context_length=128000
            )
        )
        # Warning produced but not blocked
        assert len(result.warnings) > 0
        assert any("not found" in w or "nonexistent" in w for w in result.warnings)

    def test_binary_file_produces_warning(self, tmp_path):
        ctx = _import_ctx()
        f = tmp_path / "binary.bin"
        f.write_bytes(b"\x00\x01binary content" * 20)

        msg = f"@file:{f} show contents"
        result = self._run(
            ctx.preprocess_context_references_async(
                msg, cwd=tmp_path, context_length=128000
            )
        )
        assert any("binary" in w.lower() for w in result.warnings)

    def test_folder_reference_expanded(self, tmp_path):
        ctx = _import_ctx()
        # Create a small directory structure
        (tmp_path / "src").mkdir()
        (tmp_path / "src" / "main.py").write_text("# main\n")
        (tmp_path / "src" / "utils.py").write_text("# utils\n")

        msg = f"list @folder:{tmp_path / 'src'} please"
        result = self._run(
            ctx.preprocess_context_references_async(
                msg, cwd=tmp_path, context_length=128000
            )
        )
        assert result.expanded is True
        assert "main.py" in result.message or "src" in result.message

    def test_hard_limit_blocks_injection(self, tmp_path):
        ctx = _import_ctx()
        # Create a large file — more than 50% of a tiny context window
        large = tmp_path / "large.txt"
        large.write_text("word " * 5000)  # ~5000 tokens

        msg = f"Summarize @file:{large}"
        result = self._run(
            ctx.preprocess_context_references_async(
                msg,
                cwd=tmp_path,
                context_length=100,  # tiny context
            )
        )
        assert result.blocked is True
        assert result.expanded is False
        assert result.message == msg  # original unchanged

    def test_out_of_allowed_root_produces_warning(self, tmp_path):
        ctx = _import_ctx()
        workspace = tmp_path / "workspace"
        workspace.mkdir()
        outside = tmp_path / "secret.txt"
        outside.write_text("secret content\n")

        msg = f"@file:{outside} show me"
        result = self._run(
            ctx.preprocess_context_references_async(
                msg,
                cwd=workspace,
                context_length=128000,
                allowed_root=workspace,  # outside is not in workspace
            )
        )
        assert any(
            "outside" in w.lower() or "allowed" in w.lower() for w in result.warnings
        )

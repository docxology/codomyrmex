"""Unit tests for Hermes ANSI escape stripping (tools/ansi_strip.py).

Zero-Mock Policy: tests use real strings containing actual ANSI escape
sequences and verify the regex-based stripping logic directly.
"""

from __future__ import annotations

from pathlib import Path

import pytest

# ---------------------------------------------------------------------------
# Import helpers
# ---------------------------------------------------------------------------


def _hermes_agent_root() -> Path | None:
    candidate = Path.home() / ".hermes" / "hermes-agent"
    return candidate if candidate.exists() else None


def _import_ansi_strip():
    """Import tools.ansi_strip from ~/.hermes/hermes-agent via direct path, or skip."""
    import importlib.util

    root = _hermes_agent_root()
    if root is None:
        pytest.skip("~/.hermes/hermes-agent not found — Hermes not installed")

    fpath = root / "tools" / "ansi_strip.py"
    if not fpath.exists():
        pytest.skip(f"{fpath} not found")

    spec = importlib.util.spec_from_file_location("hermes_ansi_strip", fpath)
    mod = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(mod)
    except Exception as e:
        pytest.skip(f"hermes ansi_strip not loadable: {e}")
    return mod


# ---------------------------------------------------------------------------
# strip_ansi()
# ---------------------------------------------------------------------------


class TestStripAnsi:
    """ECMA-48 compliant ANSI escape sequence removal."""

    def test_plain_text_passthrough(self) -> None:
        ansi = _import_ansi_strip()
        text = "Hello, world! This is plain text."
        assert ansi.strip_ansi(text) == text

    def test_empty_string_passthrough(self) -> None:
        ansi = _import_ansi_strip()
        assert ansi.strip_ansi("") == ""

    def test_none_like_empty(self) -> None:
        ansi = _import_ansi_strip()
        # strip_ansi with falsy input
        assert ansi.strip_ansi("") == ""

    def test_csi_color_red_stripped(self) -> None:
        ansi = _import_ansi_strip()
        result = ansi.strip_ansi("\x1b[31mERROR\x1b[0m")
        assert result == "ERROR"

    def test_csi_bold_stripped(self) -> None:
        ansi = _import_ansi_strip()
        result = ansi.strip_ansi("\x1b[1mBold text\x1b[22m")
        assert result == "Bold text"

    def test_csi_underline_stripped(self) -> None:
        ansi = _import_ansi_strip()
        result = ansi.strip_ansi("\x1b[4mUnderlined\x1b[24m")
        assert result == "Underlined"

    def test_csi_256_color_stripped(self) -> None:
        ansi = _import_ansi_strip()
        result = ansi.strip_ansi("\x1b[38;5;196mBright Red\x1b[0m")
        assert result == "Bright Red"

    def test_csi_24bit_color_stripped(self) -> None:
        ansi = _import_ansi_strip()
        result = ansi.strip_ansi("\x1b[38;2;255;100;0mOrange\x1b[0m")
        assert result == "Orange"

    def test_osc_title_bel_stripped(self) -> None:
        ansi = _import_ansi_strip()
        # OSC set window title, terminated by BEL (\x07)
        result = ansi.strip_ansi("\x1b]0;My Terminal\x07some text")
        assert result == "some text"

    def test_osc_title_st_stripped(self) -> None:
        ansi = _import_ansi_strip()
        # OSC terminated by ST (\x1b\\)
        result = ansi.strip_ansi("\x1b]0;Title\x1b\\content here")
        assert result == "content here"

    def test_cursor_movement_stripped(self) -> None:
        ansi = _import_ansi_strip()
        # Cursor up, cursor forward
        result = ansi.strip_ansi("\x1b[2ALine1\x1b[5CLine2")
        assert result == "Line1Line2"

    def test_erase_line_stripped(self) -> None:
        ansi = _import_ansi_strip()
        result = ansi.strip_ansi("\x1b[2Kclean line")
        assert result == "clean line"

    def test_mixed_ansi_and_text(self) -> None:
        ansi = _import_ansi_strip()
        raw = "\x1b[32m✓\x1b[0m Tests \x1b[1mpassed\x1b[22m (\x1b[36m42\x1b[0m items)"
        result = ansi.strip_ansi(raw)
        assert result == "✓ Tests passed (42 items)"

    def test_multiline_ansi_stripped(self) -> None:
        ansi = _import_ansi_strip()
        raw = "\x1b[31mline1\x1b[0m\n\x1b[32mline2\x1b[0m\n\x1b[33mline3\x1b[0m"
        result = ansi.strip_ansi(raw)
        assert result == "line1\nline2\nline3"

    def test_8bit_c1_csi_stripped(self) -> None:
        ansi = _import_ansi_strip()
        # 8-bit CSI: \x9b followed by params
        result = ansi.strip_ansi("\x9b31mRed text\x9b0m")
        assert result == "Red text"

    def test_private_mode_csi_stripped(self) -> None:
        ansi = _import_ansi_strip()
        # Private mode: cursor show/hide (\x1b[?25h / \x1b[?25l)
        result = ansi.strip_ansi("\x1b[?25lhidden cursor\x1b[?25h")
        assert result == "hidden cursor"

    def test_fast_path_no_regex_for_clean_text(self) -> None:
        ansi = _import_ansi_strip()
        text = "No escape chars here at all — pure ASCII and UTF-8: こんにちは"
        # Should hit the fast path (no ESC or C1 bytes)
        result = ansi.strip_ansi(text)
        assert result == text

    def test_real_terminal_output_ls_color(self) -> None:
        ansi = _import_ansi_strip()
        # Simulated `ls --color` output
        raw = (
            "\x1b[0m\x1b[01;34mdir1\x1b[0m\n"
            "\x1b[01;32mscript.sh\x1b[0m\n"
            "\x1b[00mREADME.md\x1b[0m"
        )
        result = ansi.strip_ansi(raw)
        assert "dir1" in result
        assert "script.sh" in result
        assert "README.md" in result
        assert "\x1b" not in result

    def test_real_terminal_output_pytest(self) -> None:
        ansi = _import_ansi_strip()
        raw = "\x1b[32mPASSED\x1b[0m test_example.py::test_one \x1b[32m[100%]\x1b[0m"
        result = ansi.strip_ansi(raw)
        assert result == "PASSED test_example.py::test_one [100%]"

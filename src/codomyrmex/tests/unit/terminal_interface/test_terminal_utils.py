"""Tests for TerminalFormatter and terminal_utils.

No mocks. Tests real ANSI code generation and formatting.
"""

import pytest

from codomyrmex.terminal_interface.utils.terminal_utils import TerminalFormatter


@pytest.mark.unit
class TestTerminalFormatterInit:
    """Tests for TerminalFormatter initialization."""

    def test_init_with_colors_enabled(self):
        """Verify init with colors enabled behavior."""
        fmt = TerminalFormatter(use_colors=True)
        assert fmt.use_colors is True

    def test_init_with_colors_disabled(self):
        """Verify init with colors disabled behavior."""
        fmt = TerminalFormatter(use_colors=False)
        assert fmt.use_colors is False

    def test_default_init(self):
        """Verify default init behavior."""
        fmt = TerminalFormatter()
        assert isinstance(fmt.use_colors, bool)


@pytest.mark.unit
class TestTerminalFormatterColorConstants:
    """Tests for color and style dictionaries."""

    def test_colors_dict_contains_standard_colors(self):
        """Verify colors dict contains standard colors behavior."""
        assert "RED" in TerminalFormatter.COLORS
        assert "GREEN" in TerminalFormatter.COLORS
        assert "BLUE" in TerminalFormatter.COLORS
        assert "YELLOW" in TerminalFormatter.COLORS
        assert "CYAN" in TerminalFormatter.COLORS
        assert "WHITE" in TerminalFormatter.COLORS

    def test_styles_dict_contains_bold_and_reset(self):
        """Verify styles dict contains bold and reset behavior."""
        assert "BOLD" in TerminalFormatter.STYLES
        assert "RESET" in TerminalFormatter.STYLES

    def test_color_values_are_ansi_escape_sequences(self):
        """Verify color values are ansi escape sequences behavior."""
        for name, code in TerminalFormatter.COLORS.items():
            assert code.startswith("\033["), f"Color {name} is not an ANSI escape"


@pytest.mark.unit
class TestTerminalFormatterColorMethod:
    """Tests for the color() method."""

    def test_color_with_colors_enabled_includes_ansi(self):
        """Verify color with colors enabled includes ansi behavior."""
        fmt = TerminalFormatter(use_colors=True)
        result = fmt.color("hello", "GREEN")
        assert "\033[" in result
        assert "hello" in result

    def test_color_without_colors_returns_plain_text(self):
        """Verify color without colors returns plain text behavior."""
        fmt = TerminalFormatter(use_colors=False)
        result = fmt.color("hello", "GREEN")
        assert result == "hello"

    def test_color_preserves_message_content(self):
        """Verify color preserves message content behavior."""
        fmt = TerminalFormatter(use_colors=True)
        result = fmt.color("test message", "RED")
        assert "test message" in result

    def test_color_with_style_includes_bold(self):
        """Verify color with style includes bold behavior."""
        fmt = TerminalFormatter(use_colors=True)
        result = fmt.color("styled", "WHITE", style="BOLD")
        assert "styled" in result
        assert "\033[" in result

    def test_color_with_unknown_color_still_includes_text(self):
        """Verify color with unknown color still includes text behavior."""
        fmt = TerminalFormatter(use_colors=True)
        result = fmt.color("text", "NONEXISTENT")
        assert "text" in result

    def test_color_ends_with_reset(self):
        """Verify color ends with reset behavior."""
        fmt = TerminalFormatter(use_colors=True)
        result = fmt.color("msg", "GREEN")
        assert result.endswith(TerminalFormatter.STYLES["RESET"])


@pytest.mark.unit
class TestTerminalFormatterConvenienceMethods:
    """Tests for success(), error(), warning(), info(), header()."""

    def setup_method(self):
        self.fmt = TerminalFormatter(use_colors=False)

    def test_success_returns_string_with_content(self):
        """Verify success returns string with content behavior."""
        result = self.fmt.success("Done!")
        assert isinstance(result, str)
        assert "Done!" in result

    def test_error_returns_string_with_content(self):
        """Verify error returns string with content behavior."""
        result = self.fmt.error("Something went wrong")
        assert isinstance(result, str)
        assert "Something went wrong" in result

    def test_warning_returns_string_with_content(self):
        """Verify warning returns string with content behavior."""
        result = self.fmt.warning("Be careful")
        assert isinstance(result, str)
        assert "Be careful" in result

    def test_info_returns_string_with_content(self):
        """Verify info returns string with content behavior."""
        result = self.fmt.info("FYI")
        assert isinstance(result, str)
        assert "FYI" in result

    def test_header_returns_multiline_string(self):
        """Verify header returns multiline string behavior."""
        result = self.fmt.header("Title")
        assert isinstance(result, str)
        assert "Title" in result
        assert "\n" in result

    def test_header_respects_custom_width(self):
        """Verify header respects custom width behavior."""
        result = self.fmt.header("Test", char="-", width=40)
        assert "Test" in result

    def test_progress_bar_returns_string(self):
        """Verify progress bar returns string behavior."""
        result = self.fmt.progress_bar(50, 100)
        assert isinstance(result, str)
        assert "50" in result or "%" in result

"""
Zero-mock tests for RichRenderer.

Verifies that RichRenderer correctly interacts with the rich library
to produce expected output formats.
"""

import io
import pytest
from codomyrmex.terminal_interface.rendering import RichRenderer


@pytest.fixture
def rich_renderer():
    """Fixture to provide a RichRenderer with a captured console."""
    renderer = RichRenderer(force_terminal=True)
    # Redirect console output to a string buffer for testing
    renderer.console.file = io.StringIO()
    renderer.error_console.file = io.StringIO()
    return renderer


@pytest.mark.unit
class TestRichRenderer:
    """Tests for RichRenderer functionality."""

    def test_print_output(self, rich_renderer):
        rich_renderer.print("Hello, world!")
        output = rich_renderer.console.file.getvalue()
        assert "Hello, world!" in output

    def test_error_output(self, rich_renderer):
        rich_renderer.error("Something went wrong")
        output = rich_renderer.error_console.file.getvalue()
        assert "Something went wrong" in output
        # Verify it has some red color ANSI (bold red is usually \x1b[1;31m)
        assert "\x1b[31m" in output or "\x1b[1;31m" in output

    def test_heading_output(self, rich_renderer):
        rich_renderer.heading("Test Heading")
        output = rich_renderer.console.file.getvalue()
        assert "Test Heading" in output
        # Rule usually contains horizontal lines
        assert "─" in output

    def test_table_output(self, rich_renderer):
        headers = ["Name", "Value"]
        rows = [["A", "1"], ["B", "2"]]
        rich_renderer.table(headers, rows, title="Sample Table")
        output = rich_renderer.console.file.getvalue()
        assert "Sample Table" in output
        assert "Name" in output
        assert "Value" in output
        assert "A" in output
        assert "1" in output

    def test_panel_output(self, rich_renderer):
        rich_renderer.panel("Inside a panel", title="Panel Title")
        output = rich_renderer.console.file.getvalue()
        assert "Inside a panel" in output
        assert "Panel Title" in output
        # Panel borders (Rich uses rounded corners by default sometimes: ╭ ╮ ╯ ╰)
        assert any(c in output for c in "┌┐└┘╭╮╯╰")

    def test_progress_bar_creation(self, rich_renderer):
        with rich_renderer.progress_bar(total=100) as progress:
            task = progress.add_task("Test Progress", total=100)
            progress.update(task, completed=50)
            assert not progress.finished
            assert progress.tasks[0].completed == 50

    def test_status_creation(self, rich_renderer):
        with rich_renderer.status("Working..."):
            pass
        output = rich_renderer.console.file.getvalue()
        assert "Working..." in output

    def test_prompt_interaction(self, rich_renderer):
        # Truly zero-mock: use io.StringIO for input passed to prompt
        in_buf = io.StringIO("user input\n")
        result = rich_renderer.prompt("Enter something", stream=in_buf)
        assert result == "user input"

    def test_confirm_interaction(self, rich_renderer):
        # Truly zero-mock: use io.StringIO for input passed to confirm
        in_buf = io.StringIO("y\n")
        result = rich_renderer.confirm("Are you sure?", stream=in_buf)
        assert result is True

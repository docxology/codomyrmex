"""Tests for developer tools CLI commands."""

import shutil
import pytest

from codomyrmex.agentic_memory.obsidian.cli import ObsidianCLI, ObsidianCLINotAvailable
from codomyrmex.agentic_memory.obsidian.developer import (
    ConsoleEntry,
    cdp_command, debug_toggle, eval_js,
    get_console_log, get_css, get_dom, get_errors,
    mobile_toggle, screenshot, toggle_devtools,
)


class TestConsoleEntry:
    def test_create(self):
        e = ConsoleEntry(level="warn", message="Deprecation warning")
        assert e.level == "warn"

    def test_defaults(self):
        e = ConsoleEntry()
        assert e.level == "log"
        assert e.message == ""


class TestConsoleLogParsing:
    def test_bracketed_prefix(self):
        line = "[WARN] Something went wrong"
        stripped = line.strip()
        level = "log"
        message = stripped
        if stripped.startswith("["):
            bracket_end = stripped.find("]")
            if bracket_end > 0:
                level = stripped[1:bracket_end].lower()
                message = stripped[bracket_end + 1:].strip()
        assert level == "warn"
        assert message == "Something went wrong"

    def test_no_prefix(self):
        line = "Regular log message"
        assert line.strip().startswith("[") is False

    def test_error_level(self):
        line = "[ERROR] Fatal crash"
        stripped = line.strip()
        bracket_end = stripped.find("]")
        level = stripped[1:bracket_end].lower()
        assert level == "error"


class TestDeveloperUnavailable:
    def _cli(self):
        return ObsidianCLI(binary="__nonexistent__")

    def test_toggle_devtools(self):
        with pytest.raises(ObsidianCLINotAvailable):
            toggle_devtools(self._cli())

    def test_eval_js(self):
        with pytest.raises(ObsidianCLINotAvailable):
            eval_js(self._cli(), "console.log('test')")

    def test_screenshot(self):
        with pytest.raises(ObsidianCLINotAvailable):
            screenshot(self._cli())

    def test_screenshot_with_path(self):
        with pytest.raises(ObsidianCLINotAvailable):
            screenshot(self._cli(), path="screenshot.png")

    def test_get_console_log(self):
        with pytest.raises(ObsidianCLINotAvailable):
            get_console_log(self._cli())

    def test_get_console_log_with_params(self):
        with pytest.raises(ObsidianCLINotAvailable):
            get_console_log(self._cli(), limit=10, level="warn", clear=True)

    def test_get_errors(self):
        with pytest.raises(ObsidianCLINotAvailable):
            get_errors(self._cli())

    def test_get_errors_with_clear(self):
        with pytest.raises(ObsidianCLINotAvailable):
            get_errors(self._cli(), clear=True)

    def test_get_dom(self):
        with pytest.raises(ObsidianCLINotAvailable):
            get_dom(self._cli(), ".workspace")

    def test_get_dom_full_params(self):
        with pytest.raises(ObsidianCLINotAvailable):
            get_dom(
                self._cli(), ".workspace",
                attr="class", total=True, text=True, inner=True, all=True,
            )

    def test_get_css(self):
        with pytest.raises(ObsidianCLINotAvailable):
            get_css(self._cli(), ".workspace")

    def test_get_css_with_prop(self):
        with pytest.raises(ObsidianCLINotAvailable):
            get_css(self._cli(), ".workspace", prop="background-color")

    def test_debug_toggle(self):
        with pytest.raises(ObsidianCLINotAvailable):
            debug_toggle(self._cli(), "on")

    def test_cdp_command(self):
        with pytest.raises(ObsidianCLINotAvailable):
            cdp_command(self._cli(), "Page.captureScreenshot")

    def test_cdp_command_with_params(self):
        with pytest.raises(ObsidianCLINotAvailable):
            cdp_command(
                self._cli(), "Runtime.evaluate",
                params='{"expression":"1+1"}',
            )

    def test_mobile_toggle(self):
        with pytest.raises(ObsidianCLINotAvailable):
            mobile_toggle(self._cli(), "on")

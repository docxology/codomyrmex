"""Developer tools CLI commands.

Wraps ``obsidian devtools``, ``obsidian eval``, ``obsidian dev:*`` CLI
commands for debugging, inspecting, and controlling the Obsidian application.
Includes CDP debugger support and mobile emulation.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from codomyrmex.agentic_memory.obsidian.cli import CLIResult, ObsidianCLI


@dataclass
class ConsoleEntry:
    """A single console log entry from the Obsidian app."""

    level: str = "log"  # log, warn, error, debug
    message: str = ""
    raw: str = ""


def toggle_devtools(
    cli: ObsidianCLI,
    *,
    vault: str | None = None,
) -> CLIResult:
    """Toggle the Electron developer tools.

    Maps to ``obsidian devtools``.
    """
    return cli.run("devtools", vault=vault)


def eval_js(
    cli: ObsidianCLI,
    code: str,
    *,
    vault: str | None = None,
) -> str:
    """Execute JavaScript in the Obsidian app context and return the result.

    Maps to ``obsidian eval code="<js>"``.

    .. warning::
        This runs code directly in the Electron process. Use with caution.

    Example::

        file_count = eval_js(cli, 'app.vault.getFiles().length')
    """
    return cli.run("eval", vault=vault, params={"code": code}).stdout


def screenshot(
    cli: ObsidianCLI,
    *,
    path: str | None = None,
    vault: str | None = None,
) -> CLIResult:
    """Capture a screenshot of the Obsidian UI.

    Maps to ``obsidian dev:screenshot [path=<filename.png>]``.
    Returns base64 PNG if no path is given.
    """
    params: dict[str, str] = {}
    if path:
        params["path"] = path
    return cli.run("dev:screenshot", vault=vault, params=params or None)


def get_console_log(
    cli: ObsidianCLI,
    *,
    limit: int | None = None,
    level: str | None = None,
    clear: bool = False,
    vault: str | None = None,
) -> list[ConsoleEntry]:
    """Retrieve recent console log entries.

    Maps to ``obsidian dev:console [limit=<n>] [level=...] [clear]``.
    """
    params: dict[str, str] = {}
    flags: list[str] = []
    if limit is not None:
        params["limit"] = str(limit)
    if level:
        params["level"] = level
    if clear:
        flags.append("clear")

    result = cli.run("dev:console", vault=vault, params=params or None, flags=flags)
    entries: list[ConsoleEntry] = []
    for line in result.lines:
        stripped = line.strip()
        entry_level = "log"
        message = stripped
        if stripped.startswith("["):
            bracket_end = stripped.find("]")
            if bracket_end > 0:
                entry_level = stripped[1:bracket_end].lower()
                message = stripped[bracket_end + 1:].strip()
        entries.append(ConsoleEntry(level=entry_level, message=message, raw=line))
    return entries


def get_errors(
    cli: ObsidianCLI,
    *,
    clear: bool = False,
    vault: str | None = None,
) -> list[str]:
    """Retrieve recent JS error messages from the app.

    Maps to ``obsidian dev:errors [clear]``.
    """
    flags = ["clear"] if clear else []
    result = cli.run("dev:errors", vault=vault, flags=flags)
    return result.lines


def get_dom(
    cli: ObsidianCLI,
    selector: str,
    *,
    attr: str | None = None,
    css: str | None = None,
    total: bool = False,
    text: bool = False,
    inner: bool = False,
    all: bool = False,
    vault: str | None = None,
) -> CLIResult:
    """Query DOM elements matching a CSS selector.

    Maps to ``obsidian dev:dom selector=<css>
    [attr=<name>] [css=<prop>] [total] [text] [inner] [all]``.
    """
    params: dict[str, str] = {"selector": selector}
    flags: list[str] = []
    if attr:
        params["attr"] = attr
    if css:
        params["css"] = css
    if total:
        flags.append("total")
    if text:
        flags.append("text")
    if inner:
        flags.append("inner")
    if all:
        flags.append("all")
    return cli.run("dev:dom", vault=vault, params=params, flags=flags)


def get_css(
    cli: ObsidianCLI,
    selector: str,
    *,
    prop: str | None = None,
    vault: str | None = None,
) -> CLIResult:
    """Inspect CSS for elements matching a selector.

    Maps to ``obsidian dev:css selector=<css> [prop=<name>]``.
    """
    params: dict[str, str] = {"selector": selector}
    if prop:
        params["prop"] = prop
    return cli.run("dev:css", vault=vault, params=params)


def debug_toggle(
    cli: ObsidianCLI,
    state: str | None = None,
    *,
    vault: str | None = None,
) -> CLIResult:
    """Attach/detach CDP debugger.

    Maps to ``obsidian dev:debug [on|off]``.
    """
    flags = [state] if state in ("on", "off") else []
    return cli.run("dev:debug", vault=vault, flags=flags)


def cdp_command(
    cli: ObsidianCLI,
    method: str,
    *,
    params: str | None = None,
    vault: str | None = None,
) -> CLIResult:
    """Run a Chrome DevTools Protocol (CDP) command.

    Maps to ``obsidian dev:cdp method=<CDP.method> [params=<json>]``.
    """
    cli_params: dict[str, str] = {"method": method}
    if params:
        cli_params["params"] = params
    return cli.run("dev:cdp", vault=vault, params=cli_params)


def mobile_toggle(
    cli: ObsidianCLI,
    state: str | None = None,
    *,
    vault: str | None = None,
) -> CLIResult:
    """Toggle mobile emulation.

    Maps to ``obsidian dev:mobile [on|off]``.
    """
    flags = [state] if state in ("on", "off") else []
    return cli.run("dev:mobile", vault=vault, flags=flags)

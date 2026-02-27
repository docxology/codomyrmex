"""Core Obsidian CLI wrapper — subprocess invocation, output parsing.

Wraps the ``obsidian`` CLI binary (requires Obsidian ≥1.12 with CLI enabled).
Provides structured result objects, output format support (json, tsv, csv),
and graceful unavailability handling.

The Obsidian app must be running for CLI commands to succeed.
"""

from __future__ import annotations

import json
import logging
import shutil
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Sequence

logger = logging.getLogger(__name__)


# ── exceptions ───────────────────────────────────────────────────────


class ObsidianCLINotAvailable(RuntimeError):
    """Raised when the ``obsidian`` binary cannot be found on PATH."""


class ObsidianCLIError(RuntimeError):
    """Raised when the ``obsidian`` CLI returns a non-zero exit code."""

    def __init__(self, returncode: int, stderr: str, cmd: list[str]) -> None:
        self.returncode = returncode
        self.stderr = stderr
        self.cmd = cmd
        super().__init__(
            f"obsidian CLI exited with code {returncode}: {stderr.strip()}"
        )


# ── result dataclass ─────────────────────────────────────────────────


@dataclass
class CLIResult:
    """Structured result from an Obsidian CLI invocation."""

    command: str
    stdout: str = ""
    stderr: str = ""
    returncode: int = 0
    lines: list[str] = field(default_factory=list)
    json_data: Any = None

    @property
    def ok(self) -> bool:
        """Return ``True`` when the command succeeded."""
        return self.returncode == 0

    @property
    def text(self) -> str:
        """Trimmed stdout."""
        return self.stdout.strip()


# ── core wrapper ─────────────────────────────────────────────────────


class ObsidianCLI:
    """Wrapper around the ``obsidian`` CLI binary.

    Parameters
    ----------
    binary : str
        Name or absolute path of the Obsidian CLI executable.
    vault : str | Path | None
        Default vault name or path.  Passed as ``vault=<value>`` to every
        command unless overridden per-call.
    timeout : float
        Maximum seconds to wait for a command to complete.
    """

    def __init__(
        self,
        *,
        binary: str = "obsidian",
        vault: str | Path | None = None,
        timeout: float = 30.0,
    ) -> None:
        self._binary = binary
        self._vault = str(vault) if vault else None
        self._timeout = timeout

    # ── availability ─────────────────────────────────────────────

    @staticmethod
    def is_available(binary: str = "obsidian") -> bool:
        """Return ``True`` if the CLI binary is found on ``PATH``."""
        return shutil.which(binary) is not None

    def _ensure_available(self) -> None:
        if not self.is_available(self._binary):
            raise ObsidianCLINotAvailable(
                f"Obsidian CLI binary '{self._binary}' not found on PATH. "
                "Install Obsidian ≥1.12 and enable Settings → General → CLI."
            )

    # ── command building ─────────────────────────────────────────

    def _build_argv(
        self,
        command: str,
        *,
        vault: str | None = None,
        params: dict[str, str] | None = None,
        flags: Sequence[str] = (),
    ) -> list[str]:
        """Assemble the full argv list for :func:`subprocess.run`.

        Vault targeting is placed before the command per CLI spec.
        Parameters use ``key=value`` syntax (values with spaces are quoted).
        Flags are boolean switches (``--flag`` or bare words like ``open``).
        """
        argv: list[str] = [self._binary]

        # Vault targeting (must come before command)
        effective_vault = vault or self._vault
        if effective_vault:
            argv.append(f"vault={effective_vault}")

        argv.append(command)

        # Named parameters  key=value
        if params:
            for k, v in params.items():
                argv.append(f'{k}={v}')

        # Boolean flags — bare words or already prefixed
        for flag in flags:
            argv.append(flag)

        return argv

    # ── execution ────────────────────────────────────────────────

    def run(
        self,
        command: str,
        *,
        vault: str | None = None,
        params: dict[str, str] | None = None,
        flags: Sequence[str] = (),
        parse_json: bool = False,
        timeout: float | None = None,
    ) -> CLIResult:
        """Execute an Obsidian CLI command and return a :class:`CLIResult`.

        Parameters
        ----------
        command : str
            The CLI command, e.g. ``"files"``, ``"daily:read"``.
        vault : str | None
            Override the default vault for this call.
        params : dict[str, str] | None
            Named key=value parameters.
        flags : Sequence[str]
            Boolean flags (``open``, ``newtab``, ``overwrite``, ``--copy``).
        parse_json : bool
            If ``True``, attempt to parse stdout as JSON into
            ``CLIResult.json_data``.
        timeout : float | None
            Override the default timeout for this call.

        Returns
        -------
        CLIResult
            Structured result object.

        Raises
        ------
        ObsidianCLINotAvailable
            If the binary is not on PATH.
        ObsidianCLIError
            If the command exits with a non-zero status.
        """
        self._ensure_available()

        argv = self._build_argv(
            command, vault=vault, params=params, flags=flags
        )

        logger.debug("Running Obsidian CLI: %s", " ".join(argv))

        proc = subprocess.run(
            argv,
            capture_output=True,
            text=True,
            timeout=timeout or self._timeout,
        )

        result = CLIResult(
            command=command,
            stdout=proc.stdout,
            stderr=proc.stderr,
            returncode=proc.returncode,
            lines=[
                line
                for line in proc.stdout.splitlines()
                if line.strip()
            ],
        )

        if parse_json and result.stdout.strip():
            try:
                result.json_data = json.loads(result.stdout)
            except json.JSONDecodeError:
                logger.debug("CLI output is not valid JSON for command %s", command)

        if proc.returncode != 0:
            raise ObsidianCLIError(proc.returncode, proc.stderr, argv)

        return result

    # ── general commands ─────────────────────────────────────────

    def version(self) -> str:
        """Return the Obsidian version string."""
        return self.run("version").text

    def reload(self, *, vault: str | None = None) -> CLIResult:
        """Reload the app window."""
        return self.run("reload", vault=vault)

    def restart(self) -> CLIResult:
        """Restart the Obsidian application."""
        return self.run("restart")

    def help(self, command: str | None = None) -> str:
        """Return CLI help text, optionally for a specific command."""
        if command:
            return self.run("help", params={"": command}).text
        return self.run("help").text

    # ── files & folders ──────────────────────────────────────────

    def file_info(
        self,
        *,
        file: str | None = None,
        path: str | None = None,
        vault: str | None = None,
    ) -> CLIResult:
        """Show file info (name, path, extension, size, created, modified).

        Maps to ``obsidian file [file=<name>|path=<path>]``.
        """
        params = _file_or_path(file, path)
        return self.run("file", vault=vault, params=params or None)

    def list_files(
        self,
        *,
        folder: str | None = None,
        ext: str | None = None,
        total: bool = False,
        vault: str | None = None,
    ) -> list[str]:
        """List files in the vault.

        Maps to ``obsidian files [folder=<path>] [ext=<ext>] [total]``.
        """
        params: dict[str, str] = {}
        flags: list[str] = []
        if folder:
            params["folder"] = folder
        if ext:
            params["ext"] = ext
        if total:
            flags.append("total")
        result = self.run("files", vault=vault, params=params or None, flags=flags)
        return result.lines

    def folder_info(
        self,
        path: str,
        *,
        info: str | None = None,
        vault: str | None = None,
    ) -> CLIResult:
        """Show folder info.

        Maps to ``obsidian folder path=<path> [info=files|folders|size]``.
        """
        params: dict[str, str] = {"path": path}
        if info:
            params["info"] = info
        return self.run("folder", vault=vault, params=params)

    def list_folders(
        self,
        *,
        folder: str | None = None,
        total: bool = False,
        vault: str | None = None,
    ) -> list[str]:
        """List folders in the vault.

        Maps to ``obsidian folders [folder=<path>] [total]``.
        """
        params: dict[str, str] = {}
        flags: list[str] = []
        if folder:
            params["folder"] = folder
        if total:
            flags.append("total")
        result = self.run("folders", vault=vault, params=params or None, flags=flags)
        return result.lines

    def open_file(
        self,
        *,
        file: str | None = None,
        path: str | None = None,
        newtab: bool = False,
        vault: str | None = None,
    ) -> CLIResult:
        """Open a file in Obsidian.

        Maps to ``obsidian open [file=<name>|path=<path>] [newtab]``.
        """
        params = _file_or_path(file, path)
        flags = ["newtab"] if newtab else []
        return self.run("open", vault=vault, params=params or None, flags=flags)

    def read_file(
        self,
        *,
        file: str | None = None,
        path: str | None = None,
        vault: str | None = None,
    ) -> str:
        """Read a file's content via CLI.

        Maps to ``obsidian read [file=<name>|path=<path>]``.
        Targets the active file if neither ``file`` nor ``path`` is given.
        """
        params = _file_or_path(file, path)
        return self.run("read", vault=vault, params=params or None).stdout

    def create_file(
        self,
        *,
        name: str | None = None,
        path: str | None = None,
        content: str | None = None,
        template: str | None = None,
        overwrite: bool = False,
        open: bool = False,
        newtab: bool = False,
        vault: str | None = None,
    ) -> CLIResult:
        """Create or overwrite a file.

        Maps to ``obsidian create [name=<name>] [path=<path>]
        [content=<text>] [template=<name>] [overwrite] [open] [newtab]``.
        """
        params: dict[str, str] = {}
        flags: list[str] = []
        if name:
            params["name"] = name
        if path:
            params["path"] = path
        if content is not None:
            params["content"] = content
        if template:
            params["template"] = template
        if overwrite:
            flags.append("overwrite")
        if open:
            flags.append("open")
        if newtab:
            flags.append("newtab")
        return self.run("create", vault=vault, params=params or None, flags=flags)

    def append_file(
        self,
        content: str,
        *,
        file: str | None = None,
        path: str | None = None,
        inline: bool = False,
        vault: str | None = None,
    ) -> CLIResult:
        """Append content to a file.

        Maps to ``obsidian append [file=|path=] content=<text> [inline]``.
        """
        params = _file_or_path(file, path)
        params["content"] = content
        flags = ["inline"] if inline else []
        return self.run("append", vault=vault, params=params, flags=flags)

    def prepend_file(
        self,
        content: str,
        *,
        file: str | None = None,
        path: str | None = None,
        inline: bool = False,
        vault: str | None = None,
    ) -> CLIResult:
        """Prepend content to a file (after frontmatter).

        Maps to ``obsidian prepend [file=|path=] content=<text> [inline]``.
        """
        params = _file_or_path(file, path)
        params["content"] = content
        flags = ["inline"] if inline else []
        return self.run("prepend", vault=vault, params=params, flags=flags)

    def move_file(
        self,
        to: str,
        *,
        file: str | None = None,
        path: str | None = None,
        vault: str | None = None,
    ) -> CLIResult:
        """Move/rename a file (updates links).

        Maps to ``obsidian move [file=|path=] to=<path>``.
        """
        params = _file_or_path(file, path)
        params["to"] = to
        return self.run("move", vault=vault, params=params)

    def rename_file(
        self,
        name: str,
        *,
        file: str | None = None,
        path: str | None = None,
        vault: str | None = None,
    ) -> CLIResult:
        """Rename a file.

        Maps to ``obsidian rename [file=|path=] name=<name>``.
        """
        params = _file_or_path(file, path)
        params["name"] = name
        return self.run("rename", vault=vault, params=params)

    def delete_file(
        self,
        *,
        file: str | None = None,
        path: str | None = None,
        permanent: bool = False,
        vault: str | None = None,
    ) -> CLIResult:
        """Delete a file (to trash by default).

        Maps to ``obsidian delete [file=|path=] [permanent]``.
        """
        params = _file_or_path(file, path)
        flags = ["permanent"] if permanent else []
        return self.run("delete", vault=vault, params=params or None, flags=flags)


# ── helpers ──────────────────────────────────────────────────────────


def _file_or_path(
    file: str | None = None,
    path: str | None = None,
) -> dict[str, str]:
    """Build the file/path param dict from optional arguments."""
    params: dict[str, str] = {}
    if file:
        params["file"] = file
    elif path:
        params["path"] = path
    return params

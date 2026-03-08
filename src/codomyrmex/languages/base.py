"""Base class for language managers (template-method pattern).

All language managers inherit from ``BaseLanguageManager`` and configure:

* ``_check_commands`` – one or more commands used to verify the toolchain is
  installed.  Each entry is a ``list[str]`` passed to ``subprocess.run``.
* Language-specific implementations of ``install_instructions``,
  ``setup_project``, and ``use_script``.
"""

from __future__ import annotations

import contextlib
import os
import subprocess


class BaseLanguageManager:
    """Template base class for programming language managers.

    Subclasses must define :attr:`_check_commands` and implement the three
    abstract-like methods: :meth:`install_instructions`, :meth:`setup_project`,
    and :meth:`use_script`.
    """

    # Each entry is a command (list of strings) that must exit 0 for the
    # language to be considered "installed".  Most languages need only one
    # entry; Java needs both ``javac`` and ``java``.
    _check_commands: list[list[str]] = []

    def is_installed(self) -> bool:
        """Return True if every command in :attr:`_check_commands` succeeds."""
        try:
            for cmd in self._check_commands:
                subprocess.run(cmd, check=True, capture_output=True)
            return True
        except (FileNotFoundError, subprocess.CalledProcessError):
            return False

    def _cleanup(self, files: list[str]) -> None:
        """Remove temporary files, silently ignoring missing-file errors."""
        for path in files:
            with contextlib.suppress(OSError):
                os.remove(path)

    def install_instructions(self) -> str:
        """Return markdown instructions for installing the language toolchain."""
        raise NotImplementedError

    def setup_project(self, path: str) -> bool:
        """Initialise a new project in *path*; return True on success."""
        raise NotImplementedError

    def use_script(self, script_content: str, dir_path: str | None = None) -> str:
        """Write *script_content* to a temp file and execute it, returning output."""
        raise NotImplementedError

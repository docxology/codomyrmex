"""Fail a test that spawns an environment-mutating ``uv`` command.

The suite shares one virtual environment. `uv add`, `uv remove`, `uv lock` and
`uv sync` re-resolve that environment against `.python-version`, and when the
running interpreter differs uv **deletes and recreates `.venv`** — while the
session is importing from it. Measured on the 3.12 matrix leg: `.venv` finished
the run as a 3.11 environment holding 165 packages, and the failures landed in
unrelated modules as `ModuleNotFoundError` hours after the destructive test had
passed.

The static gate in `tests/unit/release/test_environment_safety.py` reads argv
from the test tree. It cannot see a spawn that production code performs on a
test's behalf — `HermesClient._heal_environment` runs `uv add <pkg>` in whatever
directory the process is in — so this runtime guard covers the same rule from
the other side: whatever the caller, a mutating `uv` spawn during a test fails
that test and names the calling `file:line`.

`uv run` is only a mutation when it is reached from the repository root without
`--no-sync`: that is where `.python-version` lives and where the rebuild
happens. `uv build`, `uv init`, `uv pip list` and `uv --version` do not touch the
project environment and are left alone.
"""

from __future__ import annotations

import os
import subprocess
import traceback
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Any

import pytest

if TYPE_CHECKING:
    from collections.abc import Generator

MUTATING_VERBS = frozenset({"add", "remove", "sync", "lock"})
RUN_VERB = "run"
SYNC_SUPPRESSING_FLAGS = frozenset({"--no-sync", "--frozen", "--offline"})


@dataclass(frozen=True)
class Violation:
    """One environment-mutating uv spawn, with the code that asked for it."""

    argv: tuple[str, ...]
    cwd: str
    reason: str
    caller: str

    def describe(self) -> str:
        return (
            f"{self.reason}\n"
            f"    argv = {list(self.argv)}\n"
            f"    cwd  = {self.cwd}\n"
            f"    from = {self.caller}"
        )


def _verb(argv: tuple[str, ...]) -> str:
    for token in argv[1:]:
        if not token.startswith("-"):
            return token
    return ""


def violation_for(
    argv: tuple[str, ...], cwd: Path, repo_root: Path, *, caller: str = ""
) -> Violation | None:
    """Classify one spawn. Pure, so the classifier can be tested without spawning."""
    if not argv or Path(argv[0]).name not in {"uv", "uv.exe"}:
        return None
    verb = _verb(argv)
    if verb in MUTATING_VERBS:
        return Violation(
            argv,
            str(cwd),
            f"`uv {verb}` re-resolves and rewrites the shared project environment",
            caller,
        )
    if verb == RUN_VERB and not SYNC_SUPPRESSING_FLAGS.intersection(argv):
        try:
            inside_repository = Path(cwd).resolve().is_relative_to(repo_root.resolve())
        except OSError:
            return None
        if not inside_repository:
            return None
        return Violation(
            argv,
            str(cwd),
            "`uv run` from the repository root without `--no-sync` rebuilds .venv "
            "against .python-version when the running interpreter differs",
            caller,
        )
    return None


def _caller_chain() -> str:
    frames = [
        f"{Path(frame.filename).name}:{frame.lineno} in {frame.name}"
        for frame in traceback.extract_stack()
        if "uv_spawns" not in frame.filename
        and "subprocess.py" not in frame.filename
        and "conftest.py" not in frame.filename
    ]
    return " <- ".join(reversed(frames[-4:]))


class UvSpawnGuard:
    """pytest plugin that patches ``subprocess.Popen`` and fails the caller."""

    def __init__(self, config: pytest.Config, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.is_worker = hasattr(config, "workerinput")
        self.current_test: str | None = None
        self.current: list[Violation] = []
        self.by_test: dict[str, list[str]] = {}
        self.outside_tests: list[str] = []
        self._original_init = subprocess.Popen.__init__
        self._install()

    def _install(self) -> None:
        original = self._original_init
        guard = self

        def patched(
            popen_self: subprocess.Popen, args: Any, *positional: Any, **keyword: Any
        ) -> None:
            guard._inspect(args, keyword)
            original(popen_self, args, *positional, **keyword)

        subprocess.Popen.__init__ = patched  # type: ignore[method-assign]

    def uninstall(self) -> None:
        subprocess.Popen.__init__ = self._original_init  # type: ignore[method-assign]

    def _inspect(self, args: Any, keyword: dict[str, Any]) -> None:
        try:
            if isinstance(args, str | bytes):
                return
            argv = tuple(str(item) for item in args)
            cwd_option = keyword.get("cwd")
            cwd = Path(cwd_option) if cwd_option is not None else Path(os.getcwd())
            violation = violation_for(argv, cwd, self.repo_root, caller=_caller_chain())
            if violation is None:
                return
            if self.current_test is None:
                self.outside_tests.append(violation.describe())
            else:
                self.current.append(violation)
        except Exception:  # a guard must never break an unrelated spawn
            return

    def pytest_runtest_setup(self, item: pytest.Item) -> None:
        self.current_test = item.nodeid
        self.current = []

    @pytest.hookimpl(wrapper=True)
    def pytest_runtest_makereport(self, item: pytest.Item, call: Any) -> Any:
        """Turn the test's own call report into a failure, naming the caller.

        Failing in teardown instead would raise before pytest finishes its
        setup-state bookkeeping and cascade a spurious error into the next test.
        """
        report = yield
        if getattr(call, "when", None) == "call" and self.current:
            violations, self.current = self.current, []
            report.outcome = "failed"
            report.longrepr = (
                "the test spawned an environment-mutating uv command:\n\n"
                + "\n\n".join(violation.describe() for violation in violations)
            )
        return report

    def pytest_runtest_teardown(
        self, item: pytest.Item, nextitem: pytest.Item | None
    ) -> None:
        # A spawn during teardown has no call report to attach to.
        if self.current:
            self.outside_tests.extend(
                violation.describe() for violation in self.current
            )
        self.current = []
        self.current_test = None

    @pytest.hookimpl(tryfirst=True)
    def pytest_sessionfinish(self, session: pytest.Session) -> None:
        self.uninstall()
        if self.current:
            self.outside_tests.extend(v.describe() for v in self.current)
        if self.outside_tests and session.exitstatus == pytest.ExitCode.OK:
            session.exitstatus = pytest.ExitCode.TESTS_FAILED

    def pytest_terminal_summary(self, terminalreporter: Any) -> None:
        if not self.outside_tests:
            return
        terminalreporter.write_sep("=", "environment-mutating uv spawns")
        for entry in self.outside_tests:
            terminalreporter.write_line(entry)

"""Detect paths that a test run leaves behind in the repository root.

Tests write under ``tmp_path``. A test that calls an API with its default
output location (``./git_analysis/``, ``Path.cwd() / "config_audits"``) instead
creates that path in the working directory, which for a normal run is the
repository root, and the stray directory then outlives the run.

:class:`StrayPathGuard` lists the top-level entries of the repository root --
and of the directory pytest was started from, when that lies inside the
repository -- when the session starts. :class:`StrayPathPlugin`, which
``tests/conftest.py`` registers, calls :meth:`StrayPathGuard.note` after every
test, to record which test had just run when a path first appeared, and
:meth:`StrayPathGuard.stray_paths` when the session ends. Only the top level is watched: listing it costs a few
microseconds per test, whereas walking the tree would not.

Set ``CODOMYRMEX_STRAY_PATH_GUARD`` to ``fail`` (default: print a report at
the end of the run and make the run fail), ``warn`` (only print the report)
or ``off``. ``warn`` is for a checkout that other processes write into while
the tests run (an editor, a concurrent agent): the guard cannot tell their
files apart from test output.

The report is made once, by the process that owns the session: the
pytest-xdist controller or a plain single-process run. Workers only send the
controller their per-test hints.
"""

from __future__ import annotations

import fnmatch
import os
from collections.abc import Generator, Iterable, Mapping
from pathlib import Path
from typing import Any

import pytest

MODE_ENV = "CODOMYRMEX_STRAY_PATH_GUARD"
MODES = ("fail", "warn", "off")
DEFAULT_MODE = "fail"

# Written by pytest, its plugins and coverage on every run, not by tests.
TOOL_OUTPUTS = (
    ".pytest_cache",
    ".hypothesis",
    ".benchmarks",
    ".coverage",
    ".coverage.*",
    "coverage.xml",
    "coverage.json",
    "coverage.lcov",
    "coverage.md",
    "htmlcov",
    "junit*.xml",
)


def guard_mode(environ: Mapping[str, str] = os.environ) -> str:
    """Return the configured guard mode, rejecting unknown values."""
    mode = environ.get(MODE_ENV, "").strip().lower() or DEFAULT_MODE
    if mode not in MODES:
        msg = f"{MODE_ENV} must be one of {', '.join(MODES)}; got {mode!r}"
        raise ValueError(msg)
    return mode


class StrayPathGuard:
    """Track new top-level entries in the watched directories.

    Args:
        repo_root: Repository root; reported paths are relative to it.
        invocation_dir: Directory pytest was started from. Watched as well
            when it lies inside ``repo_root``; a directory outside the
            repository (``/tmp``) is shared with other processes.
        tool_outputs: Paths that the run itself is configured to write (for
            example ``--basetemp`` or ``--junitxml``); they and their parent
            directories inside the repository are not reported.
    """

    def __init__(
        self,
        repo_root: Path,
        invocation_dir: Path | None = None,
        tool_outputs: Iterable[str | os.PathLike[str]] = (),
    ) -> None:
        self.repo_root = repo_root.resolve()
        watched = [self.repo_root]
        if invocation_dir is not None:
            start = invocation_dir.resolve()
            if start != self.repo_root and start.is_relative_to(self.repo_root):
                watched.append(start)
        # (directory, prefix of the repository-relative path of its entries)
        self._watched = [(path, self._relative_prefix(path)) for path in watched]
        self._ignored = self._ignored_outputs(tool_outputs)
        self.baseline = self._snapshot()
        self.first_seen: dict[str, str] = {}

    def _relative_prefix(self, directory: Path) -> str:
        relative = directory.relative_to(self.repo_root).as_posix()
        return "" if relative == "." else f"{relative}/"

    def _ignored_outputs(self, outputs: Iterable[str | os.PathLike[str]]) -> set[str]:
        ignored: set[str] = set()
        for output in outputs:
            path = Path(output).resolve()
            if not path.is_relative_to(self.repo_root) or path == self.repo_root:
                continue
            relative = path.relative_to(self.repo_root)
            ignored.update(
                parent.as_posix() for parent in (relative, *relative.parents)
            )
        ignored.discard(".")
        return ignored

    def _snapshot(self) -> frozenset[str]:
        entries: set[str] = set()
        for directory, prefix in self._watched:
            try:
                names = os.listdir(directory)
            except OSError:
                continue
            entries.update(prefix + name for name in names)
        return frozenset(entries)

    def _is_tool_output(self, path: str) -> bool:
        if path in self._ignored:
            return True
        name = path.rsplit("/", 1)[-1]
        return any(fnmatch.fnmatchcase(name, pattern) for pattern in TOOL_OUTPUTS)

    def stray_paths(self) -> list[str]:
        """Return watched entries that exist now but did not at the start."""
        return sorted(
            path
            for path in self._snapshot() - self.baseline
            if not self._is_tool_output(path)
        )

    def note(self, nodeid: str) -> None:
        """Attribute paths that appeared since the last call to *nodeid*."""
        for path in self.stray_paths():
            self.first_seen.setdefault(path, nodeid)


def format_report(paths: Iterable[str], hints: Mapping[str, list[str]]) -> list[str]:
    """Describe each stray path and the tests that had just run when it appeared.

    Under pytest-xdist every worker notes the path after its own current
    test, so a path can carry one hint per worker; the test that created it
    is among them.
    """
    lines = []
    for path in paths:
        seen = hints.get(path)
        detail = f"  (first seen after: {'; '.join(seen)})" if seen else ""
        lines.append(f"{path}{detail}")
    return lines


_WORKER_OUTPUT_KEY = "stray_path_hints"

# pytest-cov report types whose ``--cov-report=TYPE:DEST`` value is a path.
_COVERAGE_FILE_REPORTS = ("html", "xml", "json", "lcov", "markdown", "markdown-append")


def _coverage_report_paths(config: pytest.Config) -> list[str]:
    """Return the report destinations given with ``--cov-report=TYPE:DEST``."""
    reports = getattr(config.option, "cov_report", None)
    if not isinstance(reports, dict):
        return []
    return [
        dest
        for kind, dest in reports.items()
        if kind in _COVERAGE_FILE_REPORTS and dest
    ]


class StrayPathPlugin:
    """pytest plugin that runs a :class:`StrayPathGuard` for the session."""

    def __init__(self, config: pytest.Config, repo_root: Path, mode: str) -> None:
        self.mode = mode
        self.is_worker = hasattr(config, "workerinput")
        outputs = [
            value
            for value in (
                config.option.basetemp,
                getattr(config.option, "xmlpath", None),
                *_coverage_report_paths(config),
            )
            if value
        ]
        self.guard = StrayPathGuard(
            repo_root, config.invocation_params.dir, tool_outputs=outputs
        )
        self.hints: dict[str, list[str]] = {}
        self.report: list[str] = []

    @pytest.hookimpl(wrapper=True)
    def pytest_runtest_protocol(self, item: pytest.Item) -> Generator[None, Any, Any]:
        result = yield
        self.guard.note(item.nodeid)
        return result

    @pytest.hookimpl(optionalhook=True)
    def pytest_testnodedown(self, node: Any, error: object) -> None:
        """Collect the hints a pytest-xdist worker sent with its results."""
        output = getattr(node, "workeroutput", None) or {}
        worker = getattr(getattr(node, "gateway", None), "id", "worker")
        for path, nodeid in output.get(_WORKER_OUTPUT_KEY, {}).items():
            self.hints.setdefault(path, []).append(f"{nodeid} [{worker}]")

    # tryfirst: check before plugins such as junitxml write their own files.
    @pytest.hookimpl(tryfirst=True)
    def pytest_sessionfinish(self, session: pytest.Session) -> None:
        if self.is_worker:
            workeroutput = getattr(session.config, "workeroutput", None)
            if workeroutput is not None:
                workeroutput[_WORKER_OUTPUT_KEY] = dict(self.guard.first_seen)
            return
        for path, nodeid in self.guard.first_seen.items():
            self.hints.setdefault(path, []).append(nodeid)
        stray = self.guard.stray_paths()
        if not stray:
            return
        self.report = format_report(stray, self.hints)
        if self.mode == "fail" and session.exitstatus == pytest.ExitCode.OK:
            session.exitstatus = pytest.ExitCode.TESTS_FAILED

    def pytest_terminal_summary(self, terminalreporter: Any) -> None:
        if not self.report:
            return
        failing = self.mode == "fail"
        terminalreporter.write_sep(
            "=", "paths created in the repository", red=failing, yellow=not failing
        )
        terminalreporter.line(
            "Tests created these paths outside tmp_path. Pass explicit tmp_path-based "
            "paths, or use monkeypatch.chdir(tmp_path):"
        )
        for line in self.report:
            terminalreporter.line(f"  {line}")
        consequence = "This fails the run" if failing else "Warning only"
        terminalreporter.line(
            f"{consequence} ({MODE_ENV}={self.mode}; one of {', '.join(MODES)})."
        )
        if failing:
            terminalreporter.line(
                f"If another process created them during the run, set {MODE_ENV}=warn."
            )

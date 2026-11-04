"""Fail the test that mutates import state.

The 3.12/3.13/3.14 legs report ``No module named 'fitz'``, ``'pandas.api.internals'``
and friends for tests that pass in isolation, seconds after ``find_spec`` resolved
every one of those modules inside the same venv. Something in the session changes
the interpreter's view of the installed packages, and a per-test invariant names it
instead of leaving a slate to be inferred from.

Loaded with ``-p tests.support.session_invariants``; diagnosed only, never part of
the shipped test run.
"""

from __future__ import annotations

import importlib.util
import sys

WATCH = (
    "fitz",
    "pandas",
    "pandas.api.internals",
    "matplotlib",
    "matplotlib.backends.backend_svg",
    "fastapi",
    "fastapi.middleware.cors",
    "hypothesis",
    "hypothesis.internal.conjecture.optimiser",
)


class SessionInvariantPlugin:
    """Compare sys.path and the watched modules against the state after test one."""

    def __init__(self) -> None:
        self.site_packages: set[str] = set()
        self.baseline_path: list[str] | None = None
        self.baseline_modules: dict[str, int] = {}
        self.report: list[str] = []

    def pytest_sessionstart(self, session):  # noqa: ARG002
        self.site_packages = {
            entry for entry in sys.path if "site-packages" in entry or "dist-packages" in entry
        }
        self.report.append(f"sessionstart site-packages: {sorted(self.site_packages)}")
        for name in WATCH:
            try:
                found = importlib.util.find_spec(name) is not None
            except Exception as exc:  # noqa: BLE001 - diagnosis only
                found = f"ERROR {type(exc).__name__}"
            self.report.append(f"sessionstart spec {name}: {found}")

    def pytest_runtest_teardown(self, item, nextitem):  # noqa: ARG002
        if self.baseline_path is None:
            # Collection has finished and one test has run: this is the settled
            # baseline, so collection-time insertions are not reported as a change.
            self.baseline_path = list(sys.path)
            self.baseline_modules = {
                name: id(sys.modules[name]) for name in WATCH if name in sys.modules
            }
            self.report.append(
                f"settled after {item.nodeid}: watched modules {sorted(self.baseline_modules)}"
            )
            return

        problems = []
        current = list(sys.path)
        missing = [entry for entry in self.baseline_path if entry not in current]
        added = [entry for entry in current if entry not in self.baseline_path]
        # Additions are benign and common (a test prepends the project source dir and
        # never removes it). Only a lost entry can make an installed module unreachable,
        # so only a lost entry is fatal; additions are reported for the record.
        if missing:
            problems.append(f"sys.path lost entries (missing={missing}, added={added})")
        elif added:
            self.report.append(f"{item.nodeid} added sys.path entries: {added}")

        lost = [
            entry
            for entry in self.site_packages
            if entry not in current
        ]
        if lost:
            problems.append(f"site-packages dropped from sys.path: {lost}")

        replaced = [
            name
            for name, ident in self.baseline_modules.items()
            if name in sys.modules and id(sys.modules[name]) != ident
        ]
        dropped = [name for name in self.baseline_modules if name not in sys.modules]
        if replaced:
            problems.append(f"modules replaced in sys.modules: {replaced}")
        if dropped:
            problems.append(f"modules dropped from sys.modules: {dropped}")

        if problems:
            raise AssertionError(f"{item.nodeid} mutated import state: {'; '.join(problems)}")


def pytest_configure(config):
    config.pluginmanager.register(SessionInvariantPlugin(), "codomyrmex-session-invariants")


def pytest_terminal_summary(terminalreporter):
    plugin = terminalreporter.config.pluginmanager.get_plugin("codomyrmex-session-invariants")
    if plugin is None:
        return
    terminalreporter.write_sep("=", "session invariants")
    for line in plugin.report:
        terminalreporter.write_line(line)

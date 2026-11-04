"""Capture import state at the moment a test reports a module missing.

The 3.12/3.13/3.14 legs fail with ``No module named 'fitz'`` and friends while
``find_spec`` resolves every one of those modules inside the same venv, in the same
job, seconds earlier. Whatever changes the interpreter's view of the installed
packages changes it during the run, so the diagnostic belongs at the failure, not
in a summary that arrives after thousands of lines of traceback.

Loaded with ``-p tests.support.session_invariants``. Diagnosis only.
"""

from __future__ import annotations

import importlib
import importlib.util
import os
import sys

WATCH = ("fitz", "pandas", "matplotlib", "fastapi", "hypothesis", "mnemonic", "redis")

_LOG = os.environ.get("SESSION_INVARIANT_LOG", "session-invariants.log")


def _emit(line: str) -> None:
    try:
        with open(_LOG, "a", encoding="utf-8") as handle:
            handle.write(f"[pid {os.getpid()}] {line}\n")
    except OSError:
        pass


def _state(module: str) -> str:
    base = module.split(".", maxsplit=1)[0]
    loaded = sys.modules.get(base)
    if loaded is None:
        detail = "loaded=False"
    else:
        detail = (
            f"loaded=True file={getattr(loaded, '__file__', None)!r} "
            f"path={getattr(loaded, '__path__', None)!r}"
        )
    try:
        spec = importlib.util.find_spec(base)
        spec_text = getattr(spec, "origin", spec)
    except Exception as exc:  # diagnosis only: any failure here is data
        spec_text = f"ERROR {type(exc).__name__}: {exc}"
    return f"{base}: {detail} find_spec={spec_text}"


def _machinery(label: str) -> None:
    """Dump the parts of the import system a test can replace."""
    _emit(f"{label} meta_path={[type(f).__name__ for f in sys.meta_path]}")
    _emit(
        f"{label} path_hooks={[getattr(h, '__name__', type(h).__name__) for h in sys.path_hooks]}"
    )
    for entry in sys.path:
        if "site-packages" not in entry:
            continue
        cached = sys.path_importer_cache.get(entry)
        _emit(
            f"{label} importer_cache[{entry}]={type(cached).__name__ if cached else cached!r}"
        )
        try:
            from importlib.machinery import PathFinder

            spec = PathFinder.find_spec("fitz", [entry])
            _emit(f"{label} PathFinder.fit[{entry}]={getattr(spec, 'origin', spec)}")
        except Exception as exc:  # diagnosis only
            _emit(f"{label} PathFinder.fit[{entry}] ERROR {type(exc).__name__}: {exc}")


def _after_invalidate(label: str) -> None:
    """Rebuild the finder caches and ask again: stale cache or genuinely absent?"""
    try:
        importlib.invalidate_caches()
    except Exception as exc:  # diagnosis only
        _emit(f"{label} invalidate_caches ERROR {type(exc).__name__}: {exc}")
        return
    for name in ("fitz", "bs4", "pandas.api.internals", "fastapi.middleware.cors"):
        _emit(f"{label} after_invalidate {_state(name)}")
    for entry, finder in list(sys.path_importer_cache.items()):
        if (
            finder is not None
            and type(finder).__name__ != "FileFinder"
            and type(finder).__name__ != "zipimporter"
        ):
            _emit(f"{label} odd_finder[{entry}]={type(finder).__name__}")


def _snapshot(label: str) -> None:
    _emit(f"{label} cwd={os.getcwd()} executable={sys.executable}")
    _emit(f"{label} site-packages={[p for p in sys.path if 'site-packages' in p]}")
    _emit(f"{label} sys.path={sys.path}")
    _emit(f"{label} modules_loaded={len(sys.modules)}")
    for name in WATCH:
        _emit(f"{label} {_state(name)}")
    _machinery(label)
    _after_invalidate(label)


class MissingModulePlugin:
    """Write the import state whenever a failure blames a missing module."""

    def pytest_sessionstart(self, session):
        _snapshot("SESSIONSTART")

    def pytest_runtest_logreport(self, report):
        if report.when != "call" or not report.failed:
            return
        message = str(report.longrepr)
        if "No module named" not in message and "Cannot import name" not in message:
            return
        _emit(f"FAILURE nodeid={report.nodeid}")
        for line in message.splitlines():
            if "No module named" in line or "Cannot import" in line:
                _emit(f"FAILURE blamed={line.strip()[:300]}")
        _snapshot("FAILURE")


def pytest_configure(config):
    config.pluginmanager.register(MissingModulePlugin(), "codomyrmex-missing-module")


def pytest_sessionfinish(session, exitstatus):
    _emit(f"SESSIONFINISH exitstatus={exitstatus}")
    _snapshot("SESSIONFINISH")

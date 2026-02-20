"""Tests for Sprint 22: Module Triage."""

from __future__ import annotations

import os
import tempfile
from pathlib import Path

import pytest

from codomyrmex.orchestrator.triage_engine import (
    ARCHIVE_SET,
    MERGE_MAP,
    ModuleProfile,
    PROMOTE_SET,
    TriageDecision,
    TriageEngine,
    TriageReport,
)


class TestModuleProfile:
    def test_to_dict(self) -> None:
        p = ModuleProfile("foo", loc=100, file_count=3, decision=TriageDecision.STUB)
        d = p.to_dict()
        assert d["name"] == "foo"
        assert d["decision"] == "stub"


class TestTriageReport:
    def test_summary(self) -> None:
        r = TriageReport(modules=[
            ModuleProfile("a", decision=TriageDecision.PROMOTE),
            ModuleProfile("b", decision=TriageDecision.ARCHIVE),
            ModuleProfile("c", decision=TriageDecision.STUB),
        ])
        s = r.summary()
        assert s["total"] == 3
        assert s["promote"] == 1
        assert s["archive"] == 1
        assert s["stub"] == 1

    def test_filters(self) -> None:
        r = TriageReport(modules=[
            ModuleProfile("x", decision=TriageDecision.MERGE),
            ModuleProfile("y", decision=TriageDecision.ACTIVE),
        ])
        assert len(r.merge) == 1
        assert len(r.active) == 1


class TestTriageEngine:
    def _make_module(self, root: Path, name: str, files: dict[str, str]) -> Path:
        mod = root / name
        mod.mkdir(parents=True, exist_ok=True)
        for fname, content in files.items():
            (mod / fname).write_text(content)
        return mod

    def test_profile_module(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self._make_module(root, "mymod", {
                "__init__.py": "",
                "core.py": "def foo():\n    return 1\n\ndef bar():\n    return 2\n",
            })
            engine = TriageEngine()
            profile = engine.profile_module("mymod", root / "mymod")
            assert profile.file_count == 2
            assert profile.has_init
            assert profile.loc > 0

    def test_archive_decision(self) -> None:
        engine = TriageEngine()
        profile = ModuleProfile("embodiment")
        result = engine._classify(profile)
        assert result == TriageDecision.ARCHIVE

    def test_promote_decision(self) -> None:
        engine = TriageEngine()
        profile = ModuleProfile("wallet", loc=1300)
        result = engine._classify(profile)
        assert result == TriageDecision.PROMOTE

    def test_merge_decision(self) -> None:
        engine = TriageEngine()
        profile = ModuleProfile("cache")
        result = engine._classify(profile)
        assert result == TriageDecision.MERGE
        assert profile.merge_target == "performance/caching"

    def test_active_by_loc(self) -> None:
        engine = TriageEngine()
        profile = ModuleProfile("big_mod", loc=3000, has_tests=True)
        result = engine._classify(profile)
        assert result == TriageDecision.ACTIVE

    def test_active_by_mcp(self) -> None:
        engine = TriageEngine()
        profile = ModuleProfile("api_mod", loc=600, has_mcp_tools=True)
        result = engine._classify(profile)
        assert result == TriageDecision.ACTIVE

    def test_stub_default(self) -> None:
        engine = TriageEngine()
        profile = ModuleProfile("misc_mod", loc=300, file_count=5)
        result = engine._classify(profile)
        assert result == TriageDecision.STUB

    def test_small_archive(self) -> None:
        engine = TriageEngine()
        profile = ModuleProfile("tiny", loc=50, file_count=1)
        result = engine._classify(profile)
        assert result == TriageDecision.ARCHIVE

    def test_triage_all(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self._make_module(root, "mod_a", {"__init__.py": "", "x.py": "a = 1\n"})
            self._make_module(root, "mod_b", {"__init__.py": "", "y.py": "b = 2\n"})
            engine = TriageEngine()
            report = engine.triage_all(root)
            assert len(report.modules) == 2

    def test_missing_dir(self) -> None:
        engine = TriageEngine()
        report = engine.triage_all(Path("/nonexistent_dir"))
        assert len(report.modules) == 0

    def test_constants(self) -> None:
        assert "embodiment" in ARCHIVE_SET
        assert "wallet" in PROMOTE_SET
        assert "cache" in MERGE_MAP

    def test_profile_nonexistent(self) -> None:
        engine = TriageEngine()
        profile = engine.profile_module("ghost", Path("/nonexistent"))
        assert profile.file_count == 0

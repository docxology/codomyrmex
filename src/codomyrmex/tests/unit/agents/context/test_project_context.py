"""Tests for Sprint 18: Project Context & Indexer.

Tests for project.py (ProjectScanner, ToolSelector) and indexer.py (RepoIndexer).
"""

from __future__ import annotations

import os
import tempfile
from pathlib import Path

import pytest

from codomyrmex.agents.context.project import (
    FileInfo,
    ProjectContext,
    ProjectScanner,
    ToolSelector,
)
from codomyrmex.agents.context.indexer import (
    ImportEdge,
    RepoIndex,
    RepoIndexer,
    Symbol,
)


# ── FileInfo / ProjectContext ────────────────────────────────────


class TestFileInfo:
    def test_auto_extension(self) -> None:
        fi = FileInfo(path="module.py")
        assert fi.extension == "py"

    def test_to_dict(self) -> None:
        fi = FileInfo(path="a.py", module="mymod")
        d = fi.to_dict()
        assert d["module"] == "mymod"


class TestProjectContext:
    def test_file_count(self) -> None:
        ctx = ProjectContext(files=[FileInfo("a.py"), FileInfo("b.py")])
        assert ctx.file_count == 2

    def test_files_by_extension(self) -> None:
        ctx = ProjectContext(files=[
            FileInfo("a.py"), FileInfo("b.md"), FileInfo("c.py"),
        ])
        assert len(ctx.files_by_extension("py")) == 2


# ── ProjectScanner ───────────────────────────────────────────────


class TestProjectScanner:
    def test_scan_real_dir(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            Path(tmpdir, "mod").mkdir()
            Path(tmpdir, "mod", "hello.py").write_text("def greet(): pass\n")
            Path(tmpdir, "README.md").write_text("# Readme\n")
            scanner = ProjectScanner()
            ctx = scanner.scan(tmpdir)
            assert ctx.file_count >= 2
            assert ctx.module_count >= 1

    def test_scan_nonexistent(self) -> None:
        scanner = ProjectScanner()
        ctx = scanner.scan("/nonexistent/path")
        assert ctx.file_count == 0


# ── ToolSelector ─────────────────────────────────────────────────


class TestToolSelector:
    def test_python_review(self) -> None:
        ts = ToolSelector()
        tools = ts.select("py", "review")
        assert "code_reviewer" in tools

    def test_toml_audit(self) -> None:
        ts = ToolSelector()
        tools = ts.select("toml", "audit")
        assert "dependency_scanner" in tools

    def test_unknown_type(self) -> None:
        ts = ToolSelector()
        tools = ts.select("xyz", "magic")
        assert tools == []


# ── Symbol / RepoIndex ───────────────────────────────────────────


class TestSymbol:
    def test_to_dict(self) -> None:
        s = Symbol(name="foo", kind="function", line=42)
        d = s.to_dict()
        assert d["name"] == "foo"
        assert d["line"] == 42


class TestRepoIndex:
    def test_filter_by_kind(self) -> None:
        idx = RepoIndex(symbols=[
            Symbol("foo", "function"),
            Symbol("Bar", "class"),
        ])
        assert len(idx.functions()) == 1
        assert len(idx.classes()) == 1


# ── RepoIndexer ──────────────────────────────────────────────────


class TestRepoIndexer:
    def test_index_file(self) -> None:
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write('"""Module doc."""\n\nimport os\nfrom pathlib import Path\n\n')
            f.write("def hello():\n    '''Say hi.'''\n    pass\n\n")
            f.write("class Greeter:\n    '''A greeter.'''\n    pass\n")
            f.flush()
            indexer = RepoIndexer()
            idx = indexer.index_file(f.name)
            os.unlink(f.name)

        assert idx.files_indexed == 1
        assert idx.symbol_count >= 2
        func_names = [s.name for s in idx.functions()]
        assert "hello" in func_names
        class_names = [s.name for s in idx.classes()]
        assert "Greeter" in class_names
        assert len(idx.imports) >= 2

    def test_missing_file(self) -> None:
        indexer = RepoIndexer()
        idx = indexer.index_file("/nonexistent.py")
        assert idx.symbol_count == 0

    def test_index_directory(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            Path(tmpdir, "a.py").write_text("def fa(): pass\n")
            Path(tmpdir, "b.py").write_text("class Cb: pass\n")
            indexer = RepoIndexer()
            idx = indexer.index_directory(tmpdir)
            assert idx.files_indexed == 2
            assert idx.symbol_count >= 2

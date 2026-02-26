"""Coverage tests for the static_analysis module (exports.py + imports.py).

Tests the export auditing, import scanning, layer violation detection,
dead export detection, unused function detection, and full audit
functionality using real Python source strings written to temporary
directories.  Zero mocks.
"""

from __future__ import annotations

import textwrap

import pytest

from codomyrmex.static_analysis.exports import (
    SKIP_DIRS,
    _collect_all_imports,
    _collect_defined_functions,
    _collect_name_references,
    audit_exports,
    check_all_defined,
    find_dead_exports,
    find_unused_functions,
    full_audit,
    get_modules,
)
from codomyrmex.static_analysis.imports import (
    CORE,
    FOUNDATION,
    SERVICE,
    SPECIALIZED,
    check_layer_violations,
    extract_imports_ast,
    get_layer,
    scan_imports,
)

pytestmark = pytest.mark.unit


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _make_module(base, name: str, init_source: str = "") -> None:
    """Create a fake module directory with __init__.py."""
    mod_dir = base / name
    mod_dir.mkdir(parents=True, exist_ok=True)
    (mod_dir / "__init__.py").write_text(init_source, encoding="utf-8")


def _write_py(base, relpath: str, source: str) -> None:
    """Write a .py file inside *base* at the given relative path."""
    target = base / relpath
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(textwrap.dedent(source), encoding="utf-8")


# ===================================================================
# exports.py  --  get_modules
# ===================================================================


class TestGetModules:
    """Tests for get_modules() module-directory discovery."""

    def test_empty_directory_returns_empty(self, tmp_path):
        """An empty directory has no modules."""
        assert get_modules(tmp_path) == []

    def test_nonexistent_directory_returns_empty(self, tmp_path):
        """A non-existent directory returns an empty list."""
        assert get_modules(tmp_path / "does_not_exist") == []

    def test_discovers_module_with_init(self, tmp_path):
        """A directory containing __init__.py is recognised as a module."""
        _make_module(tmp_path, "alpha")
        result = get_modules(tmp_path)
        assert len(result) == 1
        assert result[0].name == "alpha"

    def test_ignores_directory_without_init(self, tmp_path):
        """A directory without __init__.py is not a module."""
        (tmp_path / "nomod").mkdir()
        assert get_modules(tmp_path) == []

    def test_skips_pycache(self, tmp_path):
        """__pycache__ directories are skipped even if they have __init__.py."""
        _make_module(tmp_path, "__pycache__")
        assert get_modules(tmp_path) == []

    def test_skips_dot_directories(self, tmp_path):
        """Hidden directories (starting with '.') are skipped."""
        _make_module(tmp_path, ".hidden")
        assert get_modules(tmp_path) == []

    def test_skips_all_skip_dirs(self, tmp_path):
        """Every entry in SKIP_DIRS is ignored."""
        for name in SKIP_DIRS:
            _make_module(tmp_path, name)
        assert get_modules(tmp_path) == []

    def test_returns_sorted_list(self, tmp_path):
        """Modules are returned in sorted (alphabetical) order."""
        for name in ["zeta", "alpha", "mu"]:
            _make_module(tmp_path, name)
        names = [p.name for p in get_modules(tmp_path)]
        assert names == ["alpha", "mu", "zeta"]


# ===================================================================
# exports.py  --  check_all_defined
# ===================================================================


class TestCheckAllDefined:
    """Tests for check_all_defined() __all__ detection."""

    def test_list_all_detected(self, tmp_path):
        """__all__ defined as a list is detected with correct names."""
        init = tmp_path / "__init__.py"
        init.write_text('__all__ = ["foo", "bar"]\n', encoding="utf-8")
        has_all, names = check_all_defined(init)
        assert has_all is True
        assert names == ["foo", "bar"]

    def test_tuple_all_detected(self, tmp_path):
        """__all__ defined as a tuple is detected."""
        init = tmp_path / "__init__.py"
        init.write_text('__all__ = ("x", "y")\n', encoding="utf-8")
        has_all, names = check_all_defined(init)
        assert has_all is True
        assert names == ["x", "y"]

    def test_missing_all_returns_false(self, tmp_path):
        """File without __all__ returns (False, None)."""
        init = tmp_path / "__init__.py"
        init.write_text("def foo(): pass\n", encoding="utf-8")
        has_all, names = check_all_defined(init)
        assert has_all is False
        assert names is None

    def test_empty_all_list(self, tmp_path):
        """__all__ = [] returns (True, [])."""
        init = tmp_path / "__init__.py"
        init.write_text("__all__ = []\n", encoding="utf-8")
        has_all, names = check_all_defined(init)
        assert has_all is True
        assert names == []

    def test_all_with_non_string_elements(self, tmp_path):
        """Non-string elements in __all__ are filtered out."""
        init = tmp_path / "__init__.py"
        init.write_text('__all__ = ["good", 42, "also_good"]\n', encoding="utf-8")
        has_all, names = check_all_defined(init)
        assert has_all is True
        assert names == ["good", "also_good"]

    def test_all_assigned_to_non_list_returns_true_none(self, tmp_path):
        """__all__ assigned to a non-list/tuple value returns (True, None)."""
        init = tmp_path / "__init__.py"
        init.write_text('__all__ = get_exports()\n', encoding="utf-8")
        has_all, names = check_all_defined(init)
        assert has_all is True
        assert names is None

    def test_syntax_error_returns_false(self, tmp_path):
        """Unparseable file returns (False, None)."""
        init = tmp_path / "__init__.py"
        init.write_text("def broken(:\n", encoding="utf-8")
        has_all, names = check_all_defined(init)
        assert has_all is False
        assert names is None

    def test_annotated_all_list(self, tmp_path):
        """__all__: list[str] = [...] is detected via AnnAssign."""
        init = tmp_path / "__init__.py"
        init.write_text('__all__: list[str] = ["a", "b"]\n', encoding="utf-8")
        has_all, names = check_all_defined(init)
        assert has_all is True
        assert names == ["a", "b"]

    def test_annotated_all_without_value(self, tmp_path):
        """__all__: list[str] with no value returns (True, None)."""
        init = tmp_path / "__init__.py"
        # AnnAssign with no value -- Python allows bare annotations
        init.write_text("__all__: list[str]\n", encoding="utf-8")
        has_all, names = check_all_defined(init)
        # node.value is None, so we get True, None
        assert has_all is True
        assert names is None


# ===================================================================
# exports.py  --  audit_exports
# ===================================================================


class TestAuditExports:
    """Tests for audit_exports() MISSING_ALL detection."""

    def test_module_with_all_produces_no_finding(self, tmp_path):
        """A module whose __init__.py defines __all__ is clean."""
        _make_module(tmp_path, "good", '__all__ = ["x"]\n')
        findings = audit_exports(tmp_path)
        assert findings == []

    def test_module_without_all_produces_finding(self, tmp_path):
        """A module without __all__ creates a MISSING_ALL finding."""
        _make_module(tmp_path, "bad", "")
        findings = audit_exports(tmp_path)
        assert len(findings) == 1
        assert findings[0]["module"] == "bad"
        assert findings[0]["issue"] == "MISSING_ALL"

    def test_mixed_modules(self, tmp_path):
        """Only modules missing __all__ appear in findings."""
        _make_module(tmp_path, "has_all", '__all__ = ["a"]\n')
        _make_module(tmp_path, "missing", "x = 1\n")
        findings = audit_exports(tmp_path)
        modules_flagged = {f["module"] for f in findings}
        assert "missing" in modules_flagged
        assert "has_all" not in modules_flagged


# ===================================================================
# exports.py  --  _collect_all_imports
# ===================================================================


class TestCollectAllImports:
    """Tests for _collect_all_imports() cross-codebase name collection."""

    def test_collects_from_import(self, tmp_path):
        """from codomyrmex.X import Y collects Y."""
        _write_py(tmp_path, "mod/consumer.py", """\
            from codomyrmex.foo import bar
        """)
        names = _collect_all_imports(tmp_path)
        assert "bar" in names

    def test_collects_import_statement(self, tmp_path):
        """import codomyrmex.X.Y collects Y (last segment)."""
        _write_py(tmp_path, "mod/consumer.py", """\
            import codomyrmex.foo.bar
        """)
        names = _collect_all_imports(tmp_path)
        assert "bar" in names

    def test_ignores_non_codomyrmex_imports(self, tmp_path):
        """Imports not from codomyrmex are ignored."""
        _write_py(tmp_path, "mod/consumer.py", """\
            import os
            from pathlib import Path
        """)
        names = _collect_all_imports(tmp_path)
        assert len(names) == 0

    def test_skips_pycache_dirs(self, tmp_path):
        """Files inside __pycache__ are skipped."""
        _write_py(tmp_path, "__pycache__/cached.py", """\
            from codomyrmex.x import y
        """)
        names = _collect_all_imports(tmp_path)
        assert "y" not in names


# ===================================================================
# exports.py  --  find_dead_exports
# ===================================================================


class TestFindDeadExports:
    """Tests for find_dead_exports() unused-export detection."""

    def test_no_dead_when_export_is_imported(self, tmp_path):
        """An export that is imported elsewhere is not dead."""
        _make_module(tmp_path, "provider", '__all__ = ["helper"]\ndef helper(): pass\n')
        _write_py(tmp_path, "consumer/use.py", """\
            from codomyrmex.provider import helper
        """)
        dead = find_dead_exports(tmp_path)
        assert all(d["export_name"] != "helper" for d in dead)

    def test_dead_export_detected(self, tmp_path):
        """An export never imported is flagged as dead."""
        _make_module(tmp_path, "lonely", '__all__ = ["orphan"]\ndef orphan(): pass\n')
        dead = find_dead_exports(tmp_path)
        orphans = [d for d in dead if d["export_name"] == "orphan"]
        assert len(orphans) == 1
        assert orphans[0]["module"] == "lonely"


# ===================================================================
# exports.py  --  _collect_defined_functions / _collect_name_references
# ===================================================================


class TestCollectDefinedFunctions:
    """Tests for _collect_defined_functions() top-level function extraction."""

    def test_extracts_public_functions(self, tmp_path):
        """Public top-level functions are extracted."""
        py = tmp_path / "sample.py"
        py.write_text("def alpha(): pass\ndef beta(): pass\n", encoding="utf-8")
        funcs = _collect_defined_functions(py)
        assert "alpha" in funcs
        assert "beta" in funcs

    def test_excludes_private_functions(self, tmp_path):
        """Functions starting with _ are excluded."""
        py = tmp_path / "sample.py"
        py.write_text("def _private(): pass\ndef public(): pass\n", encoding="utf-8")
        funcs = _collect_defined_functions(py)
        assert "_private" not in funcs
        assert "public" in funcs

    def test_excludes_class_methods(self, tmp_path):
        """Methods inside classes are not top-level and are excluded."""
        py = tmp_path / "sample.py"
        py.write_text("class Foo:\n    def method(self): pass\n", encoding="utf-8")
        funcs = _collect_defined_functions(py)
        assert "method" not in funcs

    def test_handles_async_functions(self, tmp_path):
        """Async top-level functions are extracted."""
        py = tmp_path / "sample.py"
        py.write_text("async def fetch(): pass\n", encoding="utf-8")
        funcs = _collect_defined_functions(py)
        assert "fetch" in funcs

    def test_syntax_error_returns_empty(self, tmp_path):
        """A file with syntax errors returns an empty list."""
        py = tmp_path / "broken.py"
        py.write_text("def oops(:\n", encoding="utf-8")
        funcs = _collect_defined_functions(py)
        assert funcs == []


class TestCollectNameReferences:
    """Tests for _collect_name_references() identifier collection."""

    def test_collects_variable_names(self, tmp_path):
        """Variable references are collected."""
        py = tmp_path / "ref.py"
        py.write_text("x = 1\nprint(x)\n", encoding="utf-8")
        refs = _collect_name_references(py)
        assert "x" in refs
        assert "print" in refs

    def test_syntax_error_returns_empty(self, tmp_path):
        """A file with syntax errors returns an empty set."""
        py = tmp_path / "bad.py"
        py.write_text("def bad(:\n", encoding="utf-8")
        refs = _collect_name_references(py)
        assert refs == set()


# ===================================================================
# exports.py  --  find_unused_functions
# ===================================================================


class TestFindUnusedFunctions:
    """Tests for find_unused_functions() unreferenced-function detection."""

    def test_used_function_not_flagged(self, tmp_path):
        """A function referenced elsewhere is not unused."""
        _write_py(tmp_path, "lib.py", """\
            def compute(): pass
        """)
        _write_py(tmp_path, "main.py", """\
            from lib import compute
            compute()
        """)
        unused = find_unused_functions(tmp_path)
        assert all(u["function_name"] != "compute" for u in unused)

    def test_unused_function_flagged(self, tmp_path):
        """A function never referenced anywhere is flagged."""
        _write_py(tmp_path, "lib.py", """\
            def never_called(): pass
        """)
        _write_py(tmp_path, "main.py", """\
            x = 1
        """)
        unused = find_unused_functions(tmp_path)
        flagged_names = {u["function_name"] for u in unused}
        assert "never_called" in flagged_names


# ===================================================================
# exports.py  --  full_audit
# ===================================================================


class TestFullAudit:
    """Tests for full_audit() unified report."""

    def test_returns_expected_keys(self, tmp_path):
        """The report dict has all expected top-level keys."""
        report = full_audit(tmp_path)
        assert "missing_all" in report
        assert "dead_exports" in report
        assert "unused_functions" in report
        assert "summary" in report

    def test_summary_counts_match(self, tmp_path):
        """Summary counts match the length of finding lists."""
        _make_module(tmp_path, "a", "")
        report = full_audit(tmp_path)
        assert report["summary"]["modules_missing_all"] == len(report["missing_all"])
        assert report["summary"]["dead_export_count"] == len(report["dead_exports"])
        assert report["summary"]["unused_function_count"] == len(report["unused_functions"])

    def test_clean_codebase_summary_zeros(self, tmp_path):
        """A codebase with properly defined __all__ and no dead code has zero counts."""
        _make_module(tmp_path, "clean", '__all__ = []\n')
        report = full_audit(tmp_path)
        assert report["summary"]["modules_missing_all"] == 0
        assert report["summary"]["dead_export_count"] == 0


# ===================================================================
# imports.py  --  get_layer
# ===================================================================


class TestGetLayer:
    """Tests for get_layer() architectural layer mapping."""

    def test_foundation_modules(self):
        """All FOUNDATION members map to 'foundation'."""
        for mod in FOUNDATION:
            assert get_layer(mod) == "foundation", f"{mod} should be foundation"

    def test_core_modules(self):
        """All CORE members map to 'core'."""
        for mod in CORE:
            assert get_layer(mod) == "core", f"{mod} should be core"

    def test_service_modules(self):
        """All SERVICE members map to 'service'."""
        for mod in SERVICE:
            assert get_layer(mod) == "service", f"{mod} should be service"

    def test_specialized_modules(self):
        """All SPECIALIZED members map to 'specialized'."""
        for mod in SPECIALIZED:
            assert get_layer(mod) == "specialized", f"{mod} should be specialized"

    def test_unknown_module_returns_other(self):
        """An unrecognised module name maps to 'other'."""
        assert get_layer("totally_unknown_module") == "other"


# ===================================================================
# imports.py  --  extract_imports_ast
# ===================================================================


class TestExtractImportsAst:
    """Tests for extract_imports_ast() codomyrmex import extraction."""

    def test_from_import_extracts_module(self, tmp_path):
        """'from codomyrmex.foo import bar' extracts 'foo'."""
        py = tmp_path / "a.py"
        py.write_text("from codomyrmex.logging_monitoring import logger\n", encoding="utf-8")
        mods = extract_imports_ast(py)
        assert "logging_monitoring" in mods

    def test_import_statement_extracts_module(self, tmp_path):
        """'import codomyrmex.foo.bar' extracts 'foo'."""
        py = tmp_path / "b.py"
        py.write_text("import codomyrmex.security.secrets\n", encoding="utf-8")
        mods = extract_imports_ast(py)
        assert "security" in mods

    def test_non_codomyrmex_imports_ignored(self, tmp_path):
        """Imports not from codomyrmex produce no results."""
        py = tmp_path / "c.py"
        py.write_text("import os\nfrom pathlib import Path\n", encoding="utf-8")
        mods = extract_imports_ast(py)
        assert mods == []

    def test_syntax_error_returns_empty(self, tmp_path):
        """A file with syntax errors returns an empty list."""
        py = tmp_path / "broken.py"
        py.write_text("def f(:\n", encoding="utf-8")
        mods = extract_imports_ast(py)
        assert mods == []

    def test_multiple_imports(self, tmp_path):
        """Multiple codomyrmex imports are all extracted."""
        py = tmp_path / "multi.py"
        py.write_text(textwrap.dedent("""\
            from codomyrmex.agents import core
            from codomyrmex.cli import main
            import codomyrmex.llm.provider
        """), encoding="utf-8")
        mods = extract_imports_ast(py)
        assert "agents" in mods
        assert "cli" in mods
        assert "llm" in mods

    def test_from_import_without_submodule_ignored(self, tmp_path):
        """'from codomyrmex import X' (no submodule) has only 1 part after split, ignored."""
        py = tmp_path / "top.py"
        py.write_text("from codomyrmex import something\n", encoding="utf-8")
        mods = extract_imports_ast(py)
        # "codomyrmex" splits to ["codomyrmex"] -- only 1 part, no second element
        assert mods == []


# ===================================================================
# imports.py  --  scan_imports
# ===================================================================


class TestScanImports:
    """Tests for scan_imports() cross-module import scanning."""

    def test_detects_cross_module_import(self, tmp_path):
        """An import from module A to module B creates an edge."""
        _write_py(tmp_path, "modA/core.py", """\
            from codomyrmex.modB import helper
        """)
        _write_py(tmp_path, "modB/__init__.py", "")
        edges = scan_imports(tmp_path)
        cross = [e for e in edges if e["src"] == "modA" and e["dst"] == "modB"]
        assert len(cross) == 1

    def test_self_import_excluded(self, tmp_path):
        """A module importing from itself is not recorded."""
        _write_py(tmp_path, "self_mod/core.py", """\
            from codomyrmex.self_mod import util
        """)
        edges = scan_imports(tmp_path)
        self_edges = [e for e in edges if e["src"] == "self_mod" and e["dst"] == "self_mod"]
        assert len(self_edges) == 0

    def test_edge_contains_layer_info(self, tmp_path):
        """Each edge includes src_layer and dst_layer."""
        _write_py(tmp_path, "modX/x.py", """\
            from codomyrmex.modY import z
        """)
        edges = scan_imports(tmp_path)
        for edge in edges:
            assert "src_layer" in edge
            assert "dst_layer" in edge

    def test_empty_directory(self, tmp_path):
        """Empty directory produces no edges."""
        edges = scan_imports(tmp_path)
        assert edges == []


# ===================================================================
# imports.py  --  check_layer_violations
# ===================================================================


class TestCheckLayerViolations:
    """Tests for check_layer_violations() architectural boundary enforcement."""

    def test_foundation_importing_core_is_violation(self):
        """A foundation module importing a core module is a violation."""
        edges = [{
            "src": "logging_monitoring",
            "dst": "coding",
            "file": "logging_monitoring/bad.py",
            "src_layer": "foundation",
            "dst_layer": "core",
        }]
        violations = check_layer_violations(edges)
        assert len(violations) == 1
        assert "reason" in violations[0]

    def test_core_importing_foundation_is_allowed(self):
        """A core module importing a foundation module is NOT a violation."""
        edges = [{
            "src": "coding",
            "dst": "logging_monitoring",
            "file": "coding/analyzer.py",
            "src_layer": "core",
            "dst_layer": "foundation",
        }]
        violations = check_layer_violations(edges)
        assert violations == []

    def test_same_layer_import_is_allowed(self):
        """Imports within the same layer are allowed."""
        edges = [{
            "src": "coding",
            "dst": "security",
            "file": "coding/scan.py",
            "src_layer": "core",
            "dst_layer": "core",
        }]
        violations = check_layer_violations(edges)
        assert violations == []

    def test_foundation_importing_specialized_is_violation(self):
        """A foundation module importing a specialized module is a violation."""
        edges = [{
            "src": "config_management",
            "dst": "agents",
            "file": "config_management/bad.py",
            "src_layer": "foundation",
            "dst_layer": "specialized",
        }]
        violations = check_layer_violations(edges)
        assert len(violations) == 1

    def test_other_layer_no_violation(self):
        """Edges with 'other' layer are never flagged (rank is None)."""
        edges = [{
            "src": "unknown",
            "dst": "coding",
            "file": "unknown/x.py",
            "src_layer": "other",
            "dst_layer": "core",
        }]
        violations = check_layer_violations(edges)
        assert violations == []

    def test_multiple_edges_mixed(self):
        """A mix of valid and invalid edges only flags the invalid ones."""
        edges = [
            {
                "src": "coding",
                "dst": "logging_monitoring",
                "file": "coding/ok.py",
                "src_layer": "core",
                "dst_layer": "foundation",
            },
            {
                "src": "logging_monitoring",
                "dst": "agents",
                "file": "logging_monitoring/bad.py",
                "src_layer": "foundation",
                "dst_layer": "specialized",
            },
        ]
        violations = check_layer_violations(edges)
        assert len(violations) == 1
        assert violations[0]["src"] == "logging_monitoring"

    def test_empty_edges_returns_empty(self):
        """An empty edge list produces no violations."""
        assert check_layer_violations([]) == []


# ===================================================================
# imports.py  --  layer set completeness
# ===================================================================


class TestLayerSets:
    """Tests verifying layer set properties."""

    def test_no_overlap_between_layers(self):
        """No module appears in more than one layer."""
        all_sets = [FOUNDATION, CORE, SERVICE, SPECIALIZED]
        for i, a in enumerate(all_sets):
            for b in all_sets[i + 1:]:
                overlap = a & b
                assert overlap == set(), f"Overlap found: {overlap}"

    def test_foundation_is_nonempty(self):
        """FOUNDATION contains at least one module."""
        assert len(FOUNDATION) > 0

    def test_core_is_nonempty(self):
        """CORE contains at least one module."""
        assert len(CORE) > 0

    def test_service_is_nonempty(self):
        """SERVICE contains at least one module."""
        assert len(SERVICE) > 0

    def test_specialized_is_nonempty(self):
        """SPECIALIZED contains at least one module."""
        assert len(SPECIALIZED) > 0

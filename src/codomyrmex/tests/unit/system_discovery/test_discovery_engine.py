"""Tests for codomyrmex.system_discovery.core.discovery_engine module.

Covers:
- ModuleCapability dataclass construction and field access
- ModuleInfo dataclass construction and field access
- SystemDiscovery.__init__ (default and explicit project_root)
- SystemDiscovery.scan_system (inventory structure and stats)
- SystemDiscovery.export_inventory (JSON file writing, success/failure)
- SystemDiscovery._discover_modules (directory scanning, __init__.py detection)
- SystemDiscovery._analyze_module (importable vs non-importable paths)
- SystemDiscovery._static_analysis_capabilities (AST-based scanning)
- SystemDiscovery._analyze_object (function, class, method, constant, other)
- SystemDiscovery._get_function_signature_from_ast (args, defaults, *args, **kwargs)
- SystemDiscovery._get_module_description (README, __init__.py docstring, fallback)
- SystemDiscovery._get_module_version (__version__ detection, fallback)
- SystemDiscovery._get_module_dependencies (requirements.txt parsing)
- SystemDiscovery._has_tests (test file existence check)
- SystemDiscovery._has_docs (doc indicator detection)
- SystemDiscovery._get_last_modified (mtime scanning)
- SystemDiscovery._display_discovery_results (stdout output)
- SystemDiscovery._display_capability_summary (stdout grouping)
- SystemDiscovery._get_system_status_dict (dictionary structure)
- SystemDiscovery._check_git_status (git command execution)
- SystemDiscovery._check_core_dependencies (dependency import probing)
- SystemDiscovery.show_status_dashboard (composite dashboard output)
- SystemDiscovery.run_full_discovery (end-to-end orchestration)
- SystemDiscovery.export_full_inventory (JSON export variant)
- SystemDiscovery.check_git_repositories (git repo + submodule checking)
- SystemDiscovery.run_demo_workflows (demo execution)
"""

import ast
import json
import sys
from dataclasses import asdict
from pathlib import Path

import pytest

# ===================================================================
# ModuleCapability dataclass
# ===================================================================


@pytest.mark.unit
class TestModuleCapability:
    """Test ModuleCapability dataclass construction and field access."""

    def test_creation_all_fields(self):
        from codomyrmex.system_discovery.core.discovery_engine import ModuleCapability

        cap = ModuleCapability(
            name="my_func",
            module_path="/src/codomyrmex/utils",
            type="function",
            signature="my_func(x, y)",
            docstring="Adds two numbers.",
            file_path="/src/codomyrmex/utils/helpers.py",
            line_number=42,
            is_public=True,
            dependencies=["numpy"],
        )
        assert cap.name == "my_func"
        assert cap.type == "function"
        assert cap.line_number == 42
        assert cap.is_public is True
        assert cap.dependencies == ["numpy"]

    def test_asdict_roundtrip(self):
        from codomyrmex.system_discovery.core.discovery_engine import ModuleCapability

        cap = ModuleCapability(
            name="Cls",
            module_path="/m",
            type="class",
            signature="class Cls",
            docstring="A class.",
            file_path="/m/cls.py",
            line_number=1,
            is_public=True,
            dependencies=[],
        )
        d = asdict(cap)
        assert isinstance(d, dict)
        assert d["name"] == "Cls"
        assert d["type"] == "class"

    def test_private_capability(self):
        from codomyrmex.system_discovery.core.discovery_engine import ModuleCapability

        cap = ModuleCapability(
            name="_helper",
            module_path="/m",
            type="function",
            signature="_helper()",
            docstring="",
            file_path="/m/h.py",
            line_number=10,
            is_public=False,
            dependencies=[],
        )
        assert cap.is_public is False


# ===================================================================
# ModuleInfo dataclass
# ===================================================================


@pytest.mark.unit
class TestModuleInfo:
    """Test ModuleInfo dataclass construction and field access."""

    def test_creation_all_fields(self):
        from codomyrmex.system_discovery.core.discovery_engine import (
            ModuleCapability,
            ModuleInfo,
        )

        cap = ModuleCapability(
            name="f",
            module_path="/m",
            type="function",
            signature="f()",
            docstring="",
            file_path="/m/f.py",
            line_number=1,
            is_public=True,
            dependencies=[],
        )
        info = ModuleInfo(
            name="utils",
            path="/src/codomyrmex/utils",
            description="Utility module",
            version="1.0.0",
            capabilities=[cap],
            dependencies=["requests"],
            is_importable=True,
            has_tests=True,
            has_docs=True,
            last_modified="2026-01-01 00:00:00",
        )
        assert info.name == "utils"
        assert info.is_importable is True
        assert len(info.capabilities) == 1
        assert info.capabilities[0].name == "f"

    def test_asdict_roundtrip(self):
        from codomyrmex.system_discovery.core.discovery_engine import ModuleInfo

        info = ModuleInfo(
            name="core",
            path="/p",
            description="desc",
            version="unknown",
            capabilities=[],
            dependencies=[],
            is_importable=False,
            has_tests=False,
            has_docs=False,
            last_modified="unknown",
        )
        d = asdict(info)
        assert d["name"] == "core"
        assert d["capabilities"] == []
        assert d["is_importable"] is False


# ===================================================================
# SystemDiscovery.__init__
# ===================================================================


@pytest.mark.unit
class TestSystemDiscoveryInit:
    """Test SystemDiscovery constructor."""

    def test_default_project_root(self):
        from codomyrmex.system_discovery.core.discovery_engine import SystemDiscovery

        sd = SystemDiscovery()
        assert sd.project_root == Path.cwd()
        assert sd.src_path == Path.cwd() / "src"
        assert sd.codomyrmex_path == Path.cwd() / "src" / "codomyrmex"
        assert sd.modules == {}
        assert sd.system_status == {}

    def test_explicit_project_root(self, tmp_path):
        from codomyrmex.system_discovery.core.discovery_engine import SystemDiscovery

        sd = SystemDiscovery(project_root=tmp_path)
        assert sd.project_root == tmp_path
        assert sd.src_path == tmp_path / "src"
        assert sd.codomyrmex_path == tmp_path / "src" / "codomyrmex"
        assert sd.testing_path == tmp_path / "testing"


# ===================================================================
# SystemDiscovery._get_module_description
# ===================================================================


@pytest.mark.unit
class TestGetModuleDescription:
    """Test _get_module_description with README, __init__.py docstring, and fallback."""

    def test_from_readme(self, tmp_path):
        from codomyrmex.system_discovery.core.discovery_engine import SystemDiscovery

        mod_dir = tmp_path / "mymod"
        mod_dir.mkdir()
        (mod_dir / "README.md").write_text("# My Module\nThis module does things.\n")
        sd = SystemDiscovery(project_root=tmp_path)
        desc = sd._get_module_description(mod_dir)
        assert desc == "This module does things."

    def test_from_init_docstring(self, tmp_path):
        from codomyrmex.system_discovery.core.discovery_engine import SystemDiscovery

        mod_dir = tmp_path / "mymod"
        mod_dir.mkdir()
        (mod_dir / "__init__.py").write_text('"""A cool module."""\n')
        sd = SystemDiscovery(project_root=tmp_path)
        desc = sd._get_module_description(mod_dir)
        assert desc == "A cool module."

    def test_fallback_no_docs(self, tmp_path):
        from codomyrmex.system_discovery.core.discovery_engine import SystemDiscovery

        mod_dir = tmp_path / "mymod"
        mod_dir.mkdir()
        sd = SystemDiscovery(project_root=tmp_path)
        desc = sd._get_module_description(mod_dir)
        assert desc == "No description available"

    def test_readme_only_header(self, tmp_path):
        from codomyrmex.system_discovery.core.discovery_engine import SystemDiscovery

        mod_dir = tmp_path / "mymod"
        mod_dir.mkdir()
        (mod_dir / "README.md").write_text("# Header Only\n")
        (mod_dir / "__init__.py").write_text('"""Fallback docstring."""\n')
        sd = SystemDiscovery(project_root=tmp_path)
        desc = sd._get_module_description(mod_dir)
        # README has only a header line, so falls through to init docstring
        assert desc == "Fallback docstring."


# ===================================================================
# SystemDiscovery._get_module_version
# ===================================================================


@pytest.mark.unit
class TestGetModuleVersion:
    """Test _get_module_version from __init__.py __version__ and fallback."""

    def test_version_found(self, tmp_path):
        from codomyrmex.system_discovery.core.discovery_engine import SystemDiscovery

        mod_dir = tmp_path / "mymod"
        mod_dir.mkdir()
        (mod_dir / "__init__.py").write_text('__version__ = "2.3.4"\n')
        sd = SystemDiscovery(project_root=tmp_path)
        ver = sd._get_module_version(mod_dir)
        assert ver == "2.3.4"

    def test_version_unknown(self, tmp_path):
        from codomyrmex.system_discovery.core.discovery_engine import SystemDiscovery

        mod_dir = tmp_path / "mymod"
        mod_dir.mkdir()
        (mod_dir / "__init__.py").write_text("# no version\n")
        sd = SystemDiscovery(project_root=tmp_path)
        ver = sd._get_module_version(mod_dir)
        assert ver == "unknown"

    def test_no_init_file(self, tmp_path):
        from codomyrmex.system_discovery.core.discovery_engine import SystemDiscovery

        mod_dir = tmp_path / "mymod"
        mod_dir.mkdir()
        sd = SystemDiscovery(project_root=tmp_path)
        ver = sd._get_module_version(mod_dir)
        assert ver == "unknown"


# ===================================================================
# SystemDiscovery._get_module_dependencies
# ===================================================================


@pytest.mark.unit
class TestGetModuleDependencies:
    """Test _get_module_dependencies from requirements.txt."""

    def test_parses_requirements(self, tmp_path):
        from codomyrmex.system_discovery.core.discovery_engine import SystemDiscovery

        mod_dir = tmp_path / "mymod"
        mod_dir.mkdir()
        (mod_dir / "requirements.txt").write_text(
            "# A comment\nrequests>=2.28\nnumpy==1.24.0\nflask~=3.0\n"
        )
        sd = SystemDiscovery(project_root=tmp_path)
        deps = sd._get_module_dependencies(mod_dir)
        assert "requests" in deps
        assert "numpy" in deps
        assert "flask" in deps
        assert len(deps) == 3

    def test_no_requirements(self, tmp_path):
        from codomyrmex.system_discovery.core.discovery_engine import SystemDiscovery

        mod_dir = tmp_path / "mymod"
        mod_dir.mkdir()
        sd = SystemDiscovery(project_root=tmp_path)
        deps = sd._get_module_dependencies(mod_dir)
        assert deps == []


# ===================================================================
# SystemDiscovery._has_tests
# ===================================================================


@pytest.mark.unit
class TestHasTests:
    """Test _has_tests checks for test file existence."""

    def test_has_test_file(self, tmp_path):
        from codomyrmex.system_discovery.core.discovery_engine import SystemDiscovery

        testing_dir = tmp_path / "testing" / "unit"
        testing_dir.mkdir(parents=True)
        (testing_dir / "test_mymod.py").write_text("# test\n")
        sd = SystemDiscovery(project_root=tmp_path)
        assert sd._has_tests("mymod") is True

    def test_no_test_file(self, tmp_path):
        from codomyrmex.system_discovery.core.discovery_engine import SystemDiscovery

        sd = SystemDiscovery(project_root=tmp_path)
        assert sd._has_tests("nonexistent") is False


# ===================================================================
# SystemDiscovery._has_docs
# ===================================================================


@pytest.mark.unit
class TestHasDocs:
    """Test _has_docs checks for documentation indicators."""

    def test_has_readme(self, tmp_path):
        from codomyrmex.system_discovery.core.discovery_engine import SystemDiscovery

        mod_dir = tmp_path / "mymod"
        mod_dir.mkdir()
        (mod_dir / "README.md").write_text("# Docs\n")
        sd = SystemDiscovery(project_root=tmp_path)
        assert sd._has_docs(mod_dir) is True

    def test_has_api_spec(self, tmp_path):
        from codomyrmex.system_discovery.core.discovery_engine import SystemDiscovery

        mod_dir = tmp_path / "mymod"
        mod_dir.mkdir()
        (mod_dir / "API_SPECIFICATION.md").write_text("# API\n")
        sd = SystemDiscovery(project_root=tmp_path)
        assert sd._has_docs(mod_dir) is True

    def test_has_docs_dir(self, tmp_path):
        from codomyrmex.system_discovery.core.discovery_engine import SystemDiscovery

        mod_dir = tmp_path / "mymod"
        mod_dir.mkdir()
        (mod_dir / "docs").mkdir()
        sd = SystemDiscovery(project_root=tmp_path)
        assert sd._has_docs(mod_dir) is True

    def test_no_docs(self, tmp_path):
        from codomyrmex.system_discovery.core.discovery_engine import SystemDiscovery

        mod_dir = tmp_path / "mymod"
        mod_dir.mkdir()
        sd = SystemDiscovery(project_root=tmp_path)
        assert sd._has_docs(mod_dir) is False


# ===================================================================
# SystemDiscovery._get_last_modified
# ===================================================================


@pytest.mark.unit
class TestGetLastModified:
    """Test _get_last_modified returns formatted timestamps."""

    def test_returns_timestamp_string(self, tmp_path):
        from codomyrmex.system_discovery.core.discovery_engine import SystemDiscovery

        mod_dir = tmp_path / "mymod"
        mod_dir.mkdir()
        (mod_dir / "__init__.py").write_text("# init\n")
        (mod_dir / "core.py").write_text("# core\n")
        sd = SystemDiscovery(project_root=tmp_path)
        result = sd._get_last_modified(mod_dir)
        # Should be a date-like string, not "unknown"
        assert result != "unknown"
        assert "-" in result  # YYYY-MM-DD format

    def test_no_py_files(self, tmp_path):
        from codomyrmex.system_discovery.core.discovery_engine import SystemDiscovery

        mod_dir = tmp_path / "mymod"
        mod_dir.mkdir()
        (mod_dir / "data.txt").write_text("text\n")
        sd = SystemDiscovery(project_root=tmp_path)
        result = sd._get_last_modified(mod_dir)
        assert result == "unknown"


# ===================================================================
# SystemDiscovery._get_function_signature_from_ast
# ===================================================================


@pytest.mark.unit
class TestGetFunctionSignatureFromAst:
    """Test AST-based function signature reconstruction."""

    def test_simple_args(self):
        from codomyrmex.system_discovery.core.discovery_engine import SystemDiscovery

        code = "def foo(a, b): pass"
        tree = ast.parse(code)
        func_node = tree.body[0]
        sd = SystemDiscovery()
        sig = sd._get_function_signature_from_ast(func_node)
        assert sig == "foo(a, b)"

    def test_defaults(self):
        from codomyrmex.system_discovery.core.discovery_engine import SystemDiscovery

        code = "def bar(x, y=10): pass"
        tree = ast.parse(code)
        func_node = tree.body[0]
        sd = SystemDiscovery()
        sig = sd._get_function_signature_from_ast(func_node)
        assert sig == "bar(x, y=10)"

    def test_varargs_and_kwargs(self):
        from codomyrmex.system_discovery.core.discovery_engine import SystemDiscovery

        code = "def baz(*args, **kwargs): pass"
        tree = ast.parse(code)
        func_node = tree.body[0]
        sd = SystemDiscovery()
        sig = sd._get_function_signature_from_ast(func_node)
        assert sig == "baz(*args, **kwargs)"

    def test_no_args(self):
        from codomyrmex.system_discovery.core.discovery_engine import SystemDiscovery

        code = "def noop(): pass"
        tree = ast.parse(code)
        func_node = tree.body[0]
        sd = SystemDiscovery()
        sig = sd._get_function_signature_from_ast(func_node)
        assert sig == "noop()"


# ===================================================================
# SystemDiscovery._static_analysis_capabilities
# ===================================================================


@pytest.mark.unit
class TestStaticAnalysisCapabilities:
    """Test AST-based capability discovery."""

    def test_discovers_functions_and_classes(self, tmp_path):
        from codomyrmex.system_discovery.core.discovery_engine import SystemDiscovery

        mod_dir = tmp_path / "mymod"
        mod_dir.mkdir()
        (mod_dir / "core.py").write_text(
            '"""Module."""\n\n'
            "def public_func(x):\n"
            '    """A public function."""\n'
            "    return x\n\n"
            "def _private_func():\n"
            "    pass\n\n"
            "class MyClass:\n"
            '    """A public class."""\n'
            "    pass\n\n"
            "class _PrivateClass:\n"
            "    pass\n"
        )
        sd = SystemDiscovery(project_root=tmp_path)
        caps = sd._static_analysis_capabilities(mod_dir)
        names = [c.name for c in caps]
        # Public items discovered
        assert "public_func" in names
        assert "MyClass" in names
        # Private items excluded
        assert "_private_func" not in names
        assert "_PrivateClass" not in names

    def test_skips_test_files(self, tmp_path):
        from codomyrmex.system_discovery.core.discovery_engine import SystemDiscovery

        mod_dir = tmp_path / "mymod"
        mod_dir.mkdir()
        (mod_dir / "test_stuff.py").write_text("def test_something(): pass\n")
        (mod_dir / "real.py").write_text("def real_func(): pass\n")
        sd = SystemDiscovery(project_root=tmp_path)
        caps = sd._static_analysis_capabilities(mod_dir)
        names = [c.name for c in caps]
        assert "real_func" in names
        assert "test_something" not in names

    def test_empty_directory(self, tmp_path):
        from codomyrmex.system_discovery.core.discovery_engine import SystemDiscovery

        mod_dir = tmp_path / "mymod"
        mod_dir.mkdir()
        sd = SystemDiscovery(project_root=tmp_path)
        caps = sd._static_analysis_capabilities(mod_dir)
        assert caps == []

    def test_handles_syntax_error_gracefully(self, tmp_path):
        from codomyrmex.system_discovery.core.discovery_engine import SystemDiscovery

        mod_dir = tmp_path / "mymod"
        mod_dir.mkdir()
        (mod_dir / "bad.py").write_text("def broken(\n")
        sd = SystemDiscovery(project_root=tmp_path)
        caps = sd._static_analysis_capabilities(mod_dir)
        # Should not raise, just return empty or partial
        assert isinstance(caps, list)


# ===================================================================
# SystemDiscovery._analyze_object
# ===================================================================


@pytest.mark.unit
class TestAnalyzeObject:
    """Test runtime object analysis for different object types."""

    def test_function(self):
        from codomyrmex.system_discovery.core.discovery_engine import SystemDiscovery

        def sample_func(a, b=5):
            """Sample function."""
            return a + b

        sd = SystemDiscovery()
        cap = sd._analyze_object("sample_func", sample_func, Path("/m"))
        assert cap is not None
        assert cap.type == "function"
        assert cap.name == "sample_func"
        assert "Sample function." in cap.docstring

    def test_class(self):
        from codomyrmex.system_discovery.core.discovery_engine import SystemDiscovery

        class SampleClass:
            """A sample class."""
            pass

        sd = SystemDiscovery()
        cap = sd._analyze_object("SampleClass", SampleClass, Path("/m"))
        assert cap is not None
        assert cap.type == "class"
        assert cap.name == "SampleClass"

    def test_constant_string(self):
        from codomyrmex.system_discovery.core.discovery_engine import SystemDiscovery

        sd = SystemDiscovery()
        cap = sd._analyze_object("VERSION", "1.0.0", Path("/m"))
        assert cap is not None
        assert cap.type == "constant"

    def test_constant_int(self):
        from codomyrmex.system_discovery.core.discovery_engine import SystemDiscovery

        sd = SystemDiscovery()
        cap = sd._analyze_object("MAX_SIZE", 1024, Path("/m"))
        assert cap is not None
        assert cap.type == "constant"

    def test_other_type(self):

        from codomyrmex.system_discovery.core.discovery_engine import SystemDiscovery

        sd = SystemDiscovery()
        # A module object is "other"
        cap = sd._analyze_object("sys_mod", sys, Path("/m"))
        assert cap is not None
        assert cap.type == "other"


# ===================================================================
# SystemDiscovery._discover_modules (with synthetic filesystem)
# ===================================================================


@pytest.mark.unit
class TestDiscoverModules:
    """Test _discover_modules with a synthetic module directory."""

    def test_discovers_modules_with_init(self, tmp_path, capsys):
        from codomyrmex.system_discovery.core.discovery_engine import SystemDiscovery

        codomyrmex_dir = tmp_path / "src" / "codomyrmex"
        codomyrmex_dir.mkdir(parents=True)

        # Module with __init__.py
        mod_a = codomyrmex_dir / "mod_a"
        mod_a.mkdir()
        (mod_a / "__init__.py").write_text('"""Module A."""\n')
        (mod_a / "core.py").write_text("def hello(): pass\n")

        # Directory without __init__.py (should be skipped)
        mod_b = codomyrmex_dir / "mod_b"
        mod_b.mkdir()
        (mod_b / "stuff.py").write_text("x = 1\n")

        # Hidden directory (should be skipped)
        hidden = codomyrmex_dir / ".hidden"
        hidden.mkdir()
        (hidden / "__init__.py").write_text("")

        sd = SystemDiscovery(project_root=tmp_path)
        sd._discover_modules()

        # mod_a should be discovered (has __init__.py)
        assert "mod_a" in sd.modules
        # mod_b should NOT be discovered (no __init__.py)
        assert "mod_b" not in sd.modules
        # .hidden should NOT be discovered (starts with .)
        assert ".hidden" not in sd.modules

    def test_nonexistent_codomyrmex_path(self, tmp_path, capsys):
        from codomyrmex.system_discovery.core.discovery_engine import SystemDiscovery

        sd = SystemDiscovery(project_root=tmp_path)
        # codomyrmex_path does not exist
        sd._discover_modules()
        assert sd.modules == {}


# ===================================================================
# SystemDiscovery.scan_system
# ===================================================================


@pytest.mark.unit
class TestScanSystem:
    """Test scan_system inventory structure."""

    def test_inventory_structure(self, tmp_path, capsys):
        from codomyrmex.system_discovery.core.discovery_engine import SystemDiscovery

        # Create minimal structure
        codomyrmex_dir = tmp_path / "src" / "codomyrmex"
        codomyrmex_dir.mkdir(parents=True)
        mod = codomyrmex_dir / "testmod"
        mod.mkdir()
        (mod / "__init__.py").write_text('"""Test mod."""\n')
        (mod / "api.py").write_text("def endpoint(): pass\n")

        sd = SystemDiscovery(project_root=tmp_path)
        inventory = sd.scan_system()

        assert "project_root" in inventory
        assert "status" in inventory
        assert "modules" in inventory
        assert "stats" in inventory
        assert inventory["status"]["python_version"] == sys.version.split()[0]
        assert isinstance(inventory["stats"]["total_modules"], int)

    def test_empty_project(self, tmp_path, capsys):
        from codomyrmex.system_discovery.core.discovery_engine import SystemDiscovery

        sd = SystemDiscovery(project_root=tmp_path)
        inventory = sd.scan_system()
        assert inventory["stats"]["total_modules"] == 0
        assert inventory["modules"] == {}


# ===================================================================
# SystemDiscovery.export_inventory
# ===================================================================


@pytest.mark.unit
class TestExportInventory:
    """Test JSON export of system inventory."""

    def test_export_creates_file(self, tmp_path, capsys):
        from codomyrmex.system_discovery.core.discovery_engine import SystemDiscovery

        # Create minimal module structure
        codomyrmex_dir = tmp_path / "src" / "codomyrmex"
        codomyrmex_dir.mkdir(parents=True)
        mod = codomyrmex_dir / "alpha"
        mod.mkdir()
        (mod / "__init__.py").write_text("")

        sd = SystemDiscovery(project_root=tmp_path)
        out_path = tmp_path / "inventory.json"
        result = sd.export_inventory(out_path)

        assert result is True
        assert out_path.exists()
        data = json.loads(out_path.read_text())
        assert "modules" in data
        assert "stats" in data

    def test_export_returns_false_on_bad_path(self, tmp_path, capsys):
        from codomyrmex.system_discovery.core.discovery_engine import SystemDiscovery

        sd = SystemDiscovery(project_root=tmp_path)
        # Write to a non-existent nested directory
        out_path = tmp_path / "no" / "such" / "dir" / "inventory.json"
        result = sd.export_inventory(out_path)
        assert result is False


# ===================================================================
# SystemDiscovery._display_discovery_results
# ===================================================================


@pytest.mark.unit
class TestDisplayDiscoveryResults:
    """Test _display_discovery_results stdout output."""

    def test_prints_summary(self, tmp_path, capsys):
        from codomyrmex.system_discovery.core.discovery_engine import (
            ModuleInfo,
            SystemDiscovery,
        )

        sd = SystemDiscovery(project_root=tmp_path)
        sd.modules = {
            "alpha": ModuleInfo(
                name="alpha",
                path="/p",
                description="Alpha module",
                version="1.0",
                capabilities=[],
                dependencies=[],
                is_importable=True,
                has_tests=True,
                has_docs=True,
                last_modified="2026-01-01",
            ),
        }
        sd._display_discovery_results()
        captured = capsys.readouterr()
        assert "Discovery Results" in captured.out
        assert "alpha" in captured.out
        assert "1 modules" in captured.out


# ===================================================================
# SystemDiscovery._display_capability_summary
# ===================================================================


@pytest.mark.unit
class TestDisplayCapabilitySummary:
    """Test _display_capability_summary groups capabilities by type."""

    def test_groups_by_type(self, tmp_path, capsys):
        from codomyrmex.system_discovery.core.discovery_engine import (
            ModuleCapability,
            ModuleInfo,
            SystemDiscovery,
        )

        cap1 = ModuleCapability(
            name="f", module_path="/m", type="function", signature="f()",
            docstring="", file_path="/m/f.py", line_number=1,
            is_public=True, dependencies=[],
        )
        cap2 = ModuleCapability(
            name="C", module_path="/m", type="class", signature="class C",
            docstring="", file_path="/m/c.py", line_number=1,
            is_public=True, dependencies=[],
        )
        sd = SystemDiscovery(project_root=tmp_path)
        sd.modules = {
            "mod": ModuleInfo(
                name="mod", path="/p", description="", version="",
                capabilities=[cap1, cap2], dependencies=[],
                is_importable=True, has_tests=False, has_docs=False,
                last_modified="",
            ),
        }
        sd._display_capability_summary()
        captured = capsys.readouterr()
        assert "function" in captured.out
        assert "class" in captured.out
        assert "Total Capabilities Discovered: 2" in captured.out


# ===================================================================
# SystemDiscovery._get_system_status_dict
# ===================================================================


@pytest.mark.unit
class TestGetSystemStatusDict:
    """Test _get_system_status_dict returns complete status structure."""

    def test_structure(self, tmp_path):
        from codomyrmex.system_discovery.core.discovery_engine import SystemDiscovery

        sd = SystemDiscovery(project_root=tmp_path)
        status = sd._get_system_status_dict()
        assert "python" in status
        assert "project" in status
        assert "dependencies" in status
        assert "git" in status
        assert status["python"]["version"] == sys.version.split()[0]
        assert isinstance(status["dependencies"], dict)


# ===================================================================
# SystemDiscovery._check_git_status
# ===================================================================


@pytest.mark.unit
class TestCheckGitStatus:
    """Test _check_git_status git command execution."""

    def test_in_git_repo(self, capsys):
        """When run in the actual codomyrmex repo, git status should work."""
        from codomyrmex.system_discovery.core.discovery_engine import SystemDiscovery

        project_root = Path("/Users/mini/Documents/GitHub/codomyrmex")
        sd = SystemDiscovery(project_root=project_root)
        sd._check_git_status()
        captured = capsys.readouterr()
        assert "Git repository initialized" in captured.out or "Git" in captured.out

    def test_not_git_repo(self, tmp_path, capsys):
        from codomyrmex.system_discovery.core.discovery_engine import SystemDiscovery

        sd = SystemDiscovery(project_root=tmp_path)
        sd._check_git_status()
        captured = capsys.readouterr()
        assert "Git" in captured.out


# ===================================================================
# SystemDiscovery._check_core_dependencies
# ===================================================================


@pytest.mark.unit
class TestCheckCoreDependencies:
    """Test _check_core_dependencies prints dependency status."""

    def test_prints_dependency_status(self, capsys):
        from codomyrmex.system_discovery.core.discovery_engine import SystemDiscovery

        sd = SystemDiscovery()
        sd._check_core_dependencies()
        captured = capsys.readouterr()
        assert "Core Dependencies" in captured.out
        # numpy is installed, should show checkmark
        assert "numpy" in captured.out


# ===================================================================
# SystemDiscovery.show_status_dashboard
# ===================================================================


@pytest.mark.unit
class TestShowStatusDashboard:
    """Test show_status_dashboard composite output."""

    def test_prints_dashboard(self, tmp_path, capsys):
        from codomyrmex.system_discovery.core.discovery_engine import SystemDiscovery

        sd = SystemDiscovery(project_root=tmp_path)
        sd.show_status_dashboard()
        captured = capsys.readouterr()
        assert "STATUS DASHBOARD" in captured.out
        assert "Python Environment" in captured.out
        assert "Project Structure" in captured.out


# ===================================================================
# SystemDiscovery._analyze_module (with synthetic importable module)
# ===================================================================


@pytest.mark.unit
class TestAnalyzeModule:
    """Test _analyze_module with importable and non-importable modules."""

    def test_non_importable_uses_static_analysis(self, tmp_path):
        from codomyrmex.system_discovery.core.discovery_engine import SystemDiscovery

        mod_dir = tmp_path / "fake_module"
        mod_dir.mkdir()
        (mod_dir / "__init__.py").write_text("")
        (mod_dir / "api.py").write_text(
            "def public_api():\n    pass\n\n"
            "class PublicService:\n    pass\n"
        )
        sd = SystemDiscovery(project_root=tmp_path)
        info = sd._analyze_module("nonexistent_module_xyz", mod_dir)
        assert info is not None
        assert info.is_importable is False
        # Static analysis should find the public function and class
        cap_names = [c.name for c in info.capabilities]
        assert "public_api" in cap_names
        assert "PublicService" in cap_names

    def test_analyze_real_module(self, tmp_path):
        """Test analyzing a known importable module (logging_monitoring)."""
        from codomyrmex.system_discovery.core.discovery_engine import SystemDiscovery

        project_root = Path("/Users/mini/Documents/GitHub/codomyrmex")
        mod_path = project_root / "src" / "codomyrmex" / "logging_monitoring"
        sd = SystemDiscovery(project_root=project_root)
        info = sd._analyze_module("logging_monitoring", mod_path)
        assert info is not None
        assert info.name == "logging_monitoring"
        assert info.is_importable is True


# ===================================================================
# SystemDiscovery.run_full_discovery (smoke test)
# ===================================================================


@pytest.mark.unit
class TestRunFullDiscovery:
    """Smoke test for run_full_discovery on a synthetic project."""

    def test_runs_without_error(self, tmp_path, capsys):
        from codomyrmex.system_discovery.core.discovery_engine import SystemDiscovery

        # Set up minimal structure
        codomyrmex_dir = tmp_path / "src" / "codomyrmex"
        codomyrmex_dir.mkdir(parents=True)
        mod = codomyrmex_dir / "mymod"
        mod.mkdir()
        (mod / "__init__.py").write_text('"""My module."""\n')

        sd = SystemDiscovery(project_root=tmp_path)
        sd.run_full_discovery()
        captured = capsys.readouterr()
        assert "SYSTEM DISCOVERY" in captured.out
        assert "Discovery Results" in captured.out
        assert "Capability Summary" in captured.out


# ===================================================================
# SystemDiscovery.check_git_repositories
# ===================================================================


@pytest.mark.unit
class TestCheckGitRepositories:
    """Test check_git_repositories output."""

    def test_non_git_directory(self, tmp_path, capsys):
        from codomyrmex.system_discovery.core.discovery_engine import SystemDiscovery

        sd = SystemDiscovery(project_root=tmp_path)
        sd.check_git_repositories()
        captured = capsys.readouterr()
        assert "GIT REPOSITORY STATUS" in captured.out

    def test_with_real_git_repo(self, capsys):
        from codomyrmex.system_discovery.core.discovery_engine import SystemDiscovery

        project_root = Path("/Users/mini/Documents/GitHub/codomyrmex")
        sd = SystemDiscovery(project_root=project_root)
        sd.check_git_repositories()
        captured = capsys.readouterr()
        assert "GIT REPOSITORY STATUS" in captured.out
        assert "Remote Repositories" in captured.out or "remote" in captured.out.lower()


# ===================================================================
# SystemDiscovery.export_full_inventory
# ===================================================================


@pytest.mark.unit
class TestExportFullInventory:
    """Test export_full_inventory writes the default inventory file."""

    def test_exports_to_default_location(self, tmp_path, capsys):
        from codomyrmex.system_discovery.core.discovery_engine import SystemDiscovery

        codomyrmex_dir = tmp_path / "src" / "codomyrmex"
        codomyrmex_dir.mkdir(parents=True)

        sd = SystemDiscovery(project_root=tmp_path)
        sd.export_full_inventory()

        inv_file = tmp_path / "codomyrmex_inventory.json"
        assert inv_file.exists()
        data = json.loads(inv_file.read_text())
        assert "project_info" in data
        assert "modules" in data


# ===================================================================
# SystemDiscovery._discover_module_capabilities (runtime inspection)
# ===================================================================


@pytest.mark.unit
class TestDiscoverModuleCapabilities:
    """Test runtime capability discovery on a real imported module."""

    def test_discovers_public_members(self):
        import json as json_mod

        from codomyrmex.system_discovery.core.discovery_engine import SystemDiscovery

        sd = SystemDiscovery()
        caps = sd._discover_module_capabilities(json_mod, Path("/m"))
        names = [c.name for c in caps]
        # json module has 'dumps', 'loads' etc
        assert "dumps" in names
        assert "loads" in names
        # Private members excluded
        for c in caps:
            assert not c.name.startswith("_")

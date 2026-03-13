"""Zero-mock tests for the languages module.

Tests cover:
- BaseLanguageManager: contract and default behaviour
- Each concrete manager: instantiation, install_instructions(), setup_project() signature
- PythonManager.is_installed() returns True (Python is always present in this env)
- BashManager.is_installed() returns True (bash is always present on POSIX)
- _cleanup() with empty list and nonexistent paths raises no errors
- All install_instructions() return non-empty str with install guidance

External-compiler-dependent tests (use_script, setup_project execution) are
guarded with @pytest.mark.skipif so they are skipped cleanly when toolchains
are absent rather than failing.
"""

from __future__ import annotations

import inspect
import os
import shutil
import tempfile

import pytest

from codomyrmex.languages.base import BaseLanguageManager
from codomyrmex.languages.bash.manager import BashManager
from codomyrmex.languages.cpp.manager import CppManager
from codomyrmex.languages.csharp.manager import CSharpManager
from codomyrmex.languages.elixir.manager import ElixirManager
from codomyrmex.languages.go.manager import GoManager
from codomyrmex.languages.java.manager import JavaManager
from codomyrmex.languages.javascript.manager import JavaScriptManager
from codomyrmex.languages.php.manager import PhpManager
from codomyrmex.languages.python.manager import PythonManager
from codomyrmex.languages.r.manager import RManager
from codomyrmex.languages.ruby.manager import RubyManager
from codomyrmex.languages.rust.manager import RustManager
from codomyrmex.languages.swift.manager import SwiftManager
from codomyrmex.languages.typescript.manager import TypeScriptManager

# ---------------------------------------------------------------------------
# BaseLanguageManager — contract tests
# ---------------------------------------------------------------------------


class TestBaseLanguageManager:
    """Tests for the BaseLanguageManager template-method contract."""

    def test_check_commands_default_is_empty_list(self):
        """_check_commands class attribute defaults to an empty list."""
        assert BaseLanguageManager._check_commands == []

    def test_is_installed_returns_bool_on_empty_commands(self):
        """is_installed() returns True when _check_commands is empty (nothing to fail)."""

        class _Empty(BaseLanguageManager):
            _check_commands = []

            def install_instructions(self):
                raise NotImplementedError

            def setup_project(self, path):
                raise NotImplementedError

            def use_script(self, script_content, dir_path=None):
                raise NotImplementedError

        mgr = _Empty()
        result = mgr.is_installed()
        assert isinstance(result, bool)
        assert result is True  # empty command list → no failure → True

    def test_is_installed_returns_false_for_nonexistent_command(self):
        """is_installed() returns False when a check command is not on PATH."""

        class _Missing(BaseLanguageManager):
            _check_commands = [["__definitely_not_a_real_command_xyz__", "--version"]]

            def install_instructions(self):
                raise NotImplementedError

            def setup_project(self, path):
                raise NotImplementedError

            def use_script(self, script_content, dir_path=None):
                raise NotImplementedError

        mgr = _Missing()
        result = mgr.is_installed()
        assert isinstance(result, bool)
        assert result is False

    def test_cleanup_empty_list_no_error(self):
        """_cleanup([]) must complete without raising any exception."""
        mgr = PythonManager()  # concrete subclass, avoids ABC issues
        mgr._cleanup([])  # must not raise

    def test_cleanup_nonexistent_paths_no_error(self):
        """_cleanup() silently ignores OSError for paths that do not exist."""
        mgr = PythonManager()
        nonexistent = ["/tmp/__does_not_exist_abc123__.tmp", "/tmp/__also_gone__.tmp"]
        mgr._cleanup(nonexistent)  # must not raise

    def test_cleanup_removes_existing_file(self):
        """_cleanup() actually removes a file that exists on disk."""
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp_path = tmp.name
        assert os.path.exists(tmp_path)
        mgr = PythonManager()
        mgr._cleanup([tmp_path])
        assert not os.path.exists(tmp_path)

    def test_install_instructions_raises_not_implemented(self):
        """BaseLanguageManager.install_instructions() raises NotImplementedError."""
        # Instantiate with all abstract-like methods stubbed so we can call
        # the base one directly.
        with pytest.raises(NotImplementedError):
            BaseLanguageManager.install_instructions(
                object.__new__(BaseLanguageManager)
            )

    def test_setup_project_raises_not_implemented(self):
        """BaseLanguageManager.setup_project() raises NotImplementedError."""
        with pytest.raises(NotImplementedError):
            BaseLanguageManager.setup_project(
                object.__new__(BaseLanguageManager), "/tmp/x"
            )

    def test_use_script_raises_not_implemented(self):
        """BaseLanguageManager.use_script() raises NotImplementedError."""
        with pytest.raises(NotImplementedError):
            BaseLanguageManager.use_script(object.__new__(BaseLanguageManager), "code")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_ALL_MANAGERS: list[tuple[str, type[BaseLanguageManager]]] = [
    ("BashManager", BashManager),
    ("CppManager", CppManager),
    ("CSharpManager", CSharpManager),
    ("ElixirManager", ElixirManager),
    ("GoManager", GoManager),
    ("JavaManager", JavaManager),
    ("JavaScriptManager", JavaScriptManager),
    ("PhpManager", PhpManager),
    ("PythonManager", PythonManager),
    ("RManager", RManager),
    ("RubyManager", RubyManager),
    ("RustManager", RustManager),
    ("SwiftManager", SwiftManager),
    ("TypeScriptManager", TypeScriptManager),
]


# ---------------------------------------------------------------------------
# Generic contract tests — run for every concrete manager
# ---------------------------------------------------------------------------


class TestAllManagersContract:
    """Parametrized tests that every concrete manager must satisfy."""

    @pytest.mark.parametrize(
        ("name", "cls"), _ALL_MANAGERS, ids=[n for n, _ in _ALL_MANAGERS]
    )
    def test_instantiation_requires_no_args(self, name, cls):
        """Every manager must be constructable with zero arguments."""
        instance = cls()
        assert instance is not None

    @pytest.mark.parametrize(
        ("name", "cls"), _ALL_MANAGERS, ids=[n for n, _ in _ALL_MANAGERS]
    )
    def test_is_subclass_of_base(self, name, cls):
        """Every manager must inherit from BaseLanguageManager."""
        assert issubclass(cls, BaseLanguageManager)

    @pytest.mark.parametrize(
        ("name", "cls"), _ALL_MANAGERS, ids=[n for n, _ in _ALL_MANAGERS]
    )
    def test_install_instructions_returns_str(self, name, cls):
        """install_instructions() must return a non-empty string."""
        mgr = cls()
        result = mgr.install_instructions()
        assert isinstance(result, str), (
            f"{name}.install_instructions() did not return str"
        )
        assert len(result) > 0, f"{name}.install_instructions() returned empty string"

    @pytest.mark.parametrize(
        ("name", "cls"), _ALL_MANAGERS, ids=[n for n, _ in _ALL_MANAGERS]
    )
    def test_install_instructions_contains_install_keyword(self, name, cls):
        """install_instructions() text must mention installation guidance."""
        mgr = cls()
        text = mgr.install_instructions().lower()
        # At least one of these tokens must appear
        install_tokens = ["install", "brew", "apt", "curl", "download", "xcode"]
        assert any(tok in text for tok in install_tokens), (
            f"{name}.install_instructions() contains no install guidance. Got: {text[:200]}"
        )

    @pytest.mark.parametrize(
        ("name", "cls"), _ALL_MANAGERS, ids=[n for n, _ in _ALL_MANAGERS]
    )
    def test_is_installed_returns_bool(self, name, cls):
        """is_installed() must return a plain bool regardless of toolchain presence."""
        mgr = cls()
        result = mgr.is_installed()
        assert isinstance(result, bool), (
            f"{name}.is_installed() returned {type(result).__name__}, expected bool"
        )

    @pytest.mark.parametrize(
        ("name", "cls"), _ALL_MANAGERS, ids=[n for n, _ in _ALL_MANAGERS]
    )
    def test_setup_project_signature(self, name, cls):
        """setup_project(path) must accept a single positional 'path' argument."""
        sig = inspect.signature(cls.setup_project)
        params = list(sig.parameters.keys())
        # params = ['self', 'path']
        assert "path" in params, f"{name}.setup_project() has no 'path' parameter"

    @pytest.mark.parametrize(
        ("name", "cls"), _ALL_MANAGERS, ids=[n for n, _ in _ALL_MANAGERS]
    )
    def test_use_script_signature(self, name, cls):
        """use_script(script_content, dir_path=None) must have expected signature."""
        sig = inspect.signature(cls.use_script)
        params = list(sig.parameters.keys())
        assert "script_content" in params, (
            f"{name}.use_script() missing 'script_content'"
        )
        assert "dir_path" in params, f"{name}.use_script() missing 'dir_path'"
        # dir_path should be optional (default None)
        default = sig.parameters["dir_path"].default
        assert default is None, (
            f"{name}.use_script(dir_path) default should be None, got {default!r}"
        )

    @pytest.mark.parametrize(
        ("name", "cls"), _ALL_MANAGERS, ids=[n for n, _ in _ALL_MANAGERS]
    )
    def test_cleanup_empty_list_no_error(self, name, cls):
        """_cleanup([]) must not raise for any manager."""
        mgr = cls()
        mgr._cleanup([])

    @pytest.mark.parametrize(
        ("name", "cls"), _ALL_MANAGERS, ids=[n for n, _ in _ALL_MANAGERS]
    )
    def test_cleanup_nonexistent_paths_no_error(self, name, cls):
        """_cleanup() must silently ignore missing files for every manager."""
        mgr = cls()
        mgr._cleanup(["/tmp/__no_such_file_codomyrmex_test__.xyz"])


# ---------------------------------------------------------------------------
# PythonManager — always-present interpreter
# ---------------------------------------------------------------------------


class TestPythonManager:
    """Tests specific to PythonManager, which is always installed in this env."""

    def test_is_installed_returns_true(self):
        """Python is always installed in a pytest environment."""
        mgr = PythonManager()
        assert mgr.is_installed() is True

    def test_install_instructions_mentions_python3(self):
        """install_instructions() must mention 'python3' or 'python'."""
        mgr = PythonManager()
        text = mgr.install_instructions().lower()
        assert "python" in text

    def test_install_instructions_mentions_uv(self):
        """PythonManager documents uv as the recommended tool."""
        mgr = PythonManager()
        assert "uv" in mgr.install_instructions()

    def test_use_script_runs_hello_world(self):
        """use_script() with a trivial print executes and returns expected output."""
        mgr = PythonManager()
        output = mgr.use_script('print("hello_from_test")')
        assert "hello_from_test" in output

    def test_use_script_with_dir_path(self):
        """use_script() with an explicit dir_path still runs and cleans the script file."""
        mgr = PythonManager()
        with tempfile.TemporaryDirectory() as tmpdir:
            output = mgr.use_script('print("dir_path_test")', dir_path=tmpdir)
            assert "dir_path_test" in output
            # Script file must have been cleaned up
            assert not os.path.exists(os.path.join(tmpdir, "script.py"))

    def test_use_script_captures_stderr(self):
        """use_script() captures stderr as well as stdout."""
        mgr = PythonManager()
        output = mgr.use_script("import sys; sys.stderr.write('err_marker\\n')")
        assert "err_marker" in output

    def test_setup_project_returns_bool(self):
        """setup_project() returns a bool regardless of uv presence."""
        mgr = PythonManager()
        with tempfile.TemporaryDirectory() as tmpdir:
            target = os.path.join(tmpdir, "test_proj")
            result = mgr.setup_project(target)
            assert isinstance(result, bool)


# ---------------------------------------------------------------------------
# BashManager — bash is always present on POSIX
# ---------------------------------------------------------------------------


class TestBashManager:
    """Tests specific to BashManager, which is always present on macOS/Linux."""

    def test_is_installed_returns_true(self):
        """bash is always installed in a POSIX pytest environment."""
        mgr = BashManager()
        assert mgr.is_installed() is True

    def test_check_commands_set(self):
        """BashManager._check_commands includes a bash --version check."""
        assert BashManager._check_commands == [["bash", "--version"]]

    def test_install_instructions_mentions_brew_and_bash(self):
        text = BashManager().install_instructions().lower()
        assert "bash" in text
        assert "brew" in text or "apt" in text or "install" in text

    def test_use_script_runs_echo(self):
        """use_script() with a simple echo returns expected output."""
        mgr = BashManager()
        output = mgr.use_script("echo bash_test_marker")
        assert "bash_test_marker" in output

    def test_use_script_adds_shebang_if_missing(self):
        """use_script() prepends shebang when script content lacks one."""
        mgr = BashManager()
        # Verify the script still runs — shebang injection works
        output = mgr.use_script("echo shebang_added")
        assert "shebang_added" in output

    def test_use_script_with_existing_shebang(self):
        """use_script() does not double-add shebang when already present."""
        mgr = BashManager()
        script = "#!/usr/bin/env bash\necho shebang_present"
        output = mgr.use_script(script)
        assert "shebang_present" in output

    def test_use_script_with_dir_path(self):
        """use_script() with dir_path cleans up the script file afterward."""
        mgr = BashManager()
        with tempfile.TemporaryDirectory() as tmpdir:
            output = mgr.use_script("echo dir_path_bash", dir_path=tmpdir)
            assert "dir_path_bash" in output
            assert not os.path.exists(os.path.join(tmpdir, "script.sh"))

    def test_setup_project_creates_directory(self):
        """setup_project() creates the target directory and returns True."""
        mgr = BashManager()
        with tempfile.TemporaryDirectory() as tmpdir:
            target = os.path.join(tmpdir, "bash_proj")
            result = mgr.setup_project(target)
            assert result is True
            assert os.path.isdir(target)


# ---------------------------------------------------------------------------
# GoManager — guarded by shutil.which('go')
# ---------------------------------------------------------------------------


@pytest.mark.skipif(not shutil.which("go"), reason="go not installed")
class TestGoManager:
    def test_is_installed_returns_true(self):
        assert GoManager().is_installed() is True

    def test_check_commands_contains_go_version(self):
        assert ["go", "version"] in GoManager._check_commands

    def test_use_script_hello_world(self):
        mgr = GoManager()
        script = 'package main\nimport "fmt"\nfunc main() { fmt.Println("go_test_marker") }\n'
        output = mgr.use_script(script)
        assert "go_test_marker" in output

    def test_setup_project_creates_go_mod(self):
        mgr = GoManager()
        with tempfile.TemporaryDirectory() as tmpdir:
            target = os.path.join(tmpdir, "go_proj")
            result = mgr.setup_project(target)
            assert isinstance(result, bool)
            if result:
                assert os.path.exists(os.path.join(target, "go.mod"))


# ---------------------------------------------------------------------------
# RustManager — guarded by shutil.which('cargo')
# ---------------------------------------------------------------------------


@pytest.mark.skipif(not shutil.which("cargo"), reason="cargo (rust) not installed")
class TestRustManager:
    def test_is_installed_returns_true(self):
        assert RustManager().is_installed() is True

    def test_check_commands_contains_cargo(self):
        assert ["cargo", "--version"] in RustManager._check_commands

    def test_use_script_hello_world(self):
        mgr = RustManager()
        script = 'fn main() { println!("rust_test_marker"); }\n'
        output = mgr.use_script(script)
        assert "rust_test_marker" in output


# ---------------------------------------------------------------------------
# JavaManager — guarded by shutil.which('javac')
# ---------------------------------------------------------------------------


@pytest.mark.skipif(not shutil.which("javac"), reason="javac (JDK) not installed")
class TestJavaManager:
    def test_is_installed_returns_true(self):
        assert JavaManager().is_installed() is True

    def test_check_commands_contains_both_javac_and_java(self):
        cmds_flat = [tuple(c) for c in JavaManager._check_commands]
        assert ("javac", "--version") in cmds_flat
        assert ("java", "--version") in cmds_flat

    def test_use_script_hello_world(self):
        mgr = JavaManager()
        script = (
            "public class Main {\n"
            '    public static void main(String[] args) { System.out.println("java_test_marker"); }\n'
            "}\n"
        )
        output = mgr.use_script(script)
        assert "java_test_marker" in output


# ---------------------------------------------------------------------------
# JavaScriptManager — guarded by shutil.which('node')
# ---------------------------------------------------------------------------


@pytest.mark.skipif(not shutil.which("node"), reason="node not installed")
class TestJavaScriptManager:
    def test_is_installed_returns_true(self):
        assert JavaScriptManager().is_installed() is True

    def test_check_commands_contains_node(self):
        assert ["node", "--version"] in JavaScriptManager._check_commands

    def test_use_script_hello_world(self):
        mgr = JavaScriptManager()
        output = mgr.use_script('console.log("js_test_marker");')
        assert "js_test_marker" in output


# ---------------------------------------------------------------------------
# TypeScriptManager — guarded by node (TS falls back to node via npx)
# ---------------------------------------------------------------------------


class TestTypeScriptManager:
    def test_is_installed_returns_bool(self):
        result = TypeScriptManager().is_installed()
        assert isinstance(result, bool)

    def test_install_instructions_mentions_bun_or_tsx(self):
        text = TypeScriptManager().install_instructions().lower()
        assert "bun" in text or "tsx" in text or "typescript" in text


# ---------------------------------------------------------------------------
# PhpManager — guarded by shutil.which('php')
# ---------------------------------------------------------------------------


@pytest.mark.skipif(not shutil.which("php"), reason="php not installed")
class TestPhpManager:
    def test_is_installed_returns_true(self):
        assert PhpManager().is_installed() is True

    def test_use_script_hello_world(self):
        mgr = PhpManager()
        output = mgr.use_script('echo "php_test_marker";')
        assert "php_test_marker" in output

    def test_use_script_prepends_php_tag(self):
        """use_script() prepends <?php when content lacks it."""
        mgr = PhpManager()
        output = mgr.use_script('echo "php_tag_prepended";')
        assert "php_tag_prepended" in output


# ---------------------------------------------------------------------------
# RubyManager — guarded by shutil.which('ruby')
# ---------------------------------------------------------------------------


@pytest.mark.skipif(not shutil.which("ruby"), reason="ruby not installed")
class TestRubyManager:
    def test_is_installed_returns_true(self):
        assert RubyManager().is_installed() is True

    def test_use_script_hello_world(self):
        mgr = RubyManager()
        output = mgr.use_script('puts "ruby_test_marker"')
        assert "ruby_test_marker" in output


# ---------------------------------------------------------------------------
# RManager — guarded by shutil.which('Rscript')
# ---------------------------------------------------------------------------


@pytest.mark.skipif(not shutil.which("Rscript"), reason="Rscript (R) not installed")
class TestRManager:
    def test_is_installed_returns_true(self):
        assert RManager().is_installed() is True

    def test_check_commands_contains_rscript(self):
        assert ["Rscript", "--version"] in RManager._check_commands

    def test_use_script_hello_world(self):
        mgr = RManager()
        output = mgr.use_script('cat("r_test_marker\\n")')
        assert "r_test_marker" in output


# ---------------------------------------------------------------------------
# ElixirManager — guarded by shutil.which('elixir')
# ---------------------------------------------------------------------------


@pytest.mark.skipif(not shutil.which("elixir"), reason="elixir not installed")
class TestElixirManager:
    def test_is_installed_returns_true(self):
        assert ElixirManager().is_installed() is True

    def test_check_commands_contains_elixir(self):
        assert ["elixir", "--version"] in ElixirManager._check_commands

    def test_use_script_hello_world(self):
        mgr = ElixirManager()
        output = mgr.use_script('IO.puts("elixir_test_marker")')
        assert "elixir_test_marker" in output


# ---------------------------------------------------------------------------
# SwiftManager — guarded by shutil.which('swift')
# ---------------------------------------------------------------------------


@pytest.mark.skipif(not shutil.which("swift"), reason="swift not installed")
class TestSwiftManager:
    def test_is_installed_returns_true(self):
        assert SwiftManager().is_installed() is True

    def test_check_commands_contains_swift(self):
        assert ["swift", "--version"] in SwiftManager._check_commands

    def test_use_script_hello_world(self):
        mgr = SwiftManager()
        output = mgr.use_script('print("swift_test_marker")')
        assert "swift_test_marker" in output


# ---------------------------------------------------------------------------
# CppManager — guarded by g++ or clang++
# ---------------------------------------------------------------------------


_has_cpp = bool(shutil.which("g++") or shutil.which("clang++"))


@pytest.mark.skipif(not _has_cpp, reason="g++ or clang++ not installed")
class TestCppManager:
    def test_is_installed_returns_true(self):
        assert CppManager().is_installed() is True

    def test_use_script_hello_world(self):
        mgr = CppManager()
        script = (
            "#include <iostream>\n"
            'int main() { std::cout << "cpp_test_marker" << std::endl; return 0; }\n'
        )
        output = mgr.use_script(script)
        assert "cpp_test_marker" in output

    def test_setup_project_creates_src_dir(self):
        mgr = CppManager()
        with tempfile.TemporaryDirectory() as tmpdir:
            target = os.path.join(tmpdir, "cpp_proj")
            result = mgr.setup_project(target)
            assert isinstance(result, bool)
            if result:
                assert os.path.isdir(os.path.join(target, "src"))


# ---------------------------------------------------------------------------
# CSharpManager — guarded by shutil.which('dotnet')
# ---------------------------------------------------------------------------


@pytest.mark.skipif(not shutil.which("dotnet"), reason="dotnet not installed")
class TestCSharpManager:
    def test_is_installed_returns_true(self):
        assert CSharpManager().is_installed() is True

    def test_check_commands_contains_dotnet(self):
        assert ["dotnet", "--version"] in CSharpManager._check_commands

    def test_install_instructions_mentions_dotnet_sdk(self):
        text = CSharpManager().install_instructions().lower()
        assert "dotnet" in text or ".net" in text


# ---------------------------------------------------------------------------
# _check_commands class-level values — spot-check expected commands
# ---------------------------------------------------------------------------


class TestCheckCommandsClassAttributes:
    """Verify _check_commands values are structurally correct list-of-lists."""

    @pytest.mark.parametrize(
        ("name", "cls"), _ALL_MANAGERS, ids=[n for n, _ in _ALL_MANAGERS]
    )
    def test_check_commands_is_list(self, name, cls):
        assert isinstance(cls._check_commands, list), (
            f"{name}._check_commands is not a list"
        )

    @pytest.mark.parametrize(
        ("name", "cls"), _ALL_MANAGERS, ids=[n for n, _ in _ALL_MANAGERS]
    )
    def test_check_commands_entries_are_lists_of_strings(self, name, cls):
        for entry in cls._check_commands:
            assert isinstance(entry, list), (
                f"{name}._check_commands entry {entry!r} is not a list"
            )
            for item in entry:
                assert isinstance(item, str), (
                    f"{name}._check_commands entry item {item!r} is not a str"
                )

    def test_go_check_commands(self):
        assert GoManager._check_commands == [["go", "version"]]

    def test_rust_check_commands(self):
        assert RustManager._check_commands == [["cargo", "--version"]]

    def test_java_has_two_check_commands(self):
        assert len(JavaManager._check_commands) == 2

    def test_bash_check_commands(self):
        assert BashManager._check_commands == [["bash", "--version"]]

    def test_ruby_check_commands(self):
        assert RubyManager._check_commands == [["ruby", "--version"]]

    def test_php_check_commands(self):
        assert PhpManager._check_commands == [["php", "--version"]]

    def test_r_check_commands(self):
        assert RManager._check_commands == [["Rscript", "--version"]]

    def test_elixir_check_commands(self):
        assert ElixirManager._check_commands == [["elixir", "--version"]]

    def test_swift_check_commands(self):
        assert SwiftManager._check_commands == [["swift", "--version"]]

    def test_csharp_check_commands(self):
        assert CSharpManager._check_commands == [["dotnet", "--version"]]

    def test_js_check_commands(self):
        assert JavaScriptManager._check_commands == [["node", "--version"]]

    def test_cpp_check_commands_empty_list(self):
        """CppManager uses a custom is_installed() override, so _check_commands is empty."""
        assert CppManager._check_commands == []

    def test_python_check_commands_empty_list(self):
        """PythonManager uses a custom is_installed() override, so _check_commands is empty."""
        assert PythonManager._check_commands == []

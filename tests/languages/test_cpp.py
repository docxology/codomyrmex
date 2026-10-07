import sys

import pytest

from codomyrmex.languages.cpp.manager import CppManager


def test_cpp_manager_operations():
    """Test C++ manager functions."""
    manager = CppManager()

    is_installed = manager.is_installed()
    assert isinstance(is_installed, bool)

    instructions = manager.install_instructions()
    assert isinstance(instructions, str)

    if is_installed:
        script = '#include <iostream>\n\nint main() {\n    std::cout << "Hello from C++ zero-mock test" << std::endl;\n    return 0;\n}\n'
        result = manager.use_script(script)
        assert "Hello from C++ zero-mock test" in result


@pytest.mark.skipif(sys.platform == "win32", reason="uses a POSIX shell script")
def test_broken_compiler_is_reported_not_raised(tmp_path, monkeypatch):
    """A compiler that exits non-zero counts as missing.

    Regression: is_installed() only caught FileNotFoundError, so a g++ shim
    that fails (macOS without the Command Line Tools) or a slow first probe
    escaped as CalledProcessError / TimeoutExpired.
    """
    fake = tmp_path / "g++"
    fake.write_text("#!/bin/sh\nexit 1\n", encoding="utf-8")
    fake.chmod(0o755)
    monkeypatch.setenv("PATH", str(tmp_path))  # no clang++ either

    manager = CppManager()
    assert manager.is_installed() is False
    assert manager.use_script("int main() { return 0; }") == (
        "Error: Neither g++ nor clang++ found."
    )
